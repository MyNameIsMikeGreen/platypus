from playwright.sync_api import expect, sync_playwright


def test_category_toggles_show_and_hide_categories(live_url):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(live_url)
            page.locator("[data-filter-drawer] summary").click()
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
            phone.locator("[data-filter-drawer] summary").click()
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


def test_time_sliders_narrow_recipes_without_navigating(live_url):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(live_url)
            starting_url = page.url
            page.locator("[data-filter-drawer] summary").click()

            items = page.locator("[data-recipe-item]")
            visible_items = page.locator("[data-recipe-item]:not([hidden])")
            total_slider = page.locator("[data-total-time-slider]")
            active_slider = page.locator("[data-active-time-slider]")
            total_output = page.locator("[data-total-time-value]")
            active_output = page.locator("[data-active-time-value]")

            total_count = items.count()
            assert total_count > 0
            expect(visible_items).to_have_count(total_count)
            expect(total_output).to_have_text("Any duration")
            expect(active_output).to_have_text("Any duration")

            # Drag the total time slider down to its minimum step (15 minutes or less).
            total_slider.evaluate(
                "el => { el.value = 0; el.dispatchEvent(new Event('input', { bubbles: true })); }"
            )
            expect(total_output).to_have_text("15 min or less")
            filtered_count = visible_items.count()
            assert 0 < filtered_count < total_count
            remaining_totals = visible_items.evaluate_all(
                "items => items.map(item => Number(item.dataset.totalMinutes))"
            )
            assert all(minutes <= 15 for minutes in remaining_totals)
            assert page.url == starting_url

            # Restore total time, then narrow using the active time slider instead.
            total_slider.evaluate(
                "el => { el.value = el.max; el.dispatchEvent(new Event('input', { bubbles: true })); }"
            )
            expect(visible_items).to_have_count(total_count)

            active_slider.evaluate(
                "el => { el.value = 1; el.dispatchEvent(new Event('input', { bubbles: true })); }"
            )
            expect(active_output).to_have_text("15 min or less")
            active_filtered_count = visible_items.count()
            assert 0 < active_filtered_count < total_count
            remaining_actives = visible_items.evaluate_all(
                "items => items.map(item => Number(item.dataset.activeMinutes))"
            )
            assert all(minutes <= 15 for minutes in remaining_actives)
            assert page.url == starting_url

            active_slider.evaluate(
                "el => { el.value = el.max; el.dispatchEvent(new Event('input', { bubbles: true })); }"
            )
            expect(visible_items).to_have_count(total_count)

            # Narrowing to a single category whose recipes all exceed the time
            # budget should surface the dedicated time empty-state, distinct
            # from the category empty-state.
            toggles = page.locator("[data-category-toggle]")
            for index in range(toggles.count()):
                toggle = toggles.nth(index)
                if toggle.get_attribute("value") != "MAINS" and toggle.is_checked():
                    toggle.uncheck()
            mains_toggle = page.locator("[data-category-toggle][value='MAINS']")
            expect(mains_toggle).to_be_checked()

            total_slider.evaluate(
                "el => { el.value = 0; el.dispatchEvent(new Event('input', { bubbles: true })); }"
            )
            expect(page.locator("[data-time-empty]")).to_be_visible()
            expect(page.locator("[data-category-empty]")).to_be_hidden()
            expect(page.locator('.category-card[data-category="MAINS"]')).to_be_hidden()

            total_slider.evaluate(
                "el => { el.value = el.max; el.dispatchEvent(new Event('input', { bubbles: true })); }"
            )
            expect(page.locator("[data-time-empty]")).to_be_hidden()
            expect(page.locator('.category-card[data-category="MAINS"]')).to_be_visible()
            assert page.url == starting_url
        finally:
            browser.close()

