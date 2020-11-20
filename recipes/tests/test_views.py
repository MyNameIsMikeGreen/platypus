from django.test import TestCase
from django.test import Client

client = Client()


class IndexViewWithFixturesTest(TestCase):

    fixtures = ['recipes.json']

    def test_index_exists(self):
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/index.html')

    def test_index_displays_recipes_list_when_recipes_are_present(self):
        response = client.get('/')
        self.assertInHTML('<h1>Recipes</h1>', response.content.decode("utf-8"))


class IndexViewWithoutFixturesTest(TestCase):
    def test_index_displays_error_when_no_recipes_present(self):
        response = client.get('/')
        self.assertInHTML('<p>No recipes are available.</p>', response.content.decode("utf-8"))


class DetailWithFixturesTest(TestCase):

    fixtures = ['recipes.json']

    def test_details_returns_200_when_recipe_present(self):
        response = client.get('/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/detail.html')

    def test_details_without_trailing_slash_redirects(self):
        response = client.get('/1')
        self.assertRedirects(response, '/1/', status_code=301)


class DetailWithoutFixturesTest(TestCase):

    def test_details_returns_404_when_recipe_not_present(self):
        response = client.get('/69/')
        self.assertEqual(response.status_code, 404)


class PlannerViewTest(TestCase):
    def test_planner_exists(self):
        response = client.get('/planner/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/planner.html')

    def test_planner_without_trailing_slash_redirects(self):
        response = client.get('/planner')
        self.assertRedirects(response, '/planner/', status_code=301)


class PlannerResultsViewTest(TestCase):

    fixtures = ['recipes.json']

    def test_planner_results_exists(self):
        response = client.get('/planner/3/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/planner_results.html')

    def test_planner_results_without_trailing_slash_redirects(self):
        response = client.get('/planner/3')
        self.assertRedirects(response, '/planner/3/', status_code=301)

    def test_planner_results_returns_404_if_request_too_large(self):
        response = client.get('/planner/69/')
        self.assertEqual(response.status_code, 404)


class AboutViewTest(TestCase):
    def test_about_exists(self):
        response = client.get('/about/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/about.html')

    def test_about_without_trailing_slash_redirects(self):
        response = client.get('/about')
        self.assertRedirects(response, '/about/', status_code=301)
