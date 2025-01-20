#!/usr/bin/bash

source $HOME/www/python/venv/bin/activate
dykbot \
    --no-dry-run \
    --mylang=test \
    --log-level=info \
    --log-file=$HOME/dykbot.log \
    --basedir=$HOME/www/python \
    add-tags
