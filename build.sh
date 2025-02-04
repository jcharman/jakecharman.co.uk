#!/bin/bash --noprofile

set -x -o pipefail

tag=$1
buidl=${build:-0}

docker build -t ${tag}:latest .
if [[ $build -gt 0 ]]; then
    docker build -t ${tag}:${build} .
fi
