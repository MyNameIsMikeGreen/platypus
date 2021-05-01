from django.contrib.sitemaps import Sitemap

from recipes.models import Recipe


class RecipeSitemap(Sitemap):
    changefreq = "monthly"
    protocol = "https"

    def items(self):
        return Recipe.objects.all()

    def lastmod(self, item):
        return item.published_date
