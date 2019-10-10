#!/bin/sh

pipenv run buildbot stop buildbot-master

echo '* Removing and re-creating the buildmaster database'
rm -f buildbot-master/state.sqlite
rm -f RUN
pipenv run buildbot upgrade-master buildbot-master

pipenv run buildbot start buildbot-master
