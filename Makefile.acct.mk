# Image URL to use all building/pushing image targets
IMG ?= gsoci.azurecr.io/giantswarm/app-catalog-cleanup-tool
# ---------------------------------------------------------------------
# -- Which container tool to use
# ---------------------------------------------------------------------
CONTAINER_TOOL ?= docker

export VER ?= $(shell git describe --tags --abbrev=0 2>/dev/null || echo "0.0.0")
export COMMIT ?= $(shell git rev-parse HEAD 2>/dev/null || echo "0000000000000000000000000000000000000000")
export SHORT_COMMIT ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo "0000000")
export DATE ?= $(shell date '+%FT%T%:z')

IMG_VER ?= ${VER}-${COMMIT}

.PHONY: all release release_ver_to_code docker-build docker-build-image docker-build-ver docker-push docker-build-test test docker-test docker-test-ci

check_defined = \
    $(strip $(foreach 1,$1, \
        $(call __check_defined,$1,$(strip $(value 2)))))
__check_defined = \
    $(if $(value $1),, \
      $(error Undefined $1$(if $2, ($2))))

all: docker-build

release: release_ver_to_code docker-build-image
	git commit -am "Release ${TAG}"
	git tag ${TAG}
	mv dacct.sh.back dacct.sh
	echo "build_ver = \"${TAG}-dev\"" > app_catalog_cleanup_tool/version.py
	git commit -am "Post-release version set for ${TAG}"

release_ver_to_code:
	$(call check_defined, TAG)
	echo "build_ver = \"${TAG}\"" > app_catalog_cleanup_tool/version.py
	$(eval IMG_VER := ${TAG})
	cp dacct.sh dacct.sh.back
	bash -c 'sed -i "s/latest/$${TAG#v}/" dacct.sh'

# Build the docker image from locally built binary
docker-build: docker-build-ver docker-build-image

docker-build-image:
	$(CONTAINER_TOOL) build . -t ${IMG}:latest -t ${IMG}:${IMG_VER}

docker-build-ver:
	echo "build_ver = \"${VER}-${COMMIT}\"" > app_catalog_cleanup_tool/version.py

# Push the docker image
docker-push: docker-build
	$(CONTAINER_TOOL) push ${IMG}:${IMG_VER}

docker-build-test: docker-build
	$(CONTAINER_TOOL) build -f testrunner.Dockerfile . -t ${IMG}-test:latest

test-command = --cov app_catalog_cleanup_tool --log-cli-level info tests/
test-command-ci = --cov-report=xml $(test-command)
test-docker-args = run -it --rm -v ${PWD}/.coverage/:/acct/.coverage/
test-docker-run = $(CONTAINER_TOOL) $(test-docker-args) ${IMG}-test:latest

test:
	pipenv run python -m pytest $(test-command)

docker-test: docker-build-test
	$(test-docker-run) $(test-command)

docker-test-ci: docker-build-test
	$(test-docker-run) $(test-command-ci)
