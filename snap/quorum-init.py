#!/usr/bin/python3

import json
import os
import socket
import sys
from subprocess import check_call, check_output, DEVNULL


DEFAULT_NETADDR = '8.8.8.8'


def autoselect_netaddr(addr=DEFAULT_NETADDR):
    addrs = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect((addr, 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l]
    if addrs:
        return addrs[0][0]
    return DEFAULT_NETADDR


if __name__ == '__main__':
    snap = os.environ['SNAP']
    common = os.environ['SNAP_USER_COMMON']
    for d in ('quorum', 'constellation', 'ethereum'):
        os.makedirs(os.path.join(common, d), exist_ok=True)

    # Read ethereum genesis configuration from stdin, unless its
    # already been put in place ahead of time.
    if not os.path.exists(os.path.join(common, 'quorum', 'genesis.json')):
        genesis_contents = sys.stdin.read()
        if not genesis_contents:
            raise Exception('empty genesis.json')
        with open(os.path.join(common, 'quorum', 'genesis.json'), 'w') as f:
            f.write(genesis_contents)

    # Generate constellation config file
    if not os.path.exists(os.path.join(common, 'constellation', 'node.conf')):
        check_call([os.path.join(snap, 'bin', 'constellation-config.py'), 'othernodes='],
                   stdin=DEVNULL)

    # Generate constellation key pair
    if not os.path.exists(os.path.join(common, 'constellation', 'node.pub')):
        check_call([os.path.join(snap, 'bin', 'constellation-node'),
                    '--workdir=%s' % (os.path.join(common, 'constellation')),
                    '--generatekeys=node',
                    os.path.join(common, 'constellation', 'node.conf')],
                   stdin=DEVNULL)

    # Initialize ethereum with the genesis configuration
    check_call([os.path.join(snap, 'bin', 'geth'),
                '--datadir=%s' % (os.path.join(common, 'ethereum')),
                'init', os.path.join(common, 'quorum', 'genesis.json')])

    # Write networkid for later use on command line
    with open(os.path.join(common, 'quorum', 'genesis.json')) as f:
        g = json.load(f)
        networkid = g.get('config', {}).get('chainId', 2017)
    with open(os.path.join(common, 'quorum', 'networkid'), 'w') as f:
        f.write(networkid)

    # Write bootnodes for later use on command line
    bootnodes = sys.argv[1:]
    if bootnodes:
        with open(os.path.join(common, 'quorum', 'bootnodes'), 'w') as f:
            f.write(" ".join([bootnode.strip() for bootnode in bootnodes]))
    else:
        print("WARNING: no bootnodes specified; your node will not automatically connect to a quorum!")
