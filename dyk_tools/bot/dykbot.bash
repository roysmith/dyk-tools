#!/usr/bin/bash

source $HOME/www/python/venv/bin/activate
dykbot \
    --no-dry-run \
    --log-level=debug \
    --log-file=$HOME/dykbot.log
