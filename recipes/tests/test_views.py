from django.test import TestCase
from django.test import Client
from lxml import html

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


class PlannerViewTest(TestCase):
    def test_planner_exists(self):
        response = client.get('/planner/')
        self.assertEqual(response.status_code, 200, msg="HTTP 200 returned")
        self.assertTemplateUsed(response, 'recipes/planner.html')

    def test_planner_without_trailing_slash_redirects(self):
        response = client.get('/planner')
        self.assertRedirects(response, '/planner/', status_code=301)

    def test_planner_has_title(self):
        response = client.get('/planner/')
        self.assertInHTML('<h1>Meal Planner</h1>', response.content.decode("utf-8"))


class PlannerResultsViewTest(TestCase):

    fixtures = ['recipes.json']

    def test_planner_results_exists(self):
        response = client.get('/planner/3/')
        self.assertEqual(response.status_code, 200, msg="HTTP 200 returned")
        self.assertTemplateUsed(response, 'recipes/planner_results.html')

    def test_planner_results_without_trailing_slash_redirects(self):
        response = client.get('/planner/3')
        self.assertRedirects(response, '/planner/3/', status_code=301)

    def test_planner_results_returns_list_number_of_recipes_requested(self):
        for recipes_to_request in range(1, 10):
            recipes_list_length = self._count_recipe_links_from_planner(recipes_to_request)
            self.assertEqual(recipes_list_length, recipes_to_request, "Recipe list size equals the recipes requested")

    def test_planner_results_returns_random_list_on_each_request(self):
        link_list_initial = self._fetch_recipe_links_from_planner(5)
        link_list_repeat = self._fetch_recipe_links_from_planner(5)
        self.assertNotEqual(link_list_initial, link_list_repeat, "Linked recipes are different between requests")

    @staticmethod
    def _count_recipe_links_from_planner(recipes_to_request):
        response = client.get(f'/planner/{recipes_to_request}/')
        response_tree = html.fromstring(response.content.decode("utf-8"))
        return len(response_tree.xpath('//div[@id="platypus-content"]/ul/li'))

    @staticmethod
    def _fetch_recipe_links_from_planner(recipe_count):
        response = client.get(f'/planner/{recipe_count}/')
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
