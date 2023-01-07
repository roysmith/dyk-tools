#!/usr/bin/bash

source $HOME/www/python/venv/bin/activate
cd $HOME/www/python/src
./dykbot.py \
    --no-dry-run \
    --log-level=debug \
    --log-file=$HOME/dykbot.log
