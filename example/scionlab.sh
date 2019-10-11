#!/bin/bash

SERVER="http://netsec-eosmd7.inf.ethz.ch:5000"

set -e
ProgName=$(basename $0)

sub_help(){
    echo "Usage: $ProgName <subcommand> [options]\n"
    echo "Subcommands:"
    echo "    signup TEAM_NAME   Sign up a new time with name TEAM_NAME."
    echo "    submit FILE_NAME   Submit a new version of the code."
    echo "    log                Display the latest log."
    echo
}

check_team_token() {
    if [ -z $TEAM_TOKEN ]; then
        echo "=== BEFORE YOU RUN COMMANDS (other than signup) REMEBER TO $ export TEAM_TOKEN=<token> ==="
        exit 47
    fi
}

sub_signup(){
    echo "Signing up..."
    curl $SERVER"/signup/$1"
}

sub_submit(){
    check_team_token
    echo "Submitting: $1"
    curl "$SERVER/$TEAM_TOKEN/submit" -X POST -F "upload=@$1"
}

sub_log(){
    check_team_token
    curl "$SERVER/$TEAM_TOKEN/logs" --output -
}


sub_manage(){
    if [ -z $MAN_SECRET ]; then
        echo 'Set up $MAN_SECRET or go away!' >&2
        exit 47
    fi
    curl "$SERVER/$MAN_SECRET/$1"
}


subcommand=$1

case $subcommand in
    "" | "-h" | "--help")
        sub_help
        ;;

    "manage")
        shift
        sub_manage $@
        ;;

    *)
        shift
        sub_${subcommand} $@
        if [ $? = 127 ]; then
            echo "Error: '$subcommand' is not a known subcommand." >&2
            echo "       Run '$ProgName --help' for a list of known subcommands." >&2
            exit 1
        fi
        ;;
esac
