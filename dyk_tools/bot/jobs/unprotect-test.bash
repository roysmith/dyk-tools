#!/usr/bin/bash

source $HOME/www/python/venv/bin/activate

PYWIKIBOT_DIR=/data/project/dyk-tools/www/python/pywikibot/DYKToolsAdminBot \
dykbot \
    --no-dry-run \
    --mylang=test \
    --log-level=info \
    --log-file=$HOME/dykbot.log \
    --basedir=$HOME/www/python \
    unprotect
