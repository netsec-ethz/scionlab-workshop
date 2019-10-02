"""Utilities for the management of webserver directories."""
import csv
import datetime
import os
import re
import shutil
from collections import defaultdict
from hashlib import sha256
from shutil import rmtree, copyfile

from influxdb import InfluxDBClient

from gen_configs import read_addr
from scoring.score_run import load_goals, score_run

NUM_ROUNDS = 100
DST_PER_ROUND = 3

# Directory structure
TEAMS_DIR = "teams/"
ROUNDS_DIR = "rounds/"
CONFIGS_DIR = "configs/"
INFRASTRUCTURE_DIR = "infrastructure/"
SOURCE_SUBDIR = "source/"
SINK_SUBDIR = "sink/"
LOGS_SUBDIR = "logs/"
CODE_SUBDIR = "code/"
CUR_ROUND = "cur-round"
SUBMIT_NAME = "submit"
SCORE_FILE = "scores.txt"
ROUND_CONFIG = "round.txt"
# Default messages
DEFAULT_PY = "# This is the default blank python script.\nprint('You " \
             "have not provided a valid submission yet!')\n"
NULL_CODE = "print('Default code to make buildbot happy')\n"

LOGNAME = "log"

TEAMS = os.path.join(CONFIGS_DIR, "teams_ids.csv")
SOURCES = os.path.join(INFRASTRUCTURE_DIR, "src_addr.csv")
DESTINATIONS = os.path.join(INFRASTRUCTURE_DIR, "dst_addr.csv")
CUR_ROUND_DIR = os.path.join(ROUNDS_DIR, CUR_ROUND)

SECRET = os.getenv('SECRET', default="")

INFLUX_USER = os.getenv("INFLUX_USER")
INFLUX_PWD = os.getenv("INFLUX_PWD")
INFLUX_DB = os.getenv("INFLUX_DB")
INFLUX_ADDR = os.getenv("INFLUX_ADDR")


def team_id(instring, length=6):
    return str(sha256(bytes(instring + SECRET, 'ascii')).hexdigest())[:length]


def valid_teamname(teamname):
    if re.match(r'[\w]+$', teamname):
        return True
    return False


def teams_from_dir():
    """Read all the team names from the folders and generate team IDs."""
    teams = os.listdir(TEAMS_DIR)
    team_ids = dict(zip(list(map(team_id, teams)), teams))
    return teams, team_ids


def cleanup_dir(dir):
    """Remove all the contents in the directory"""
    if os.path.exists(dir):
        rmtree(dir)
    os.makedirs(dir)


def most_recent_timestamp(dir):
    """Returns the file with the most recent timestamp in the directory."""
    most_recent = datetime.datetime.min
    file = None
    for cur in os.listdir(dir):
        timestr = cur.split("-", maxsplit=1)[0]
        cur_time = datetime.datetime.strptime(timestr, '%y%m%d%H%M%S')
        if cur_time > most_recent:
            most_recent = cur_time
            file = cur
    return file


def check_teamid(teamid, team_ids):
    if teamid in team_ids:
        return True
    return False


def prepare_round():
    """Put the most recent code for each team in the appropriate folder.

    Round numbers start from 0.
    """
    last_round = get_last_round_num()
    cur_round = last_round + 1

    # Populate the cur-round folder with source/ and sink/ folders
    if os.path.exists(CUR_ROUND_DIR):
        print(">> PREPARE ALREADY CALLED, REMOVING AND RE-PREPARING")
        shutil.rmtree(CUR_ROUND_DIR)
    os.mkdir(CUR_ROUND_DIR)
    os.mkdir(os.path.join(CUR_ROUND_DIR, "source"))
    os.mkdir(os.path.join(CUR_ROUND_DIR, "sink"))

    # Get the config with the teamname-source mappings.
    all_sources, _ = read_addr(SOURCES)
    config_name = os.path.join(CONFIGS_DIR, f"config_round_{cur_round}.csv")
    with open(config_name, 'r') as infile:
        reader = csv.reader(infile)
        for row in reader:
            move_code_to_source(row[0], row[1])
            _prepare_config_run(row[1], row[2], row[3])
            try:
                all_sources.remove(row[1])  # Remove the machine from the list
            except ValueError:
                print("Machine already considered")
    for leftover in all_sources:
        _create_empty_entry(leftover)


def _prepare_config_run(src, dst, nbytes):
    config_file = os.path.join(CUR_ROUND_DIR, SOURCE_SUBDIR, src, ROUND_CONFIG)
    if os.path.exists(config_file):
        with open(config_file, 'a') as outfile:
            outfile.write(f"{dst} {nbytes}\n")
    else:
        with open(config_file, 'w') as outfile:
            outfile.write(f"{dst} {nbytes}\n")


