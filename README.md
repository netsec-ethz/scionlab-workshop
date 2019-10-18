# SCIONLab path control game

This repo contains the infrastructure, API, and example code for the SCION path control game/workshop/hackathon/thingy for VIScon 2019.

The aim of the workshop is to enable participants to program bots that make use of SCION path control (path selection and multipath) and send data across the real planet-wide SCIONLab network.

Users write code that uses a simplified SCION paths API. This code is then run on a randomly chosen machine in the SCIONLab network. The code's task is to send data to assigned *sink machines* within the given time frame. The user machine's address, sink addresses, and required amounts of data are provided on standard input. We run a number of **rounds** (with randomised assignments), and users may view logs from previous runs and improve their algorithm to do better in the next rounds.

# How this works

Documentation lives in [the wiki](https://github.com/netsec-ethz/scionlab-workshop/wiki/). Start with [Architecture](https://github.com/netsec-ethz/scionlab-workshop/wiki/Architecture).

# Materials

* Intro slides about SCION that tell the participants enough to understand what they're doing: https://kamila.is/talking/scion/viscon19/
* Slides that explain the game itself: TODO :D
