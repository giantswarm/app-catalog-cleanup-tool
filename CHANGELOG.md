# Changelog

Based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), following [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.7] - 2024-02-20

- Update
    - Update setup-helm and helm versions in the cleanup action

## [0.2.6] - 2024-02-13

- Update
    - Stop using deprecated set outputs

## [0.2.5] - 2022-03-11

## [0.2.4] - 2021-10-14

- Fixed
  - Do not try to remove non-existing app
  - Try to preserve standard formatting of the helm index.yaml

## [0.2.3] - 2021-10-12

- Changed
  - Disable draft PRs in the cleanup workflow

## [0.2.2] - 2021-10-11

- Removed
  - Remove `team-reviewers` from the action in favour of the CODEOWNERS

## [0.2.1] - 2021-10-11

## [0.2.0] - 2021-10-08

- Added
  - Add [Reusable Workflow](https://docs.github.com/en/actions/learn-github-actions/reusing-workflows) to be called from
    the App Catalogs repositories.

## [0.1.2]

## [0.1.1]

- Added
  - Initial commit

[Unreleased]: https://github.com/giantswarm/app-catalog-cleanup-tool/compare/v0.2.5...HEAD
[0.2.5]: https://github.com/giantswarm/app-catalog-cleanup-tool/compare/v0.2.4...v0.2.5
[0.2.4]: https://github.com/giantswarm/app-catalog-cleanup-tool/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/giantswarm/app-catalog-cleanup-tool/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/giantswarm/app-catalog-cleanup-tool/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/giantswarm/app-catalog-cleanup-tool/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/giantswarm/app-catalog-cleanup-tool/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/giantswarm/app-catalog-cleanup-tool/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/giantswarm/app-catalog-cleanup-tool/releases/tag/v0.1.1
