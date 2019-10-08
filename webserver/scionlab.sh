#!/bin/bash

ProgName=$(basename $0)
SERVER="127.0.0.1:5000"


sub_help(){
    echo "Usage: $ProgName <subcommand> [options]\n"
    echo "Subcommands:"
    echo "    signup TEAM_NAME   Sign up a new time with name TEAM_NAME."
    echo "    submit FILE_NAME   Submit a new version of the code."
    echo "    logs FILE_NAME     Save the latest log to FILE_NAME"
    echo ""
}

sub_signup(){
    echo "Signing up..."
    curl $SERVER"/signup/$1"
}

sub_submit(){
    echo "Submitting: $1"
    curl "$SERVER/$TEAM_TOKEN/submit" -X POST -F "upload=@$1"
}

sub_logs(){
    echo "Getting last available log"
    curl "$SERVER/$TEAM_TOKEN/logs" > "$1"
}


sub_manage(){
    if [[ "$1" =~ ^(signup|teams|config|prepare|finish)$ ]]; then
        echo "Executing: manage $1"
        curl "$SERVER/$MAN_SECRET/$1"
    else
        echo "Error: 'manage'_'$1' is not a known subcommand." >&2
        echo "       Run '$ProgName --help' for a list of known subcommands." >&2
        exit 1
    fi
}


subcommand=$1

echo "=== BEFORE YOU RUN COMMANDS (other than signup) REMEBER TO $ export TEAM_TOKEN=<token> ==="
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
