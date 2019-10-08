#!/bin/sh

# just in case
pipenv run buildbot stop buildbot-master

echo '* Removing and re-creating the buildmaster database'
rm -f buildbot-master/state.sqlite
pipenv run buildbot upgrade-master buildbot-master
