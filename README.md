# app catalog cleanup tool

[![build](https://circleci.com/gh/giantswarm/app-catalog-cleanup-tool.svg?style=svg)](https://circleci.com/gh/giantswarm/app-catalog-cleanup-tool)
[![codecov](https://codecov.io/gh/giantswarm/app-catalog-cleanup-tool/branch/master/graph/badge.svg)](https://codecov.io/gh/giantswarm/app-catalog-cleanup-tool)
[![Apache License](https://img.shields.io/badge/license-apache-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

A simple tool to remove old Helm charts stored in a chart repository.

## How does it work

You specify a removal condition and a regexp to match application names. All chart entries matching
the regexp and matching the condition are removed, i.e.:

- relevant entry is removed from the `index.yaml` file
- the chart file is removed
- if exists, the metadata directory is removed.

For a list of available conditions, please run with `--help|-h`.

## Running

There are currently 2 options:

1. Using your native python 3 installation.

   - Checkout the source code from repository
   - Run `pipenv install`
   - Start the tool using `pipenv run python -m app_catalog_cleanup_tool ...`

2. Using the dockerized version

   You can use the dockerized version available as a convenience script `dacct.sh`. Please note, that currently the
   dockerized version can work on
   the current directory only, so you have to download the script, make it executable in your system, then run it
   in the directory with a catalog
   giving the local directory `.` as the ast argument.

   Example:

   ```bash
   dacct.sh -a ".*" -s "2020-02-01" -d -n .
   ```

## Examples

1. Remove all app entries for the `linkerd2-app` that are older than '2019-01-01' for the catalog stored in `/tmp/giantswarm-playground-catalog`

   ```bash
   python -m app_catalog_cleanup_tool -a "linkerd2-app" -s "2019-01-01" /tmp/giantswarm-playground-catalog
   ```

2. Remove all app entries older than 4 weeks for the catalog stored in `/tmp/giantswarm-playground-catalog`

   ```bash
   python -m app_catalog_cleanup_tool -a ".*" -b "4 weeks" /tmp/giantswarm-playground-catalog
   ```

3. Keep at most the 3 most recent builds of all apps with names starting with "loki"

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

## Update catalog repos

Since renovate bot doesn't work for catalog repos, one can use a script `./bin/update-catalag-repos`. It should be executed from the root of this project.

It depends on yq and github-cli, os both of them must be installed and configured.
