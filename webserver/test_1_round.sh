#!/usr/bin/env bash

# Before running this script, make sure you started one instance of the server

TEAM_1="97cbea"
TEAM_2="40176f"

echo "Start a test run"

./scionlab.sh manage signup

# Sign up 2 teams
echo ""
./scionlab.sh signup scionlab_team
echo ""
./scionlab.sh signup netsec_team
# Try to sign up the same team again, see that it fails
echo ""
./scionlab.sh signup netsec_team

echo ""
./scionlab.sh manage signup

echo ""
./scionlab.sh manage teams
echo ""
./scionlab.sh manage config

# Wait so that the timestamps are different
sleep 1

# Submit code for both teams
echo ""
touch fakesubmission.py
export TEAM_TOKEN=$TEAM_1
./scionlab.sh submit fakesubmission.py
echo ""
export TEAM_TOKEN=$TEAM_2
#./scionlab.sh submit fakesubmission.py

# Prepare the round
echo ""
./scionlab.sh manage prepare

echo
# Add some fake logs
for cur in ./rounds/cur-round/source/*
do
touch "$cur/log"
done

# Clear the round
./scionlab.sh manage finish

rm fakesubmission.py