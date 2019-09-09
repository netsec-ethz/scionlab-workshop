#!/bin/sh

PLAYERS="p1 p2"
SINKS="s1 s2"

for i in $PLAYERS; do
    buildbot-worker create-worker player-$i localhost player-$i pass
done
for i in $SINKS; do
    buildbot-worker create-worker sink-$i localhost sink-$i pass
done
