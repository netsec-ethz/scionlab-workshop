# SCIONLab path control game

This repo contains the infrastructure, API, and example code for the SCION path control game/workshop/hackathon/thingy for VIScon 2019.

The aim of the workshop is to enable participants to program bots that make use of SCION path control (path selection and multipath) and send data across the real planet-wide SCIONLab network.

Users write code that uses a simplified SCION paths API. This code is then run on a randomly chosen machine in the SCIONLab network. The code's task is to send data to assigned *sink machines* within the given time frame. The user machine's address, sink addresses, and required amounts of data are provided on standard input. We run a number of **rounds** (with randomised assignments), and users may view logs from previous runs and improve their algorithm to do better in the next rounds.

How this works:

* The front-end **webserver** provides the interface for users (participants).
  * Users upload their code here, and get logs and results from here.
  * Code lives in `webserver/`.
* The **master** takes care of running the user code on worker machines and collecting results from the sinks.
  * Code lives in `master/`.
* We need to **generate the assignments and score the results** for each round.
  * Code lives in `webserver/scoring/`.
* The webserver pushes the scores into InfluxDB, and a **dashboard** is used to display them. 
  * This does not live in this repository.

# Documentation

Detailed documentation lives in [the wiki](https://github.com/netsec-ethz/scionlab-workshop/wiki/).
