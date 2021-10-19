from django.test import TestCase
from django.test import Client
from lxml import html

from recipes.models import Recipe

PROD_FIXTURES = 'recipes.json'
TEST_FIXTURES = 'test_recipes.json'

ENCODING = "utf-8"

client = Client()


class IndexViewWithFixturesTest(TestCase):

    fixtures = [PROD_FIXTURES, TEST_FIXTURES]

    def test_index_exists(self):
        response = client.get('/')
        self.assertEqual(response.status_code, 200, msg="HTTP 200 returned")
        self.assertTemplateUsed(response, 'recipes/index.html')

    def test_index_displays_recipes_list_when_recipes_are_present(self):
        response = client.get('/')
        response_body = response.content.decode(ENCODING)
        self.assertInHTML('<h1>Recipes</h1>', response_body)
        self.assertInHTML('<h2>CONFECTIONERY</h2>', response_body)
        self.assertInHTML('<li><a href="/1/">Ice Cream</a></li>', response_body)

    def test_index_does_not_contain_json_ld_block(self):
        response = client.get('/')
        response_tree = html.fromstring(response.content.decode(ENCODING))
        self.assertEqual(len(response_tree.xpath('//head/script[@type="application/ld+json"]')), 0, "json-ld block not in HTML")

    def test_index_with_search_term_param_matching_only_one_recipe_redirects_to_detail_page(self):
        response = client.get('/', {"search_term": "y89234kl"})
        self.assertRedirects(response, '/recipes/6970/', fetch_redirect_response=False, status_code=301)

    def test_index_with_search_term_param_matching_many_recipes_filters_recipe_lists(self):
        response = client.get('/', {"search_term": "title"})
        response_body = response.content.decode(ENCODING)
        self.assertInHTML('<h1>Recipes</h1>', response_body)
        self.assertInHTML('<h2>LIGHT DISHES</h2>', response_body)
        self.assertInHTML('<li><a href="/6969/">Some recipe title</a></li>', response_body)
        self.assertInHTML('<h2>MAINS</h2>', response_body)
        self.assertInHTML('<li><a href="/6970/">Unique title 923y89234kljj9</a></li>', response_body)
        self.assertNotIn('>Ice Cream</a>', response_body)

    def test_index_with_search_term_param_matching_no_recipes_still_displays_search_bar(self):
        response = client.get('/', {"search_term": "this search term is utter nonsense"})
        response_body = response.content.decode(ENCODING)
        self.assertInHTML('<p>No recipes are available.</p>', response_body)
        self.assertInHTML('<input type="submit" value="Search">', response_body)


class IndexViewWithoutFixturesTest(TestCase):
    def test_index_displays_error_when_no_recipes_present(self):
        response = client.get('/')
        self.assertInHTML('<p>No recipes are available.</p>', response.content.decode(ENCODING))


class DetailWithFixturesTest(TestCase):

    fixtures = [PROD_FIXTURES, TEST_FIXTURES]

    def test_details_returns_200_when_recipe_present(self):
        response = client.get('/1/ice-cream/')
        self.assertEqual(response.status_code, 200, msg="HTTP 200 returned")
        self.assertTemplateUsed(response, 'recipes/detail.html')

    def test_details_contains_json_ld_block(self):
        response = client.get('/1/ice-cream/')
        response_tree = html.fromstring(response.content.decode(ENCODING))
        self.assertEqual(len(response_tree.xpath('//head/script[@type="application/ld+json"]')), 1, "json-ld block in HTML")

    def test_slug_appended_if_omitted(self):
        response = client.get('/1/')
        self.assertEqual(response.url, "/1/ice-cream/")

    def test_slug_corrected_if_incorrect(self):
        response = client.get('/1/spaghetti-cookies/')
        self.assertEqual(response.url, "/1/ice-cream/")

    def test_under_development_icon_shown_when_final_flag_false(self):
        response = client.get('/6969/some-recipe-title/')
        response_tree = html.fromstring(response.content.decode(ENCODING))
        self.assertIn("⚠", response_tree.xpath('//h1')[0].text_content(), "Under development icon is shown")

    def test_icon_not_shown_when_final_flag_true(self):
        response = client.get('/1/ice-cream/')
        response_tree = html.fromstring(response.content.decode(ENCODING))
        self.assertNotIn("&#x26A0;", response_tree.xpath('//h1')[0].text_content(), "Under development icon is not shown")

    def test_tags_shown(self):
        response = client.get('/6969/some-recipe-title/')
        response_tree = html.fromstring(response.content.decode(ENCODING))
        tags = response_tree.xpath('//div[@id="platypus-tag-list"]/div[@id="platypus-tag"]')
        self.assertIn("MakesMouthFeelOuchy", tags[0].text_content(), "First tag from recipe (alphabetically) is shown")
        self.assertIn("Spicy", tags[1].text_content(), "Second tag from recipe (alphabetically) is shown")


class DetailWithoutFixturesTest(TestCase):

    def test_details_returns_404_when_recipe_not_present(self):
        response = client.get('/99999999/')
        self.assertEqual(response.status_code, 404, msg="HTTP 404 returned")


