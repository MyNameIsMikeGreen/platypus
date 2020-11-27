from django.test import TestCase
from django.test import Client
from lxml import html

from recipes.models import Recipe

client = Client()


class IndexViewWithFixturesTest(TestCase):

    fixtures = ['recipes.json']

    def test_index_exists(self):
        response = client.get('/')
        self.assertEqual(response.status_code, 200, msg="HTTP 200 returned")
        self.assertTemplateUsed(response, 'recipes/index.html')

    def test_index_displays_recipes_list_when_recipes_are_present(self):
        response = client.get('/')
        self.assertInHTML('<h1>Recipes</h1>', response.content.decode("utf-8"))
        self.assertInHTML('<h2>DESSERTS</h2>', response.content.decode("utf-8"))
        self.assertInHTML('<li><a href="/1/">Ice Cream</a></li>', response.content.decode("utf-8"))


class IndexViewWithoutFixturesTest(TestCase):
    def test_index_displays_error_when_no_recipes_present(self):
        response = client.get('/')
        self.assertInHTML('<p>No recipes are available.</p>', response.content.decode("utf-8"))


class DetailWithFixturesTest(TestCase):

    fixtures = ['recipes.json']

    def test_details_returns_200_when_recipe_present(self):
        response = client.get('/1/')
        self.assertEqual(response.status_code, 200, msg="HTTP 200 returned")
        self.assertTemplateUsed(response, 'recipes/detail.html')

    def test_details_without_trailing_slash_redirects(self):
        response = client.get('/1')
        self.assertRedirects(response, '/1/', status_code=301)


class DetailWithoutFixturesTest(TestCase):

    def test_details_returns_404_when_recipe_not_present(self):
        response = client.get('/69/')
        self.assertEqual(response.status_code, 404, msg="HTTP 404 returned")


class PlannerView(TestCase):

    fixtures = ['recipes.json']

    def test_planner_input_template_used_if_no_params_provided(self):
        response = client.get('/planner/')
        self.assertEqual(response.status_code, 200, msg="HTTP 200 returned")
        self.assertTemplateUsed(response, 'recipes/planner_input.html')

    def test_planner_results_template_used_if_valid_recipe_count_param_provided(self):
        response = client.get('/planner/?recipe_count=3')
        self.assertEqual(response.status_code, 200, msg="HTTP 200 returned")
        self.assertTemplateUsed(response, 'recipes/planner_results.html')

    def test_planner_without_trailing_slash_redirects(self):
        response = client.get('/planner')
        self.assertRedirects(response, '/planner/', status_code=301)

    def test_planner_results_returns_list_containing_number_of_recipes_requested(self):
        for recipes_to_request in range(1, 10):
            recipes_list_length = self._count_recipe_links_from_planner(recipes_to_request)
            self.assertEqual(recipes_list_length, recipes_to_request, "Recipe list size equals the recipes requested")

    def test_planner_results_returns_random_list_on_each_request(self):
        link_list_initial = self._fetch_recipe_links_from_planner(5)
        link_list_repeat = self._fetch_recipe_links_from_planner(5)
        self.assertNotEqual(link_list_initial, link_list_repeat, "Linked recipes are different between requests")

    def test_planner_results_returns_only_recipes_from_category_requested(self):
        recipes_to_request = 25

        category_to_request = "MAINS"
        link_list = self._fetch_recipe_links_from_planner(recipes_to_request, category_to_request)
        self._assert_recipe_list_contains_only_recipes_from_category(link_list, category_to_request)

        category_to_request = "DESSERTS"
        link_list = self._fetch_recipe_links_from_planner(recipes_to_request, category_to_request)
        self._assert_recipe_list_contains_only_recipes_from_category(link_list, category_to_request)

        category_to_request = "OTHER"
        link_list = self._fetch_recipe_links_from_planner(recipes_to_request, category_to_request)
        self._assert_recipe_list_contains_only_recipes_from_category(link_list, category_to_request)

    def test_planner_results_returns_only_unique_results(self):
        recipes_to_request = 25
        link_list = self._fetch_recipe_links_from_planner(recipes_to_request)
        link_set = set(link_list)
        self.assertEqual(len(link_set), len(link_list), msg="Recipe list contains no duplicates")

    def test_planner_results_returns_all_recipes_in_category_if_too_many_requested(self):
        recipes_to_request = 9999
        category_to_request = "MAINS"
        link_list = self._fetch_recipe_links_from_planner(recipes_to_request, category_to_request)
        recipes_in_category = Recipe.objects.filter(category=category_to_request)
        self.assertEqual(len(link_list), len(recipes_in_category), msg="Recipe list size doesnt exceed max recipes")

    def _assert_recipe_list_contains_only_recipes_from_category(self, link_list, category):
        for link in link_list:
            recipe = Recipe.objects.get(pk=_get_id_from_link(link))
            self.assertEqual(recipe.category, category, msg=f"Recipe is in the {category} category")

    @staticmethod
    def _count_recipe_links_from_planner(recipes_to_request):
        response = client.get(f'/planner/?recipe_count={recipes_to_request}')
        response_tree = html.fromstring(response.content.decode("utf-8"))
        return len(response_tree.xpath('//div[@id="platypus-content"]/ul/li'))

    @staticmethod
    def _fetch_recipe_links_from_planner(recipe_count, category="MAINS"):
        response = client.get(f'/planner/?recipe_count={recipe_count}&category={category}')
        response_tree = html.fromstring(response.content.decode("utf-8"))
        return response_tree.xpath('//div[@id="platypus-content"]/ul/li/a/@href')


class AboutViewTest(TestCase):
    def test_about_exists(self):
        response = client.get('/about/')
        self.assertEqual(response.status_code, 200, msg="HTTP 200 returned")
        self.assertTemplateUsed(response, 'recipes/about.html')

    def test_about_without_trailing_slash_redirects(self):
        response = client.get('/about')
        self.assertRedirects(response, '/about/', status_code=301)


def _get_id_from_link(link: str):
    return int(link.strip().replace("/", ""))
