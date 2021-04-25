import xml.etree.ElementTree as ET

from django.test import Client
from django.test import TestCase

from recipes.models import Recipe

SITEMAP_SCHEMA = "http://www.sitemaps.org/schemas/sitemap/0.9"

client = Client()


class SitemapTest(TestCase):

    fixtures = ['recipes.json']

    def test_sitemap_exists(self):
        response = client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200, "HTTP 200 returned")

    def test_sitemap_has_entry_for_each_recipe(self):
        recipe_count = Recipe.objects.all().count()
        self.assertEqual(len(self._sitemap_loc_elements()), recipe_count, "All recipes have an entry")

    def test_sitemap_urls_are_correct(self):
        loc_elements = self._sitemap_loc_elements()
        self.assertGreater(len(loc_elements), 0, "loc elements are found")
        for url in loc_elements:
            self.assertRegex(url.text, "^https://testserver/recipes/\d+/$", "URL matches expected format")

    def _sitemap_loc_elements(self):
        response = client.get('/sitemap.xml')
        response_tree = ET.fromstring(response.content.decode("utf-8"))
        return response_tree.findall(f"{{{SITEMAP_SCHEMA}}}url/{{{SITEMAP_SCHEMA}}}loc")
