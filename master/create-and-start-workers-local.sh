#!/bin/sh

WORKERS="1 2 3 10 20 30 40"
WRKDIR='/tmp/buildbot-workers/'

if [ -z "$BUILDBOT_WORKERS_PASSWORD" ]; then
	echo 'set BUILDBOT_WORKERS_PASSWORD first!' >&2
	exit 1
fi

mkdir -p "$WRKDIR"
for i in $WORKERS; do
    buildbot-worker create-worker "$WRKDIR/worker-viscon-$i" localhost "viscon-$i" "$BUILDBOT_WORKERS_PASSWORD"
    buildbot-worker start "$WRKDIR/worker-viscon-$i"
done
