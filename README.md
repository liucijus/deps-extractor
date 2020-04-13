# Migrate deps to rules_jvm_external

## Repo deps
Extracts deps from `third_party.bzl` by running it

Usage: `./extract-deps <repo dir>`

## pom.xml deps
Usage: `./extract-pom.sh <pom file>`

Assumes exist on the path:
 - [starlark](https://github.com/google/starlark-go/)
 - [buildifier](https://github.com/bazelbuild/buildtools/blob/master/buildifier/README.md)
