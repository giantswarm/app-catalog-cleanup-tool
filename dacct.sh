#!/bin/sh

DACCT_TAG=${DACCT_TAG:-"0.1.2"}

docker run -it --rm \
  -e USE_UID="$(id -u "${USER}")" \
  -e USE_GID="$(id -g "${USER}")" \
  -v "$(pwd)":/acct/workdir/ \
  "quay.io/giantswarm/app-catalog-cleanup-tool:${DACCT_TAG}" "$@"
