# -*- python -*-
# ex: set filetype=python:
"""Defines VIScon-specific configuration.

This file is imported by master.cfg to build the final buildbot config.
"""

import csv
import os
import re
from datetime import datetime

from buildbot.plugins import *
from buildbot.process.results import SUCCESS

####### CONSTANTS

ROUND_TICK  =  60  # How often we run a round, in seconds.
                   # Drives the round-tick scheduler.
PLAYER_TIME =  30  # How long the player code runs in each round, in seconds.
                   # Sets player running time.

PLAYERS = {}
SINKS   = {}
with open('../worker_to_ssh.csv') as f:
    for row in csv.reader(f):
        if row[0].startswith('source-'):
            PLAYERS[row[0]] = row[1:]
        elif row[0].startswith('sink-'):
            SINKS[row[0]] = row[1:]
        # ignore everything else

# communication with webserver
WEBSERVER_BASEURL = 'http://{}/'.format(os.environ['SERVER'])
WEBSERVER_MAN_SECRET = os.environ['MAN_SECRET']
WEBSERVER_URL = WEBSERVER_BASEURL + WEBSERVER_MAN_SECRET
# dir for sharing data with webserver
DATADIR   = os.path.join(os.getcwd(), '../../webserver/rounds/cur-round')

def webserver_dir(what, id):
    return os.path.join(DATADIR, what, id)

# communication with sinks
SINK_HTTP_PORT = 8080  # used for stats reset signalling

RUN_FILE = os.path.abspath('../RUN')

####### WORKERS

BUILDBOT_WORKERS_PASSWORD = os.environ['BUILDBOT_WORKERS_PASSWORD']

DUMMY_WORKER = 'dummy'
# The 'workers' list defines the set of recognized workers. Each element is
# a tuple of the shape (worker name, password).  The same
# worker name and password must be configured on the worker.
workers = [(p, BUILDBOT_WORKERS_PASSWORD) for p in (list(PLAYERS.keys())+list(SINKS.keys())+[DUMMY_WORKER])]


####### ROUND/SCHEDULERS

# As written in ../../README.md, a round is the following:

# 1. Prepare round
start_round_sch = schedulers.Periodic(
    name='start-round',
    periodicBuildTimer=ROUND_TICK,
    builderNames=['start-round'],
)
# 2. Run player code on source workers
run_players_sch = schedulers.Dependent(
    name='start-players',
    upstream=start_round_sch,
    builderNames=['run-player-{}'.format(i) for i in PLAYERS],
)
# 3. Collect results from sinks
collect_results_sch = schedulers.Dependent(
    name="collect-results",
    upstream=run_players_sch,
    builderNames=['collect-results-{}'.format(i) for i in SINKS],
)

# 4. Finish round
finish_round_sch = schedulers.Dependent(
    name="finish-round",
    upstream=collect_results_sch,
    builderNames=['finish-round'],
)

schedulers = [
    start_round_sch,
    run_players_sch,
    collect_results_sch,
    finish_round_sch,
]

####### BUILDERS

# The 'builders' list defines the Builders, which tell Buildbot how to perform a build:
# what steps, and which workers can execute them.  Note that any particular build will
# only take place on one worker.

builders = []

#### 1. Prepare round

start_round_factory = util.BuildFactory()
start_round_factory.addStep(steps.FileExists(file=RUN_FILE))  # only run if we're enabled
start_round_factory.addStep(steps.GET(WEBSERVER_URL+'/prepare'))

builders += [util.BuilderConfig(
    name="start-round",
    factory=start_round_factory,
    workernames=[DUMMY_WORKER],
)]

#### 2. Run players

def player_factory_factory(player_id):
    player_factory = util.BuildFactory()

    src_addr = PLAYERS[player_id][0]
    src_name = player_id[len('source-'):]
    nowstr     = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    source_dir = webserver_dir('source', src_addr)
    task_file  = os.path.join(source_dir, 'round.txt')
    code_file  = os.path.join(source_dir, 'submit.py')
    log_file   = os.path.join(source_dir, 'log')  # why not at least output.log or something
    run_cmd    = ['sh', '-c', 'python3 ./submit.py < ./round.txt >> ./output.log 2>&1 || true']  # :D

    # 1. put the task file and user's code on the worker
    player_factory.addStep(steps.FileDownload(mastersrc=task_file,
                                              workerdest='./round.txt'))
    player_factory.addStep(steps.FileDownload(mastersrc=code_file,
                                              workerdest='./submit.py'))
    loghdr = '# running on: {} ({})\n'.format(src_addr, src_name)
    player_factory.addStep(steps.StringDownload(loghdr,
                                                workerdest="output.log"))



    # 2. run it
    # player_factory.addStep(steps.ShellCommand(command=['cp']+API_FILES+['.']))
    player_factory.addStep(steps.ShellCommand(command=run_cmd,
                                              maxTime=PLAYER_TIME,
                                              sigtermTime=1,
                                              logfiles={'userout': './output.log'},
                                              decodeRC={i: SUCCESS for i in range(-256,256)}))
    # 3. give the code's output back to the users
    player_factory.addStep(steps.FileUpload(workersrc='./output.log',
                                            masterdest=log_file))
    return player_factory

builders += [
    util.BuilderConfig(
        name="run-player-{}".format(player_id),
        workernames=[player_id],
        factory=player_factory_factory(player_id))
    for player_id in PLAYERS
]

#### 3. Collect results

def collect_results_factory_factory(sink_id):
    results_factory = util.BuildFactory()
    sink_dir = webserver_dir('sink', SINKS[sink_id][0])
    sink_file = os.path.join(sink_dir, 'scores.txt')

    # I don't really want to do the POST from master, because then that would
    # require it to be network-accessible and I'm not sure if that's a good
    # idea given that the participants have access to the network and we don't
    # have any auth :D So... fuck it, gonna curl from localhost :D
    # results_factory.addStep(steps.POST())
    http_cmd = ['curl', '-X', 'POST', 'http://localhost:{}/'.format(SINK_HTTP_PORT)]
    results_factory.addStep(steps.ShellCommand(command=http_cmd))
    results_factory.addStep(steps.FileUpload(workersrc='/tmp/scores.txt',
                                            masterdest=sink_file))
    return results_factory

builders += [
    util.BuilderConfig(
        name="collect-results-{}".format(sink_id),
        workernames=[sink_id],
        factory=collect_results_factory_factory(sink_id))
    for sink_id in SINKS
]

#### 4. Finish round

finish_round_factory = util.BuildFactory()
finish_round_factory.addStep(steps.GET(WEBSERVER_URL+'/finish'))

builders += [util.BuilderConfig(
    name="finish-round",
    workernames=[DUMMY_WORKER],
    factory=finish_round_factory,
)]


####### WEB INTERFACE

# Web interface settings: host, port, and title.
# The 'title' string will appear at the top of this buildbot installation's
# home pages (linked to the 'titleURL').
port        = 8010
buildbotURL = "http://localhost:{}/".format(port)
titleURL    = buildbotURL
title       = "SCIONLab Workshop"
