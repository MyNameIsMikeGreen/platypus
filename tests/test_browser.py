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


def test_tag_toggles_are_all_enabled_by_default_and_filter_recipes(live_url):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(live_url)
            page.locator("[data-filter-drawer] summary").click()

            tag_toggles = page.locator("[data-tag-toggle]")
            items = page.locator("[data-recipe-item]")
            tag_count = tag_toggles.count()
            item_count = items.count()

            assert tag_count >= 1
            for index in range(tag_count):
                expect(tag_toggles.nth(index)).to_be_checked()
            expect(page.locator("[data-tag-status]")).to_have_text(
                f"Showing {tag_count} of {tag_count} tags"
            )
            expect(page.locator("[data-recipe-item]:not([hidden])")).to_have_count(item_count)

            item_tags = items.evaluate_all("items => items.map(item => item.dataset.tags)")
            target_tag = tag_toggles.first.get_attribute("value")
            # Recipes whose only tag is the one being disabled must disappear;
            # recipes with additional enabled tags, or no tags at all, must remain.
            expected_hidden = {
                index
                for index, tags in enumerate(item_tags)
                if tags and all(tag == target_tag for tag in tags.split(","))
            }
            assert expected_hidden, "expected at least one recipe solely tagged with the target tag"

            tag_toggles.first.uncheck()
            expect(page.locator("[data-tag-status]")).to_have_text(
                f"Showing {tag_count - 1} of {tag_count} tags"
            )
            for index in range(item_count):
                if index in expected_hidden:
                    expect(items.nth(index)).to_be_hidden()
                else:
                    expect(items.nth(index)).to_be_visible()

            tag_toggles.first.check()
            expect(page.locator("[data-recipe-item]:not([hidden])")).to_have_count(item_count)
            expect(page.locator("[data-tag-status]")).to_have_text(
                f"Showing {tag_count} of {tag_count} tags"
            )
        finally:
            browser.close()


def test_tag_clear_all_button_deselects_and_reselects_every_tag(live_url):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(live_url)
            page.locator("[data-filter-drawer] summary").click()

            tag_toggles = page.locator("[data-tag-toggle]")
            clear_button = page.locator("[data-tag-clear]")
            tag_count = tag_toggles.count()

            expect(clear_button).to_have_text("Clear all")
            for index in range(tag_count):
                expect(tag_toggles.nth(index)).to_be_checked()

            clear_button.click()
            expect(page.locator("[data-tag-status]")).to_have_text(f"Showing 0 of {tag_count} tags")
            for index in range(tag_count):
                expect(tag_toggles.nth(index)).not_to_be_checked()
            expect(clear_button).to_have_text("Select all")

            clear_button.click()
            expect(page.locator("[data-tag-status]")).to_have_text(
                f"Showing {tag_count} of {tag_count} tags"
            )
            for index in range(tag_count):
                expect(tag_toggles.nth(index)).to_be_checked()
            expect(clear_button).to_have_text("Clear all")
        finally:
            browser.close()


def test_tag_link_navigates_to_the_single_tag_results_page(live_url):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(live_url)
            page.locator("[data-filter-drawer] summary").click()

            wrapper = page.locator("[data-tag-toggle-wrapper]").first
            target_tag = wrapper.locator("[data-tag-toggle]").get_attribute("value")
            expected_titles = set(
                page.locator("[data-recipe-item]").evaluate_all(
                    """(items, tag) => items
                        .filter(item => (item.dataset.tags || "").split(",").includes(tag))
                        .map(item => item.querySelector("a").textContent)""",
                    target_tag,
                )
            )

            wrapper.locator(".tag-toggle-link").click()

            page.wait_for_url(f"**/search-results/?tag={target_tag.replace(' ', '+')}")
            expect(page.locator("h1")).to_have_text(target_tag.title())
            result_titles = set(page.locator(".result-list a").all_inner_texts())
            assert result_titles == expected_titles
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

            input_field.fill(query)
            input_field.press("ArrowDown")
            expect(page.locator("[role='option']").first).to_have_attribute("aria-selected", "true")
            first_recipe = next(recipe for recipe in recipes if recipe["title"] == expected[0])
            input_field.press("Enter")
            page.wait_for_url(f"**{first_recipe['url']}")
            expect(page.locator("h1")).to_have_text(expected[0])
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


