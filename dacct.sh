#!/bin/sh

DACCT_TAG=${DACCT_TAG:-"latest"}

docker run -it --rm \
	-e USE_UID="$(id -u "${USER}")" \
	-e USE_GID="$(id -g "${USER}")" \
	-v "$(pwd)":/acct/workdir/ \
	"gsoci.azurecr.io/giantswarm/app-catalog-cleanup-tool:${DACCT_TAG}" "$@"
