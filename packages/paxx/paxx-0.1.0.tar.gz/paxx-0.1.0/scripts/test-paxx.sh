cd tmp
rm -rf test-project
uv run paxx bootstrap test-project

cd test-project
uv sync --all-extras

uv sync --reinstall-package paxx

uv run paxx feature add example_products

uv run paxx db status

uv run paxx db migrate "add example_products"
uv run paxx db upgrade

uv run paxx db status

# migration down
uv run paxx db downgrade

uv run paxx db status

# migration up
uv run paxx db upgrade

uv run paxx db status

# remove and add feature again
rm -rf features/example_products

uv run paxx feature add example_products

uv run paxx feature create test_feature

open http://127.0.0.1:8000/docs

uv run paxx start





