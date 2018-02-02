#!/bin/bash

set -euxo pipefail

export PRIVATE_CONFIG=${SNAP_USER_COMMON}/constellation/node.conf

exec ${SNAP}/bin/geth attach ${SNAP_USER_COMMON}/ethereum/geth.ipc "$@"