def test_photo_gallery_opens_a_lightbox_and_navigates_without_leaving_the_page(live_url):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(live_url)
            recipe_urls = page.locator("[data-search-option]").evaluate_all(
                "options => options.map(option => option.dataset.url)"
            )

            gallery_url = None
            photo_count = 0
            for recipe_url in recipe_urls:
                page.goto(f"{live_url}{recipe_url}", wait_until="domcontentloaded")
                count = page.locator("[data-gallery-trigger]").count()
                if count >= 3:
                    gallery_url = recipe_url
                    photo_count = count
                    break
            assert gallery_url is not None, "expected at least one recipe with 3+ photos"

            starting_url = page.url
            lightbox = page.locator("[data-lightbox]")
            counter = page.locator("[data-lightbox-counter]")
            image = page.locator("[data-lightbox-image]")
            triggers = page.locator("[data-gallery-trigger]")
            expect(lightbox).to_be_hidden()

            # Clicking a photo opens it in-page, rather than navigating away.
            triggers.first.click()
            expect(lightbox).to_be_visible()
            expect(counter).to_have_text(f"Photo 1 of {photo_count}")
            first_src = image.get_attribute("src")
            assert page.url == starting_url

            # The next/previous controls step through photos without navigating.
            page.locator("[data-lightbox-next]").click()
            expect(counter).to_have_text(f"Photo 2 of {photo_count}")
            second_src = image.get_attribute("src")
            assert second_src != first_src
            assert page.url == starting_url

            page.keyboard.press("ArrowRight")
            expect(counter).to_have_text(f"Photo 3 of {photo_count}")

            page.keyboard.press("ArrowLeft")
            expect(counter).to_have_text(f"Photo 2 of {photo_count}")

            # Escape closes the viewer and restores focus to the triggering thumbnail.
            page.keyboard.press("Escape")
            expect(lightbox).to_be_hidden()
            expect(triggers.first).to_be_focused()
            assert page.url == starting_url

            # Clicking the backdrop also closes the viewer.
            triggers.nth(1).click()
            expect(lightbox).to_be_visible()
            expect(counter).to_have_text(f"Photo 2 of {photo_count}")
            page.locator(".lightbox-backdrop").click(position={"x": 5, "y": 5})
            expect(lightbox).to_be_hidden()

            # Navigation wraps around from the last photo back to the first.
            triggers.nth(photo_count - 1).click()
            expect(counter).to_have_text(f"Photo {photo_count} of {photo_count}")
            page.locator("[data-lightbox-next]").click()
            expect(counter).to_have_text(f"Photo 1 of {photo_count}")

            # The explicit close button also dismisses the viewer.
            page.locator("[data-lightbox-close]").click()
            expect(lightbox).to_be_hidden()
        finally:
            browser.close()


def test_ingredient_export_copies_selected_ingredient_names_without_quantities(live_url):
    def copied_message(count):
        return f"Copied {count} ingredient{'' if count == 1 else 's'} to your clipboard."

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(permissions=["clipboard-read", "clipboard-write"])
        page = context.new_page()
        try:
            page.goto(live_url)
            recipe_urls = page.locator("[data-search-option]").evaluate_all(
                "options => options.map(option => option.dataset.url)"
            )

            ingredients_url = None
            ingredient_count = 0
            for recipe_url in recipe_urls:
                page.goto(f"{live_url}{recipe_url}", wait_until="domcontentloaded")
                count = page.locator("[data-ingredient-toggle]").count()
                if count >= 3:
                    ingredients_url = recipe_url
                    ingredient_count = count
                    break
            assert ingredients_url is not None, "expected at least one recipe with 3+ ingredients"

            toggles = page.locator("[data-ingredient-toggle]")
            status = page.locator("[data-ingredient-status]")
            clear_button = page.locator("[data-ingredient-clear]")
            copy_button = page.locator("[data-ingredient-copy]")
            copy_status = page.locator("[data-ingredient-copy-status]")

            # Every ingredient is selected by default.
            for index in range(ingredient_count):
                expect(toggles.nth(index)).to_be_checked()
            expect(status).to_have_text(f"{ingredient_count} of {ingredient_count} ingredients selected")
            expect(clear_button).to_have_text("Clear all")

            expected_names = toggles.evaluate_all("els => els.map(el => el.dataset.ingredientName)")
            raw_ingredient_text = page.locator(".ingredient-toggle span").first.inner_text()
            # The visible label keeps the original quantity; only the export omits it.
            assert raw_ingredient_text != expected_names[0]

            # Copying with everything selected puts every quantity-free name on the clipboard.
            # The button's own label briefly flashes "Copied!" (avoiding a layout-shifting message
            # below it), while the full description is still announced via the hidden live region.
            default_copy_label = copy_button.inner_text()
            copy_button.click()
            expect(copy_button).to_have_text("Copied!")
            expect(copy_status).to_have_text(copied_message(ingredient_count))
            assert page.evaluate("navigator.clipboard.readText()") == "\n".join(expected_names)
            expect(copy_button).to_have_text(default_copy_label, timeout=3000)

            # Deselecting one ingredient (as if the user already has it) excludes it from the export.
            toggles.first.uncheck()
            expect(status).to_have_text(f"{ingredient_count - 1} of {ingredient_count} ingredients selected")
            copy_button.click()
            expect(copy_button).to_have_text("Copied!")
            expect(copy_status).to_have_text(copied_message(ingredient_count - 1))
            assert page.evaluate("navigator.clipboard.readText()") == "\n".join(expected_names[1:])
            expect(copy_button).to_have_text(default_copy_label, timeout=3000)

            # "Clear all" deselects everything and flips its own label to "Select all".
            clear_button.click()
            expect(status).to_have_text(f"0 of {ingredient_count} ingredients selected")
            for index in range(ingredient_count):
                expect(toggles.nth(index)).not_to_be_checked()
            expect(clear_button).to_have_text("Select all")

            # Attempting to copy with nothing selected is a no-op with a clear message, and the
            # button label flashes an explanation instead of a full sentence below it.
            copy_button.click()
            expect(copy_button).to_have_text("Select an ingredient")
            expect(copy_status).to_have_text("Select at least one ingredient to copy.")
            expect(copy_button).to_have_text(default_copy_label, timeout=3000)

            # "Select all" restores every ingredient.
            clear_button.click()
            expect(status).to_have_text(f"{ingredient_count} of {ingredient_count} ingredients selected")
            for index in range(ingredient_count):
                expect(toggles.nth(index)).to_be_checked()
            expect(clear_button).to_have_text("Clear all")
        finally:
            browser.close()

