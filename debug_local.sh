#!/bin/bash --noprofile

run() {
    python3 src/projects.wsgi || run
}

export DISCORD_ERR_HOOK='dummy'
run
unset DISCORD_ERR_HOOK