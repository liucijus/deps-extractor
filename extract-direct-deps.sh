#!/bin/bash

PROJECTS=projects

PROJECT=wix-ci-original

OUTPUT=output/$PROJECT

rm -rf $OUTPUT
mkdir -p $OUTPUT/third_party

cp artifacts.star $OUTPUT

# convert bzl -> starlark
./convert.py $HOME/$PROJECTS/$PROJECT $OUTPUT

# generate maven.artifacts
# get starlark-go:
# docker run -v /tmp/bin:/go/bin golang go get -u go.starlark.net/cmd/starlark

cd $OUTPUT || exit

mkdir -p $HOME/$PROJECTS/$PROJECT/third_party/maven

starlark artifacts.star 2>&1 | buildifier --type=bzl > $HOME/$PROJECTS/$PROJECT/third_party/maven/local_repo_artifacts.bzl



