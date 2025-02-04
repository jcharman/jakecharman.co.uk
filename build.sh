#!/bin/bash --noprofile

set -x -o pipefail

tag=$1
build=${$2:-0}

docker build -t ${tag}:latest .
if [[ $build -gt 0 ]]; then
    docker build -t ${tag}:${build} .
fi
