#!/usr/bin/env python3

import collections
import copy
import numbers
import sys
import yaml

SINK_SERVER_PORT = 12345

ANSIBLE_SSH_USER = 'ubuntu'  # :D

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
    src_addr_sz = {}  # source node SCION address => bandwidth factor
    dst_addr_sz = {}  # sink node SCION address   => bandwidth factor
    node_to_ssh = {}  # source node SCION address => user@hostname
    for name, data in find_hosts(inv):
        if not 'scion_ia' in data: continue  # not a SCION node, ignore
        public_ip = data['ansible_host']
        scion_local_addr = data.get('scion_local_address', public_ip)
        scion_addr = '{},[{}]'.format(data['scion_ia'], scion_local_addr)
        bw_factor  = data.get('bw_factor', 10)
        # I don't want to think, so let's just put both sources and sinks
        # everywhere :D
        src_addr_sz[scion_addr] = bw_factor
        dst_addr_sz[scion_addr] = bw_factor
        node_to_ssh[scion_addr] = '{}@{}'.format(ANSIBLE_SSH_USER, public_ip)

    return src_addr_sz, dst_addr_sz, node_to_ssh

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
    src_addr, dst_addr, node_to_ssh = inv_to_infra(inv)

    poor_mans_csv(src_addr.items(),    'src_addr.csv')
    poor_mans_csv(dst_addr.items(),    'dst_addr.csv')
    poor_mans_csv(node_to_ssh.items(), 'node_to_ssh.csv')

if __name__ == '__main__':
    main()
