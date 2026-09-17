# Changelog

## [1.2.5]

- Minimize differences across all *-client source code

## [1.2.4]

- Support nested #foreach

## [1.2.3]

- Support #foreach dynamic loop directive

## [1.2.2]

- Support ${param} template variable and enforce ${param} in #if conditions

## [1.2.1]

- Collect queries in Client class and delete query_all.py

## [1.2.0]

- Support name referencing via `#include name` and `#include name(key)`

## [1.1.1]

- Refactoring code to apply ruff format, ruff check

## [1.1.0]

- Query changed to yml file format from python dict format.

## [1.0.10]

Fixed:
`%` in children not replaced to `{percent}`, so replaced after `json.dumps`

## [1.0.9]

Fixed:
Included query_by_key sub directory by modifying pyproject.toml
