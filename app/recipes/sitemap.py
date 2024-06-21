from django.contrib.sitemaps import Sitemap

from .models import Recipe


class RecipePageSitemap(Sitemap):
    changefreq = "monthly"
    protocol = "https"

    def items(self):
        return Recipe.objects.all()

    def lastmod(self, item):
        return item.published_date


class SupportPageSitemap(Sitemap):
    changefreq = "monthly"
    protocol = "https"

    def items(self):
        return ['/', '/planner/', '/about/']

    def location(self, item):
        return item
