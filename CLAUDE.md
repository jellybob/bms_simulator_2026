Read the readme.

When running under Claude Code the actual application will be within a container,
which you can access with `docker compose`. Most things should be done in the `server`
container, which will have this directory mounted within it.

Use the tests. They can be run with `docker compose run -T server pytest`.
Use ruff, which is run with `docker compose run server ruff check`.
Format the code with `docker compose run server ruff format .`.

When making changes to the server you only need to look in `src/` and `tests/`. The
web interface is in `web/`. I will usually ask you to only work on one of those at a
time, if I haven't explicitly asked for the other ignore it.
