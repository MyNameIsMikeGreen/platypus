from datetime import date
from threading import Thread
from wsgiref.simple_server import WSGIRequestHandler, make_server

import pytest
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.wsgi import get_wsgi_application

from recipes.catalog import RecipeData


class QuietRequestHandler(WSGIRequestHandler):
    def log_message(self, _format: str, *_args: object) -> None:
        pass


@pytest.fixture(scope="session")
def live_url():
    application = StaticFilesHandler(get_wsgi_application())
    server = make_server(
        "127.0.0.1",
        0,
        application,
        handler_class=QuietRequestHandler,
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.fixture
def recipe_factory(monkeypatch):
    recipes: list[RecipeData] = []

    def catalog():
        return tuple(sorted(recipes, key=lambda recipe: recipe.title.casefold()))

    monkeypatch.setattr("recipes.views.CATALOG", catalog())
    monkeypatch.setattr("recipes.forms.CATALOG", catalog())
    created = 0

    def create(**overrides):
        nonlocal created
        created += 1
        defaults = {
            "id": created,
            "slug": f"test-recipe-{created}",
            "title": f"Test Recipe {created}",
            "ingredients": ["Ingredient"],
            "instructions": ["Do the thing."],
            "category": "MAINS",
            "published_on": date(2025, 1, 1),
            "is_final": True,
            "tags": [],
            "image_urls": [],
        }
        defaults.update(overrides)
        for field in ("ingredients", "instructions", "tags", "image_urls"):
            defaults[field] = tuple(defaults[field])
        recipe = RecipeData(**defaults)
        recipes.append(recipe)
        current_catalog = catalog()
        monkeypatch.setattr("recipes.views.CATALOG", current_catalog)
        monkeypatch.setattr("recipes.forms.CATALOG", current_catalog)
        return recipe

    return create
