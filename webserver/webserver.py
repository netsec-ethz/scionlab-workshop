#!/usr/bin/env python3
"""Webserver to handle teams and file submissions"""

import logging

from flask import Flask
from flask import request, send_file

from gen_configs import read_teamnames, read_addr, generate_all_configs, \
    write_configs
from server_util import *

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

app.sign_up = False  # The platform allows signup


@app.route('/')
def hello():
    return "SCION-Lab workshop at VISCON!"


@app.route('/signup/<teamname>', methods=['GET'])
def signup(teamname):
    if not valid_teamname(teamname):
        return "This is not a valid team name, please conform to the" \
               "regexp: [\\w]+$"
    if not app.sign_up:
        return "Sorry, signing up is now disabled."
    teams, team_ids = teams_from_dir()
    if teamname in teams:
        return "Sorry, this name is already in use."
    new_team_id = team_id(teamname)
    app.logger.info(f"New team '{teamname}' signed up! ID: {new_team_id}")
    # Create team folder
    base_dir = os.path.join(TEAMS_DIR, teamname)
    os.mkdir(base_dir)
    os.mkdir(os.path.join(base_dir, CODE_SUBDIR))
    os.mkdir(os.path.join(base_dir, LOGS_SUBDIR))
    # Add a 'default' script to make buildbot happy
    out_name = datetime.datetime.now().strftime("%y%m%d%H%M%S") + f"-DEFAULT.py"
    with open(os.path.join(TEAMS_DIR, teamname, CODE_SUBDIR, out_name),
              'w') as outfile:
        outfile.write(DEFAULT_PY)
    return f"Welcome, {teamname}! Your ID is {new_team_id}\n" \
        f"PLEASE REMEMBER TO $ export TEAM_TOKEN={new_team_id}"


@app.route('/<teamid>/submit', methods=['POST'])
def submit(teamid):
    _, team_ids = teams_from_dir()
    if check_teamid(teamid, team_ids):
        teamname = team_ids[teamid]
        app.logger.info(f"Submission from {teamname}")
        submitted = request.files['upload']
        # Save the submitted file to the appropriate folder
        fnm = submitted.filename
        out_name = datetime.datetime.now().strftime("%y%m%d%H%M%S") + f"-{fnm}"
        submitted.save(os.path.join(TEAMS_DIR, teamname, CODE_SUBDIR, out_name))
        return "You successfully submitted the code!"
    return "Team ID not recognized. Please check it or sign up."


@app.route('/<teamid>/logs', methods=['GET'])
def get_logs(teamid):
    _, team_ids = teams_from_dir()
    if check_teamid(teamid, team_ids):
        teamname = team_ids[teamid]
        app.logger.info(f"Checking logs from {teamname}")
        team_log_dir = os.path.join(TEAMS_DIR, teamname, LOGS_SUBDIR)
        log = most_recent_timestamp(team_log_dir)
        if log:
            return send_file(
                os.path.join(TEAMS_DIR, teamname, LOGS_SUBDIR, log),
                as_attachment=True)
        else:
            return "No logs found, sorry."
    return "Team ID not recognized. Please check it or sign up."


# Management commands
MAN_SECRET = os.getenv('MAN_SECRET')


@app.route("/manage")
def get_management_token():
    app.logger.info(f"The management secret is {MAN_SECRET}")
    return f"This page is for management only"


@app.route(f"/{MAN_SECRET}/teams")
def get_teams():
    teams, team_ids = teams_from_dir()
    teams_str = "\n"
    for id, team in zip(team_ids, teams):
        teams_str += "{:<20} {:>10}\n".format(team, id)
    teams_str += "\n"
    app.logger.info(teams_str)
    with open(TEAMS, 'w') as outfile:
        writer = csv.writer(outfile)
        for id, team in zip(team_ids, teams):
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
    src_addr, src_size = read_addr(SOURCES)
    dst_addr, dst_size = read_addr(DESTINATIONS)

    app.logger.info("There are:")
    app.logger.info(f"   - {len(teams)} teams;")
    app.logger.info(f"   - {len(src_addr)} source addresses;")
    app.logger.info(f"   - {len(dst_addr)} destination (sink) addresses;")
    app.logger.info(f"   - {DST_PER_ROUND} destinations for each team, each "
                    f"round;")
    app.logger.info(f"   - {NUM_ROUNDS} rounds to be played.")
    app.logger.info(f"The output will be saved in {CONFIGS_DIR}.")

    if len(teams) > len(src_addr):
        raise ValueError("There are more teams than source IPs!")

    confs = generate_all_configs(NUM_ROUNDS, teams, src_addr, dst_addr,
                                 src_size, dst_size, DST_PER_ROUND)
    write_configs(confs, CONFIGS_DIR)
    return "Configs written"


@app.route(f"/{MAN_SECRET}/prepare")
def prepare():
    """Prepare the round folders with the code for each machine."""
    prepare_round()
    return "Round preparation completed."


@app.route(f"/{MAN_SECRET}/finish")
def finish():
    """Clean up the round folders"""
    finish_round()
    return "Round finished."


if __name__ == '__main__':
    cleanup_dir(TEAMS_DIR)
    cleanup_dir(ROUNDS_DIR)
    cleanup_dir(CONFIGS_DIR)
    app.run(port=os.getenv('PORT', 5000), threaded=True)
