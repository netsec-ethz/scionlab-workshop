"""Webserver to handle teams and file submissions"""

import csv
import datetime
import os
from hashlib import sha256

from flask import Flask
from flask import request, send_file
from gen_configs import read_teamnames, read_src_addr, read_dst_addr, \
    generate_all_configs, write_configs

app = Flask(__name__)

SECRET = "NEXT RETREAT IN SINGAPORE"
app.sign_up = False  # The platform allows signup
teams = []
team_ids = {}


@app.route('/')
def hello():
    return "SCION-Lab workshop at VISCON!"


def team_id(instring, length=6):
    return str(sha256(bytes(instring + SECRET, 'ascii')).hexdigest())[:length]


@app.route('/signup/<teamname>', methods=['GET'])
def signup(teamname):
    if not app.sign_up:
        return "Sorry, signing up is now disabled."
    if teamname in teams:
        return "Sorry, this name is already in use."
    new_team_id = team_id(teamname)
    app.logger.info(f"New team {teamname} signed up! ID: {new_team_id}")
    team_ids[new_team_id] = teamname
    teams.append(teamname)
    # Create team folder
    os.mkdir(f"teams/{new_team_id}")
    os.mkdir(f"teams/{new_team_id}/code")
    os.mkdir(f"teams/{new_team_id}/logs")
    return f"Welcome, {teamname}! Your ID is {new_team_id}"


@app.route('/<teamid>/submit', methods=['POST'])
def submit(teamid):
    if _check_teamid(teamid):
        app.logger.info(f"Submission from {teamid}")
        submitted = request.files['upload']
        # Save the submitted file to the appropriate folder
        fnm = submitted.filename
        out_name = datetime.datetime.now().strftime("%y%m%d%H%M%S") + f"-{fnm}"
        submitted.save(f"teams/{teamid}/code/{out_name}")
        return "You successfully submitted the code!"
    return "Team ID not recognized. Please check it or sign up."


@app.route('/<teamid>/logs', methods=['GET'])
def get_logs(teamid):
    if _check_teamid(teamid):
        app.logger.info(f"Checking logs from {teamid}")
        log = _most_recent_log(teamid)
        if log:
            return send_file(f"teams/{teamid}/logs/{log}", as_attachment=True)
        else:
            return "No logs found, sorry."
    return "Team ID not recognized. Please check it or sign up."


def _most_recent_log(teamid):
    logdir = f"teams/{teamid}/logs"
    most_recent = datetime.datetime.min
    log = None
    for cur in os.listdir(logdir):
        timestr = cur.split("-", maxsplit=1)[0]
        cur_time = datetime.datetime.strptime(timestr, '%y%m%d%H%M%S')
        if cur_time > most_recent:
            most_recent = cur_time
            log = cur
    return log


def _check_teamid(teamid):
    if teamid in team_ids:
        return True
    return False


# Management commands
MAN_SECRET = team_id("GO SCIONLAB", length=16)
ROUNDS = 2
DST_PER_ROUND = 3
TEAMS = "teams/teams_ids.csv"
SOURCES = "infrastructure/src_addr"
DESTINATIONS = "infrastructure/dst_addr.csv"
CONFIGS = "configs/"


@app.route("/manage")
def get_management_token():
    print(f"The management secret is {MAN_SECRET}")
    return f"This page is for management only"


@app.route(f"/{MAN_SECRET}/teams")
def get_teams():
    teams_str = "\n"
    for id, team in team_ids.items():
        teams_str += "{:<20} {:>10}\n".format(team, id)
    teams_str += "\n"
    print(teams_str)
    with open("teams/teams_ids.csv", 'w') as outfile:
        writer = csv.writer(outfile)
        for id, team in team_ids.items():
            writer.writerow([team, id])
    return teams_str


@app.route(f"/{MAN_SECRET}/signup")
def toggle_signup():
    if app.sign_up:
        app.sign_up = False
        return "SIGNUP is now DISABLED"
    else:
        app.sign_up = True
        return "SIGNUP is now ENABLED"


@app.route(f"/{MAN_SECRET}/config")
def generate_configs():
    teams, team_ids = read_teamnames(TEAMS)
    src_addr = read_src_addr(SOURCES)
    dst_addr, msg_size = read_dst_addr(DESTINATIONS)

    print("There are:")
    print(f"   - {len(teams)} teams;")
    print(f"   - {len(src_addr)} source addresses;")
    print(f"   - {len(dst_addr)} destination (sink) addresses;")
    print(f"   - {DST_PER_ROUND} destinations for each team, each round;")
    print(f"   - {ROUNDS} rounds to be played.")
    print(f"The output will be saved in {CONFIGS}.")

    if len(teams) > len(src_addr):
        raise ValueError("There are more teams than source IPs!")

    confs = generate_all_configs(ROUNDS, teams, src_addr, dst_addr,
                                 msg_size, DST_PER_ROUND)
    write_configs(confs, CONFIGS)
    return "Configs written"


if __name__ == '__main__':
    app.run()
