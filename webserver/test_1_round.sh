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
# Try to sign up a team name with invalid characters
echo ""
./scionlab.sh signup ..\netsec-teams

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
echo ""
./scionlab.sh manage prepare

echo ""
# Add some fake logs
for cur in ./rounds/cur-round/source/*
do
touch "$cur/log"
done

# Add some fake results
LINE=0
while IFS=, read -r col1 col2 col3 col4
do
    if (($LINE % 2 ))
    then
        echo $LINE
        mkdir rounds/cur-round/sink/$col3
        echo -e "$col2\t$col4" >> rounds/cur-round/sink/$col3/scores.txt
    fi
    LINE=$((LINE+1))
done < configs/config_round_0.csv
for i in {1..8}; do
    mkdir rounds/cur-round/sink/$(($i * 10))
    touch rounds/cur-round/sink/$((i * 10))/scores.txt
done

# Clear the round
./scionlab.sh manage finish

rm fakesubmission.py