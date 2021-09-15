# app catalog cleanup tool

A simple tool to remove old Helm charts stored in a chart repository.

## How does it work

You specify a removal condition and a regexp to match application names. All chart entries matching
the regexp and matching the condition are removed, i.e.:

- relevant entry is removed from the `index.yaml` file
- the chart file is removed
- if exists, the metadata directory is removed.

For a list of available conditions, please run with `--help|-h`.

## Examples

1. Remove all app entries for the `linkerd2-app` that are older than '2019-01-01' for the catalog stored in `/tmp/giantswarm-playground-catalog`

    ```bash
    python -m app_catalog_cleanup_tool -a "linkerd2-app" -s "2019-01-01" /tmp/giantswarm-playground-catalog
    ```

2. Remove all app entries older than 4 weeks for the catalog stored in `/tmp/giantswarm-playground-catalog`

    ```bash
    python -m app_catalog_cleanup_tool -a ".*" -b "4 weeks" /tmp/giantswarm-playground-catalog
    ```

3. Keep only at most 3 most recent builds of all apps which names start with "loki"

    ```bash
    python -m app_catalog_cleanup_tool -a "loki.*" -l 3 /tmp/giantswarm-playground-catalog
    ```

## Development

Use `pipenv` to manage dependencies and `pre-commit` to check for code quality. To get started, check out the repo
and run:

```bash
pipenv install -d
pipenv run pre-commit install --install-hooks
```
