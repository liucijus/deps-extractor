#!/bin/bash

PROJECTS=projects

PROJECT=wix-ci-original

OUTPUT=output/$PROJECT

rm -rf $OUTPUT
mkdir -p $OUTPUT/third_party

cp $HOME/$PROJECTS/$PROJECT/third_party.bzl $OUTPUT/ 
cp $HOME/$PROJECTS/$PROJECT/third_party/*bzl $OUTPUT/third_party/

# convert bzl -> starlark
./convert.py $OUTPUT

# generate maven.artifacts
# get starlark-go:
# docker run -v /tmp/bin:/go/bin golang go get -u go.starlark.net/cmd/starlark

cd $OUTPUT || exit

starlark third_party.star 



