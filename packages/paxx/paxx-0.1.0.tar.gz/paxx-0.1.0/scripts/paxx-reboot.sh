cd tmp
rm -rf test-project
uv run paxx bootstrap test-project

cd test-project
uv sync --all-extras

uv sync --reinstall-package paxx

uv run paxx feature add example_products

uv run paxx db migrate "add example_products"
uv run paxx db upgrade