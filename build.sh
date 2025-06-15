#!/bin/bash --noprofile

set -x -o pipefail

tag=$1
build=$2

cat <<EOF >src/.buildinfo.json
{
    "tag": "${tag}:${build}",
    "date": "$(date -I)",
    "host": "$(hostname -f)",
    "user": "${USER}"
}
EOF

docker build -t ${tag}:latest .
if [[ $build != "" ]]; then
    docker build -t ${tag}:${build} .
fi