def _create_empty_entry(source):
    """Create an empty file in the 'source' folder"""
    if not os.path.exists(os.path.join(CUR_ROUND_DIR,
                                       SOURCE_SUBDIR,
                                       source)):
        os.makedirs(os.path.join(CUR_ROUND_DIR,
                                 SOURCE_SUBDIR,
                                 source))

    dst = os.path.join(CUR_ROUND_DIR,
                       SOURCE_SUBDIR,
                       source,
                       f"{SUBMIT_NAME}.py")
    with open(dst, 'w') as outfile:
        outfile.write(NULL_CODE)

    dst = os.path.join(CUR_ROUND_DIR,
                       SOURCE_SUBDIR,
                       source,
                       f"{ROUND_CONFIG}")
    with open(dst, 'w') as outfile:
        outfile.write("\n")


def move_code_to_source(teamname, source):
    """Copy the most recently submitted code to the appropriate source dir.

    The sumbmitted code for a team will then be:

        ./rounds/cur-round/source/<source machine addr>/<teamname>.py

    The <teamname>.py file is the runnable file.
    """
    team_code_dir = os.path.join(TEAMS_DIR, teamname, CODE_SUBDIR)
    recent_code = most_recent_timestamp(team_code_dir)
    if recent_code is not None:
        # Copy the file over to the appropriate source
        if not os.path.exists(os.path.join(CUR_ROUND_DIR,
                                           SOURCE_SUBDIR,
                                           source)):
            os.makedirs(os.path.join(CUR_ROUND_DIR, SOURCE_SUBDIR, source))
        dst = os.path.join(CUR_ROUND_DIR,
                           SOURCE_SUBDIR,
                           source,
                           f"{SUBMIT_NAME}.py")
        copyfile(os.path.join(team_code_dir, recent_code), dst)


def get_last_round_num():
    round_names = os.listdir(ROUNDS_DIR)
    if not round_names:
        return -1
    cur_max = -1
    for name in round_names:
        if name != "cur-round":
            print(name)
            round_num = int(name.split("-")[1])  # Round folders  `round-N`
            cur_max = max(cur_max, round_num)
    return cur_max


def finish_round():
    """Clean up the folders at the end of the round.

    After round N, the cur-round folder is renamed to round-N.
    """
    last_round = get_last_round_num()
    cur_round = last_round + 1
    round_dir = os.path.join("rounds", f"round-{cur_round}")
    os.rename(CUR_ROUND_DIR, round_dir)

    timestamp = datetime.datetime.now().strftime("%y%m%d%H%M%S")

    # Keep only the machines that actually have a team assigned
    machine_team = machine2team(cur_round)
    for cur_src, cur_team in machine_team.items():
        log_name = f"{timestamp}_log"
        dst_path = os.path.join(TEAMS_DIR, cur_team, LOGS_SUBDIR, log_name)
        copyfile(os.path.join(round_dir, SOURCE_SUBDIR, cur_src, LOGNAME),
                 dst_path)
    # Gather the scores
    sink_dir = os.path.join(round_dir, SINK_SUBDIR)
    results = defaultdict(dict)
    for cur_sink in os.listdir(sink_dir):
        with open(os.path.join(sink_dir, cur_sink, SCORE_FILE), 'r') as infile:
            reader = csv.reader(infile, delimiter='\t')
            for line in reader:
                # results: (src, dst, bytes)
                results[line[0]][cur_sink] = int(line[1])

    # Scores
    goals, src2team = load_goals(os.path.join(CONFIGS_DIR,
                                              f"config_round_{cur_round}.csv"))
    scores = score_run(goals, results)
    # If there is no src entry in the scores, set the score to zero
    teamscores = {team: scores[src] if src in scores else 0 for src, team in
                  src2team.items()}
    print(teamscores)
    # Send scores to influx
    _push_to_influxdb(teamscores, cur_round)
    return "Round finished and scores pushed"


def machine2team(cur_round):
    """Compute the map from teams to machines."""
    # Get the config with the teamname-source mappings.
    config_name = f"configs/config_round_{cur_round}.csv"
    machine_team = {}
    with open(config_name, 'r') as infile:
        reader = csv.reader(infile)
        for row in reader:
            machine_team[row[1]] = row[0]
    return machine_team


def _push_to_influxdb(teamscores, round_n):
    points = _create_point_list(teamscores, round_n)
    client = InfluxDBClient(INFLUX_ADDR, 8086, INFLUX_USER, INFLUX_PWD,
                            INFLUX_DB)
    client.write_points(points)


def _create_point_list(teamscores, round_n):
    timestamp = f"{datetime.datetime.now().utcnow()}"
    points = []
    for team, score in teamscores.items():
        points.append(
            {
                "measurement": "score",
                "tags": {
                    "team": team,
                    "round": round_n
                },
                "time": timestamp,
                "fields": {
                    "value": score
                }
            }
        )
    return points
