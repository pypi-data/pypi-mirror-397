# paxx

Python Async API - a domain-oriented web framework built on top of FastAPI.

Resync paxx in scaffolded project:

```
uv sync --reinstall-package paxx
```

Recreate tmp feature:

```
sh scripts/paxx-reboot.sh
```

Test paxx flow:

```
sh scripts/test-paxx.sh
```

Check package name:

```
curl -s -o /dev/null -w "%{http_code}" https://pypi.org/pypi/NAME/json
```
