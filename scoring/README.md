# Generating goals and scoring results

The two scripts provided:
- generate the configuration files that describe the goals each team tries to achieve;
- score the results of the competition, comparing the goals with the achieved;

## Goal generation

The configuration of the goals is carried out by `gen_configs.py`. This requires the following inputs:

1. The available addresses for the sources. They should be no less than the number of sources;
2. The available destination addresses and their goal transfer file size;
3. The names of the teams;
4. The number `R` of rounds the game will be played;
5. The number `N` of goals each team will have per round.

Each goal is composed as follows:

```
Team | sources address (team vm) | destination address (sink) | bytes to transfer
```

At each round, for `R` rounds:

1. Each team gets assigned a new, randomly chosen source address;
2. `N` destination addresses are sampled randomly for each team;
3. For each of the destination addresses, the number of bytes to tranfer is used.

To try the script, run:

```
python gen_configs.py  -t test/teams -s test/src_addr -d test/dst_addr -r 2 --out test/
```
This will generate 2 different configs for 2 rounds, and will save them in `./test/`.

## Scoring

Scoring compares the number of bytes delivered with the number of bytes expected, and returns a file reporting:

```
Team | source address (team vm) | average score
```

The average score for each round is computed as:

```
avg_score = 1/N * sum_(0<=i<N) Min(1, (delivered[i] / goal[i]))

```
