#!/bin/bash

ProgName=$(basename $0)

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
    curl $SCION_ADDRESS"/signup/$1"
}

sub_submit(){
    echo "Submitting: $1"
    curl "$SCION_ADDRESS/$TEAM_TOKEN/submit" -X POST -F "upload=@$1"
}

sub_logs(){
    echo "Getting last available log"
    curl "$SCION_ADDRESS/$TEAM_TOKEN/logs" > "$1"
}

sub_manage_signup(){
    echo "Toggling signup"
    curl "$SCION_ADDRESS/$MANAGE_TOKEN/signup"
}

sub_manage_config(){
    echo "Printing configs..."
    curl "$SCION_ADDRESS/$MANAGE_TOKEN/config"
}

sub_manage_finish(){
    echo "Finishing round..."
    curl "$SCION_ADDRESS/$MANAGE_TOKEN/finish_round"
}

sub_manage_prepare(){
    echo "Preparing round..."
    curl "$SCION_ADDRESS/$MANAGE_TOKEN/prepare_round"
}

sub_manage_teams(){
    echo "Printing teams..."
    curl "$SCION_ADDRESS/$MANAGE_TOKEN/teams"
}

sub_manage(){
    curl "$SCION_ADDRESS/manage"
}

subcommand=$1

case $subcommand in
    "" | "-h" | "--help")
        sub_help
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
