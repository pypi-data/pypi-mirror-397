cd tmp/test-project

uv run facet db migrate "add example_products"
uv run facet db upgrade