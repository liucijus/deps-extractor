#!/bin/bash

REPO_PATH=$1

PROJECT=$(basename $REPO_PATH)

OUTPUT=output/$PROJECT

rm -rf $OUTPUT
mkdir -p $OUTPUT/third_party

cp artifacts.star $OUTPUT/

# convert bzl -> starlark
./convert.py $REPO_PATH $OUTPUT

# generate maven.artifacts
# get starlark-go:
# docker run -v /tmp/bin:/go/bin golang go get -u go.starlark.net/cmd/starlark

cd $OUTPUT || exit

mkdir -p $REPO_PATH/third_party/maven

# run patched files via starlark to generate artifacts.bzl
starlark artifacts.star 2>&1 | buildifier --type=bzl > local_repo_artifacts.bzl

# copy generated file to repo
cp local_repo_artifacts.bzl $REPO_PATH/third_party/maven/



