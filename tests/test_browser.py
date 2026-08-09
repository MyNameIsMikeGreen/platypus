from playwright.sync_api import expect, sync_playwright


def test_category_toggles_show_and_hide_categories(live_url):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(live_url)
            toggles = page.locator("[data-category-toggle]")
            cards = page.locator(".category-card[data-category]")
            toggle_count = toggles.count()

            assert toggle_count >= 2
            assert cards.count() == toggle_count
            for index in range(toggle_count):
                expect(toggles.nth(index)).to_be_checked()
                expect(cards.nth(index)).to_be_visible()
            expect(page.locator("[data-category-status]")).to_have_text(
                f"Showing {toggle_count} of {toggle_count} categories"
            )

            toggles.first.uncheck()
            expect(cards.first).to_be_hidden()
            expect(cards.nth(1)).to_be_visible()

            for index in range(1, toggle_count):
                toggles.nth(index).uncheck()
            expect(page.locator("[data-category-empty]")).to_be_visible()
            expect(page.locator("[data-category-status]")).to_have_text(
                f"Showing 0 of {toggle_count} categories"
            )

            toggles.first.check()
            expect(cards.first).to_be_visible()
            expect(page.locator("[data-category-empty]")).to_be_hidden()
        finally:
            browser.close()


def test_search_autocomplete_filters_navigates_and_stays_local(live_url):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        requests = []
        page.on("request", lambda request: requests.append(request.url))
        try:
            page.goto(live_url)
            options = page.locator("[data-search-option]")
            recipes = options.evaluate_all(
                """options => options.map(option => ({
                    category: option.dataset.category,
                    title: option.value,
                    url: option.dataset.url
                }))"""
            )
            titles = [recipe["title"] for recipe in recipes]
            query = titles[0][:4].casefold()
            expected = [title for title in titles if query in title.casefold()][:8]
            input_field = page.locator("#recipe-search")
            suggestions = page.locator("[role='option'] a")

            input_field.fill(query)
            expect(suggestions).to_have_count(len(expected))
            assert suggestions.all_inner_texts() == expected
            expect(page.locator("#recipe-suggestions")).to_be_visible()
            assert all(url.startswith(live_url) for url in requests)

            input_field.press("Escape")
            expect(page.locator("#recipe-suggestions")).to_be_hidden()

            input_field.fill("a search term that cannot exist")
            expect(page.locator("#recipe-suggestions")).to_be_hidden()
            expect(page.locator("[data-search-status]")).to_have_text("No recipe suggestions")

            scoped_search = None
            for recipe in recipes:
                for word in recipe["title"].casefold().split():
                    candidate = word[:2]
                    global_matches = [
                        item for item in recipes if candidate in item["title"].casefold()
                    ]
                    scoped_matches = [
                        item for item in global_matches if item["category"] == recipe["category"]
                    ][:8]
                    if scoped_matches and any(
                        item["category"] != recipe["category"] for item in global_matches
                    ):
                        scoped_search = (recipe["category"], candidate, scoped_matches)
                        break
                if scoped_search:
                    break

            assert scoped_search is not None
            selected_category, query, expected_recipes = scoped_search
            page.locator("[data-search-category]").select_option(selected_category)
            input_field.fill(query)
            assert suggestions.all_inner_texts() == [recipe["title"] for recipe in expected_recipes]
            assert page.locator("[role='option']").evaluate_all(
                """(options, selectedCategory) =>
                    options.every(option => option.dataset.category === selectedCategory)""",
                selected_category,
            )
            input_field.press("ArrowDown")
            expect(page.locator("[role='option']").first).to_have_attribute("aria-selected", "true")
            first_url = expected_recipes[0]["url"]
            input_field.press("Enter")
            page.wait_for_url(f"**{first_url}")
            expect(page.locator("h1")).to_have_text(expected_recipes[0]["title"])
        finally:
            browser.close()


def test_phone_and_desktop_layouts_are_responsive(live_url):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            phone = browser.new_page(viewport={"width": 390, "height": 844})
            phone.goto(live_url)

            assert phone.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
            for selector in ["nav a", "button", ".category-toggle", ".recipe-list a"]:
                assert phone.locator(selector).first.bounding_box()["height"] >= 44
            assert (
                int(
                    phone.locator("#recipe-search").evaluate(
                        "el => parseFloat(getComputedStyle(el).fontSize)"
                    )
                )
                >= 16
            )

            phone_cards = phone.locator(".category-card[data-category]")
            first_phone_card = phone_cards.nth(0).bounding_box()
            second_phone_card = phone_cards.nth(1).bounding_box()
            assert first_phone_card["x"] == second_phone_card["x"]
            assert second_phone_card["y"] > first_phone_card["y"]

            recipe_url = phone.locator(".recipe-list a").first.get_attribute("href")
            phone.goto(f"{live_url}{recipe_url}", wait_until="domcontentloaded")
            ingredients = phone.locator(".ingredients").bounding_box()
            method = phone.locator(".method").bounding_box()
            assert ingredients["x"] == method["x"]
            assert method["y"] > ingredients["y"]
            assert phone.evaluate("document.documentElement.scrollWidth <= window.innerWidth")

            desktop = browser.new_page(viewport={"width": 1280, "height": 900})
            desktop.goto(live_url)
            desktop_cards = desktop.locator(".category-card[data-category]")
            first_desktop_card = desktop_cards.nth(0).bounding_box()
            second_desktop_card = desktop_cards.nth(1).bounding_box()
            assert second_desktop_card["x"] > first_desktop_card["x"]
            assert second_desktop_card["y"] == first_desktop_card["y"]

            desktop.goto(f"{live_url}{recipe_url}", wait_until="domcontentloaded")
            ingredients = desktop.locator(".ingredients").bounding_box()
            method = desktop.locator(".method").bounding_box()
            assert method["x"] > ingredients["x"]
            assert method["y"] == ingredients["y"]
        finally:
            browser.close()
