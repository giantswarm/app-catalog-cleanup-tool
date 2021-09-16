#!/bin/sh

DACCT_TAG=${DACCT_TAG:-"0.1.1"}

  # "quay.io/giantswarm/app-build-suite:${DACCT_TAG}" "$@"
docker run -it --rm \
  -e USE_UID="$(id -u "${USER}")" \
  -e USE_GID="$(id -g "${USER}")" \
  -v "$(pwd)":/acct/workdir/ \
  "acct:${DACCT_TAG}" "$@"
