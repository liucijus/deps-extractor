#!/bin/bash

PROJECTS=projects

PROJECT=$1

OUTPUT=output/$PROJECT

rm -rf $OUTPUT
mkdir -p $OUTPUT/third_party

cp artifacts.star $OUTPUT/

# convert bzl -> starlark
./convert.py $HOME/$PROJECTS/$PROJECT $OUTPUT

# generate maven.artifacts
# get starlark-go:
# docker run -v /tmp/bin:/go/bin golang go get -u go.starlark.net/cmd/starlark

cd $OUTPUT || exit

mkdir -p $HOME/$PROJECTS/$PROJECT/third_party/maven

starlark artifacts.star 2>&1 | buildifier --type=bzl > local_repo_artifacts.bzl

cp local_repo_artifacts.bzl $HOME/$PROJECTS/$PROJECT/third_party/maven/



