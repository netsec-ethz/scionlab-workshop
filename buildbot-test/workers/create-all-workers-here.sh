#!/bin/sh

SOURCES="p1 p2"
SINKS="s1 s2"

for i in $SOURCES; do
    buildbot-worker create-worker source-$i localhost source-$i pass
done
for i in $SINKS; do
    buildbot-worker create-worker sink-$i localhost sink-$i pass
done