class PlannerView(TestCase):

    fixtures = [PROD_FIXTURES]

    def test_planner_input_template_used_if_no_params_provided(self):
        response = client.get('/planner/')
        self.assertEqual(response.status_code, 200, msg="HTTP 200 returned")
        self.assertTemplateUsed(response, 'recipes/planner_input.html')

    def test_planner_does_not_contain_json_ld_block(self):
        response = client.get('/planner/')
        response_tree = html.fromstring(response.content.decode(ENCODING))
        self.assertEqual(len(response_tree.xpath('//head/script[@type="application/ld+json"]')), 0, "json-ld block not in HTML")

    def test_planner_without_trailing_slash_redirects(self):
        response = client.get('/planner')
        self.assertRedirects(response, '/planner/', status_code=301)

    def test_search_results_returns_random_list_on_each_request(self):
        link_list_initial = self._fetch_recipe_links_from_search_results(5)
        link_list_repeat = self._fetch_recipe_links_from_search_results(5)
        self.assertNotEqual(link_list_initial, link_list_repeat, "Linked recipes are different between requests")

    def test_search_results_returns_only_recipes_from_category_requested(self):
        recipes_to_request = 25

        category_to_request = "MAINS"
        link_list = self._fetch_recipe_links_from_search_results(recipes_to_request, category_to_request)
        self.assertGreater(len(link_list), 0, f"Found {len(link_list)} {category_to_request} recipes")
        self._assert_recipe_list_contains_only_recipes_from_category(link_list, category_to_request)

        category_to_request = "LIGHT DISHES"
        link_list = self._fetch_recipe_links_from_search_results(recipes_to_request, category_to_request)
        self.assertGreater(len(link_list), 0, f"Found {len(link_list)} {category_to_request} recipes")
        self._assert_recipe_list_contains_only_recipes_from_category(link_list, category_to_request)

        category_to_request = "CONFECTIONERY"
        link_list = self._fetch_recipe_links_from_search_results(recipes_to_request, category_to_request)
        self.assertGreater(len(link_list), 0, f"Found {len(link_list)} {category_to_request} recipes")
        self._assert_recipe_list_contains_only_recipes_from_category(link_list, category_to_request)

        category_to_request = "MISCELLANEOUS"
        link_list = self._fetch_recipe_links_from_search_results(recipes_to_request, category_to_request)
        self.assertGreater(len(link_list), 0, f"Found {len(link_list)} {category_to_request} recipes")
        self._assert_recipe_list_contains_only_recipes_from_category(link_list, category_to_request)

    def test_search_results_returns_only_unique_results(self):
        recipes_to_request = 25
        link_list = self._fetch_recipe_links_from_search_results(recipes_to_request)
        link_set = set(link_list)
        self.assertEqual(len(link_set), len(link_list), msg="Recipe list contains no duplicates")

    def test_search_results_returns_all_recipes_in_category_if_too_many_requested(self):
        recipes_to_request = 9999
        category_to_request = "MAINS"
        link_list = self._fetch_recipe_links_from_search_results(recipes_to_request, category_to_request)
        recipes_in_category = Recipe.objects.filter(category=category_to_request)
        self.assertEqual(len(link_list), len(recipes_in_category), msg="Recipe list size doesnt exceed max recipes")

    def _assert_recipe_list_contains_only_recipes_from_category(self, link_list, category):
        for link in link_list:
            recipe = Recipe.objects.get(pk=_get_id_from_link(link))
            self.assertEqual(recipe.category, category, msg=f"Recipe is in the {category} category")

    @staticmethod
    def _fetch_recipe_links_from_search_results(recipe_count, category="MAINS"):
        response = client.get(f'/search-results/', {"recipe_count": recipe_count, "category": category})
        response_tree = html.fromstring(response.content.decode(ENCODING))
        return response_tree.xpath('//div[@id="platypus-content"]/ul/li/a/@href')


class AboutViewTest(TestCase):
    def test_about_exists(self):
        response = client.get('/about/')
        self.assertEqual(response.status_code, 200, msg="HTTP 200 returned")
        self.assertTemplateUsed(response, 'recipes/about.html')

    def test_about_without_trailing_slash_redirects(self):
        response = client.get('/about')
        self.assertRedirects(response, '/about/', status_code=301)

    def test_about_does_not_contain_json_ld_block(self):
        response = client.get('/about/')
        response_tree = html.fromstring(response.content.decode(ENCODING))
        self.assertEqual(len(response_tree.xpath('//head/script[@type="application/ld+json"]')), 0, "json-ld block not in HTML")


class Http404Test(TestCase):
    def test_missing_page_returns_custom_404_view(self):
        response = client.get('/thisPageDoesNotExist/')
        self.assertEqual(response.status_code, 404, msg="HTTP 404 returned")
        self.assertTemplateUsed(response, '404.html')

    def test_about_does_not_contain_json_ld_block(self):
        response = client.get('/thisPageDoesNotExist/')
        response_tree = html.fromstring(response.content.decode(ENCODING))
        self.assertEqual(len(response_tree.xpath('//head/script[@type="application/ld+json"]')), 0, "json-ld block not in HTML")


def _get_id_from_link(link: str):
    return int(link.strip().replace("/", ""))
