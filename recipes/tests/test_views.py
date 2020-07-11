from django.test import TestCase
from django.test import Client

client = Client()


class IndexViewTest(TestCase):
    def test_index_exists(self):
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/index.html')


class DetailWithFixturesTest(TestCase):

    fixtures = ['recipes.json']

    def test_details_returns_200_when_recipe_present(self):
        response = client.get('/1/')
        self.assertEqual(response.status_code, 200)


class DetailWithoutFixturesTest(TestCase):

    def test_details_returns_404_when_recipe_not_present(self):
        response = client.get('/69/')
        self.assertEqual(response.status_code, 404)


class AboutViewTest(TestCase):
    def test_about_exists(self):
        response = client.get('/about/')
        self.assertEqual(response.status_code, 200)

    def test_about_without_trailing_slash_redirects(self):
        response = client.get('/about')
        self.assertEqual(response.status_code, 301)
