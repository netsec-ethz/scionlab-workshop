#!/bin/sh

set -e

RUNFILE='./RUN'

if [ -f $RUNFILE ]; then
    rm $RUNFILE
    echo 'RUN OFF'
    pipenv run buildbot reconfig buildbot-master
else
    touch $RUNFILE
    echo 'RUN ON'
    pipenv run buildbot reconfig buildbot-master
fi
