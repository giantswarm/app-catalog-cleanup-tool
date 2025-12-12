FROM python:3.12.6-slim AS base

ENV LANG=C.UTF-8 \
  LC_ALL=C.UTF-8 \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONFAULTHANDLER=1 \
  ACCT_DIR="/acct"

# Install uv - pinned to specific version for security
COPY --from=ghcr.io/astral-sh/uv:0.5.18 /uv /uvx /bin/

WORKDIR $ACCT_DIR


FROM base as builder

# pip prerequesties
RUN apt-get update && \
  apt-get install --no-install-recommends -y gcc && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-install-project


FROM base

ENV USE_UID=0 \
  USE_GID=0 \
  PATH="${ACCT_DIR}/.venv/bin:$PATH" \
  PYTHONPATH=$ACCT_DIR

# install dependencies
RUN apt-get update && \
  apt-get install --no-install-recommends -y sudo && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=builder ${ACCT_DIR}/.venv ${ACCT_DIR}/.venv

COPY app_catalog_cleanup_tool/ ${ACCT_DIR}/app_catalog_cleanup_tool/

COPY container-entrypoint.sh /usr/bin
RUN chmod +x /usr/bin/container-entrypoint.sh

WORKDIR $ACCT_DIR/workdir

# we assume the user will be using UID==1000 and GID=1000; if that's not true, we'll run `chown`
# in the container's startup script
RUN chown -R 1000:1000 $ACCT_DIR

ENTRYPOINT ["container-entrypoint.sh"]

CMD ["-h"]
