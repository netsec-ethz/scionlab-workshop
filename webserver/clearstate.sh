#!/bin/sh

DATADIRS='teams configs rounds'
echo '* Removing all contest data'
rm -rf $DATADIRS
mkdir $DATADIRS
