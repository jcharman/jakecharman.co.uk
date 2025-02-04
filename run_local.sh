#!/bin/bash --noprofile

set -x -o pipefail

./build.sh "jc-ng-localtest"

content_dir=""
if [[ -d "../jc-content" ]]; then
     content_dir="-v $(realpath ../jc-content):/var/www/jc/projects"
fi

docker run -v $(pwd)/src/:/var/www/jc $content_dir jc-ng-localtest

