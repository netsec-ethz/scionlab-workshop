We use [Buildbot](https://docs.buildbot.net/current/tutorial/firstrun.html) to coordinate running the player code on source machines and collecting results from sink machines.

The basic idea is:

* The user-facing **webserver** handles the mapping of teams to sources and sinks.
  * Round configuration, such as assignment of teams to sources and sinks, is handled there.
  * The code lives in `../webserver`.
* The **buildmaster** (i.e. the code in this directory) talks to the webserver, as well as to the source and sink machines, and coordinates things.
  * We only know about sources and sinks, not about teams.
  * VIScon-specific config is in `./buildbot-master/viscon.py`. This is loaded by
    the raw buildmaster configuration in `./buildbot-master/master.cfg`.  
    You probably want to edit `viscon.py`.
* Every source and sink machine is handled by a **buildbot worker**. The buildmaster config tells them what to do, they just need to connect to the buildmaster and no further configuration is necessary.
  * The environment must be set up to be able to run the user code: in particular, the SCION installation and the Python API must be available. We handle this via the `viscon` playbook in the SCIONLab Ansible repo.
* The job of this buildbot is to run one **round** every `$ROUND_TICK` seconds.

A **round** is the following:
 1. Prepare round: tell webserver to prepare the files by `HTTP GET /prepare` and wait for 200 OK.
 2. Run players: for each source worker, download the player code from webserver to worker, run it, and collect logs.
 3. Collect results: for each sink worker, send an `HTTP POST /` to create stats file and reset stats, and upload the results file to webserver.
 4. Finish round: tell webserver to process and clean up the round files by `HTTP GET /finish` and wait for 200 OK.

The rounds are scheduled to run periodically: the settings are in `./buildbot-master/viscon.py`.

A known bug of the current implementation is that the rounds are completely independent, and thus if the timing is tight, a new round can be triggered before the previous one finished, which will mess up the state on the webserver and thus the round won't run correctly. Issue #
