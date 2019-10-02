#!/bin/sh

set -e

RUNFILE='./RUN'

if [ -f $RUNFILE ]; then
    rm $RUNFILE
    echo 'RUN OFF'
else
    touch $RUNFILE
    echo 'RUN ON'
fi
