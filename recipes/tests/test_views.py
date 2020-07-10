import unittest
from django.test import Client

client = Client()


class IndexViewTest(unittest.TestCase):
    def test_index_exists(self):
        response = client.get('/')
        self.assertEqual(response.status_code, 200)


class DetailTest(unittest.TestCase):
    def test_details_returns_404_when_recipe_not_populated(self):
        response = client.get('/69/')
        self.assertEqual(response.status_code, 404)


class AboutViewTest(unittest.TestCase):
    def test_about_exists(self):
        response = client.get('/about')
        self.assertEqual(response.status_code, 200)

