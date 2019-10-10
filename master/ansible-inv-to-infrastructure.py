#!/usr/bin/env python3

import collections
import copy
import numbers
import sys
import yaml

SCIONLAB_FUN_THROUGHPUT = 50e6  # Mbps
PLAYER_TIME = 30  # seconds
BW_FACTOR_RANGE = 10

def bytes_for_dest(bw_factor):
    return int(SCIONLAB_FUN_THROUGHPUT * PLAYER_TIME * bw_factor / (8 * BW_FACTOR_RANGE))

SINK_SERVER_PORT = 12345

SSH_USER = 'runner'

WITH_DUMMY = True
DUMMY_SSH_USER = 'ubuntu'
DUMMY_HOST = 'viscon-netsec-eosmd7'

def find_hosts(inv):
    for k, v in inv.items():
        if k == 'hosts':
            for name, data in v.items():
                yield (name, data)
        else:
            for h in find_hosts(v): yield h
def DEBUG(*args):
    print('*** DEBUG:', *args, file=sys.stderr)

def inv_to_infra(inv):
    """Generates source and sink infrastructure files for the webserver."""
    src_addr_sz   = {}  # source node SCION address => bandwidth factor
    dst_addr_sz   = {}  # sink node SCION address   => bandwidth factor
    worker_to_ssh = {}  # source node SCION address => user@hostname
    for name, data in find_hosts(inv):
        if WITH_DUMMY and name == DUMMY_HOST:
            worker_to_ssh['dummy'] = (None, '{}@{}'.format(DUMMY_SSH_USER, data['ansible_host']))
            continue
        public_ip = data['ansible_host']
        scion_local_addr = data.get('scion_local_address', public_ip)
        scion_addr = '{},[{}]'.format(data['scion_ia'], scion_local_addr)
        # bw_factor  = data['link_quality_to_next_hop_trust']
        # I don't actually think the scaling is a good idea -- I trust
        # randomness more than this :D so I'll hardcode something
        bw_factor = 10
        # I don't want to think, so let's just put both sources and sinks
        # everywhere :D
        src_addr_sz[scion_addr] = bytes_for_dest(bw_factor)
        dst_addr_sz[scion_addr] = bytes_for_dest(bw_factor)
        worker_to_ssh['source-'+name] = (scion_addr, '{}@{}'.format(SSH_USER, public_ip))
        worker_to_ssh['sink-'+name]   = (scion_addr, '{}@{}'.format(SSH_USER, public_ip))

    return src_addr_sz, dst_addr_sz, worker_to_ssh

def poor_mans_csv(data, filename, print_info=True):
    def fmt(x):
        if isinstance(x, numbers.Number): return str(x)
        return '"{}"'.format(x)

    with open(filename, 'w') as f:
        for row in data:
            print(','.join(fmt(x) for x in row), file=f)
    if print_info:
        print('Wrote file {}'.format(filename), file=sys.stderr)

def main():
    inv = yaml.safe_load(sys.stdin.read())
    src_addr, dst_addr, worker_to_ssh = inv_to_infra(inv)

    poor_mans_csv(src_addr.items(),    'src_addr.csv')
    poor_mans_csv(dst_addr.items(),    'dst_addr.csv')
    poor_mans_csv([(a,n,v) for (a,(n,v)) in worker_to_ssh.items()], 'worker_to_ssh.csv')

if __name__ == '__main__':
    main()
