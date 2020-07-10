import unittest

from django.test import TestCase
from django.test import Client

client = Client()


class IndexViewTest(unittest.TestCase):
    def test_index_exists(self):
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed(response, 'index.html')
        # self.assertInHTML(response, "<p>No recipes are available.</p>")


class DetailWithFixturesTest(unittest.TestCase):

    fixtures = ['recipes.json']

    def test_details_returns_200_when_recipe_present(self):
        response = client.get('/1/')
        self.assertEqual(response.status_code, 200)


class DetailWithoutFixturesTest(unittest.TestCase):

    def test_details_returns_404_when_recipe_not_present(self):
        response = client.get('/69/')
        self.assertEqual(response.status_code, 404)


class AboutViewTest(unittest.TestCase):
    def test_about_exists(self):
        response = client.get('/about')
        self.assertEqual(response.status_code, 200)
