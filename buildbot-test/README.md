TODO this half of this README should actually be in the top-level README.

SCION path control workshop: write code that makes use of SCION paths (path selection and multipath) and sends data across the real planet-wide SCIONLab network.

Users write code that uses a simplified SCION paths API. This code is then run on a randomly chosen machine in the SCIONLab network. The code's task is to send data to assigned *sink machines* within the given time frame. The user machine's address, sink addresses, and required amounts of data are provided on standard input. We run a number of **rounds** (with randomised assignments), and users may view logs from previous runs and improve their algorithm to do better in the next rounds.

How this works:

* A front-end **webserver** provides the user interface for users.
  * Users upload their code here, and get logs and results from here.
  * Code lives in `webserver/`.
* An **orchestrator** takes care of running the user code on machines and collecting results from the sinks.
  * Code lives in `orchestrator/`.
* We need to generate the assignments and score the results for each round.
  * Code lives in `scoring/`.

-----------

not toplevel readme starting from here

We use [Buildbot](https://docs.buildbot.net/current/tutorial/firstrun.html) to coordinate running the player code on source machines and collecting results from sink machines.

The basic idea is:

* The user-facing **webserver** handles the mapping of teams to sources and sinks.
  * Round configuration, such as assignment of teams to sources and sinks, is handled there.
  * The code lives in `../webserver`.
* The **buildmaster** talks to the webserver, as well as to the source and sink machines, and coordinates things.
  * We only know about sources and sinks, not about teams.
  * VIScon-specific config is in `master/master/viscon.py`. This is loaded by
    the raw buildmaster configuration in `master/master/master.cfg`.
* Every source and sink machine is handled by a **buildbot worker**. The buildmaster config tells them what to do.
* The job of this buildbot is to run one **round** every `$ROUND_TICK` seconds.

A **round** is the following:
 1. Prepare round: tell webserver to prepare the files and wait for 200 OK.
 2. Run players: for each source worker, download the player code from webserver to worker, run it, and collect logs.
 3. Collect results: for each sink worker, send a HTTP POST to create stats file and reset stats, and upload the result to webserver.
 4. Finish round: tell webserver to process and clean up the round files.
