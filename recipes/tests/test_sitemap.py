import re
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
        recipe_log_elements = self._sitemap_loc_elements(r"^https://testserver/recipes/\d+/[a-z-]+/$")
        self.assertEqual(len(recipe_log_elements), recipe_count, "All recipes have an entry")

    def _sitemap_loc_elements(self, regex=None):
        response = client.get('/sitemap.xml')
        response_tree = ET.fromstring(response.content.decode("utf-8"))
        all_locs = response_tree.findall(f"{{{SITEMAP_SCHEMA}}}url/{{{SITEMAP_SCHEMA}}}loc")
        if regex:
            return [loc_element for loc_element in all_locs if re.match(regex, loc_element.text)]
        return all_locs
