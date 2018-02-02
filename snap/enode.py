#!/usr/bin/python3

import socket
from subprocess import check_output
import sys


DEFAULT_NETADDR = '8.8.8.8'


def autoselect_netaddr(addr=DEFAULT_NETADDR):
    addrs = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect((addr, 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l]
    if addrs:
        return addrs[0][0]
    return DEFAULT_NETADDR


if __name__ == '__main__':
    if sys.argv[1:]:
        local_netaddr = autoselect_netaddr()
    else:
        local_netaddr = sys.argv[1]
    enode = check_output(['%s/bin/attach.bash' % (os.environ['SNAP']),
                          '--exec', 'admin.nodeInfo.enode'],
                         universal_newlines=True)
    enode = re.sub(r'\[::\]', local_netaddr, enode)
    print(enode)
