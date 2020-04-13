#!/bin/bash

mkdir -p output

./extract-deps-pom.py $1 | buildifier > output/managed_artifacts.bzl

