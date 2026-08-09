# Managing recipes

The application reads recipes directly from [`src/recipes/data/recipes.json`](../src/recipes/data/recipes.json). This file is the only recipe data source.

## Catalog format

The top-level `schema_version` is currently `1`. Each entry in `recipes` contains:

| Field | Meaning |
| --- | --- |
| `id` | Unique positive integer used in the recipe URL |
| `title` | Display title; also produces the canonical URL slug |
| `ingredients` | Ordered, non-empty list of ingredient strings |
| `instructions` | Ordered, non-empty list of method steps |
| `category` | Category shown on the index and planner |
| `published_on` | Original publication date in `YYYY-MM-DD` format |
| `is_final` | `false` displays the under-development notice |
| `tags` | Optional list used for tag links |
| `image_urls` | Optional list of `https://res.cloudinary.com` image URLs |

Recipe prose and ordering are preserved exactly as written. JSON strings must use normal JSON escaping.

## Add or edit a recipe

1. Edit the catalog. For a new recipe, choose an ID that has never been used.
2. Validate it:

   ```shell
   uv run python manage.py check
   ```

3. Run `make check`.
4. Review the page locally using the setup in [`development.md`](development.md).

The catalog must be non-empty and use exactly the documented fields. Duplicate JSON fields, IDs,
and generated slugs are rejected. Invalid data fails checks and the container build. Removing a
recipe from the catalog removes it from the next image; follow the update procedure in
[`deployment.md`](deployment.md#updates) to publish the change.

Do not make this file writable by the running application. Adding browser-side or API editing
changes the security and persistence model and requires the
[`security-boundary.md`](security-boundary.md#before-adding-write-capabilities) plan.
