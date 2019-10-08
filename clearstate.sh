#!/bin/sh

for d in master webserver; do
    echo "=== Clearing $d ==="
    (cd $d; ./clearstate.sh)
done
