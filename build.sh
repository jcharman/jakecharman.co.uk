#!/bin/bash --noprofile

set -x -o pipefail

tag=$1
build=$2

docker build -t ${tag}:latest .
if [[ $build != "" ]]; then
    docker build -t ${tag}:${build} .
fi
