#!/usr/bin/python3

import os
import sys

from jinja2 import Template
import yaml


CONFIG_KEYS = set([
    'url',
    'port',
    'othernodes',
])

DEFAULT_CONFIG = {
    'url': 'https://localhost:9000',
    'port': '9000',
    'othernodes': '',
}

TEMPLATE = r"""
# Externally accessible URL for this node (this is what's advertised)
url = "{{ url }}"

# Port to listen on for the public API
port = {{ port }}

# Socket file to use for the private API / IPC
socket = "{{ constellation_path }}/node.ipc"

# Initial (not necessarily complete) list of other nodes in the network.
# Constellation will automatically connect to other nodes not in this list
# that are advertised by the nodes below, thus these can be considered the
# "boot nodes."
othernodes = [{% for othernode in othernodes %}{% if not loop.first %},{% endif %}"{{othernode}}"{% endfor %}]

# The set of public keys this node will host
publickeys = ["{{ constellation_path }}/node.pub"]

# The corresponding set of private keys
privatekeys = ["{{ constellation_path }}/node.key"]

# Optional comma-separated list of paths to public keys to add as recipients
# for every transaction sent through this node, e.g. for backup purposes.
# These keys must be advertised by some Constellation node on the network, i.e.
# be in a node's publickeys/privatekeys lists.
# alwayssendto = []

# Optional file containing the passwords to unlock the given privatekeys
# (one password per line -- add an empty line if one key isn't locked.)
# passwords = "passwords"

# Where to store payloads and related information
storage = "dir:{{ constellation_path }}/payloads"

# Optional IP whitelist for the public API. If unspecified/empty,
# connections from all sources will be allowed (but the private API remains
# accessible only via the IPC socket above.) To allow connections from
# localhost when a whitelist is defined, e.g. when running multiple
# Constellation nodes on the same machine, add "127.0.0.1" and "::1" to
# this list.
# ipwhitelist = ["10.0.0.1", "2001:0db8:85a3:0000:0000:8a2e:0370:7334"]

# Verbosity level (each level includes all prior levels)
#   - 0: Only fatal errors
#   - 1: Warnings
#   - 2: Informational messages
#   - 3: Debug messages
verbosity = 2

"""


def main():
    if sys.argv[1:]:
        set_config()
    else:
        get_config()


def set_config():
    kvpairs = sys.argv[1:]
    kvpairs = [[s.strip() for s in kv.split('=', 2)] for kv in kvpairs]
    cfg = load_config()
    for (k, v) in kvpairs:
        if k not in CONFIG_KEYS:
            raise Exception("unsupported config key '%s'" % (k))
        if not v:
            cfg.pop(k, None)
        else:
            cfg[k] = v
    save_config(cfg)
    update_node_cfg(cfg)


def get_config():
    cfg = load_config()
    yaml.dump(node_cfg(cfg), sys.stdout)


def load_config():
    cfgfile = config_file()
    if not os.path.exists(cfgfile):
        return DEFAULT_CONFIG.copy()
    with open(cfgfile, 'r') as f:
        return yaml.load(f)


def save_config(cfg):
    cfgfile = config_file()
    with open(cfgfile, 'w') as f:
        return yaml.dump(cfg, f)


def config_file():
    user_data = os.environ['SNAP_USER_COMMON']
    return os.path.join(user_data, 'constellation', 'constellation-config.yaml')


def node_cfg(cfg):
    if cfg.get('othernodes'):
        cfg['othernodes'] = [s.strip() for s in cfg.get('othernodes', '').split(',')]
    user_data = os.environ['SNAP_USER_COMMON']
    cfg['constellation_path'] = os.path.join(user_data, 'constellation')
    return cfg


def update_node_cfg(cfg):
    t = Template(TEMPLATE)
    result = t.render(**node_cfg(cfg))
    user_data = os.environ['SNAP_USER_COMMON']
    with open(os.path.join(user_data, 'constellation', 'node.conf'), 'w') as f:
        f.write(result)


if __name__ == '__main__':
    main()
