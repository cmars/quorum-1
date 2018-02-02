#!/usr/bin/python3

import os
import sys
from subprocess import check_call, DEVNULL

if __name__ == '__main__':
    genesis_contents = sys.stdin.read()
    if not genesis_contents:
        raise Exception('empty genesis.json')
    snap = os.environ['SNAP']
    common = os.environ['SNAP_USER_COMMON']
    for d in ('quorum', 'constellation', 'ethereum'):
        os.makedirs(os.path.join(common, d), exist_ok=True)
    with open(os.path.join(common, 'quorum', 'genesis.json'), 'w') as f:
        f.write(genesis_contents)

    if not os.path.exists(os.path.join(common, 'constellation', 'node.conf')):
        check_call([os.path.join(snap, 'bin', 'constellation-config.py'), 'othernodes='],
                   stdin=DEVNULL)

    if not os.path.exists(os.path.join(common, 'constellation', 'node.pub')):
        check_call([os.path.join(snap, 'bin', 'constellation-node'),
                    '--workdir=%s' % (os.path.join(common, 'constellation')),
                    '--generatekeys=node',
                    os.path.join(common, 'constellation', 'node.conf')],
                   stdin=DEVNULL)

    sys.stdin.close()
    sys.stdin = open('/dev/null', 'r')  # Re-open stdin
    os.execl(os.path.join(snap, 'bin', 'geth'),
             '--datadir=%s' % (os.path.join(common, 'ethereum')),
             'init', os.path.join(common, 'quorum', 'genesis.json'))
