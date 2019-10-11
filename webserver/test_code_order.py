"""Script to test properties on the code that the webserver submits each round.

In particular, the property that we want to achieve is that the webserver
never submits "old code".
More formally:
    There never exist a 3-tuple of round indices x, y, z, with
    0 <= x < y < z <= last_round such that code(x) == code(z) != code(y)
"""

import os
from collections import defaultdict
from hashlib import sha256
from server_util import ROUNDS_DIR, CUR_ROUND, machine2team, SOURCE_SUBDIR, SUBMIT_NAME
import json
from pprint import pprint

round_dirs = os.listdir(ROUNDS_DIR)

try:
    round_dirs.remove(CUR_ROUND)
except ValueError:
    print("cur-round already removed")

# get the maximum round number
max_round = max([int(x.split('-')[1]) for x in round_dirs])

# Go through the rounds and get a hash of the code
teamcode = defaultdict(list)
for idx in range(max_round + 1):   # Count also the last round
    mt = machine2team(idx)
    src_dir = os.path.join(ROUNDS_DIR, f"round-{idx}", SOURCE_SUBDIR)
    for cur_source in os.listdir(src_dir):
        if cur_source in mt:
            # Get the team for the current source
            team = mt[cur_source]
            # Get the file for the source
            code_path = os.path.join(src_dir, cur_source, f"{SUBMIT_NAME}.py")
            try:
                with open(code_path, 'r') as infile:
                    code = infile.read()
                hash = str(sha256(bytes(code, 'utf-8')).hexdigest())
            except FileNotFoundError:
                print(f"Round {idx} source {cur_source} NO CODE")
                hash = None
            teamcode[team].append(hash)

# Save the hashes for future use
with open('teamhashes.json', 'w') as outfile:
    json.dump(teamcode, outfile)

# Analyze the hashses
for team in teamcode:
    last_hash = None
    seen_hashes = []
    pprint(teamcode[team][:10])
    for idx, cur_hash in enumerate(teamcode[team]):
        if cur_hash != last_hash and cur_hash in teamcode[team][:idx]:
            print(f"PROBLEM for team {team} in round {idx}")
            print(f"The same code was found in pos {teamcode[team].index(cur_hash)}")
        last_hash = cur_hash


