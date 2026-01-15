FROM gsoci.azurecr.io/giantswarm/app-catalog-cleanup-tool:latest

ARG ACCT_DIR="/acct"

# Install uv - pinned to specific version for security (already in base image but ensure it's available)
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

RUN apt-get update && apt-get install -y wget git xz-utils libatomic1 && rm -rf /var/lib/apt/lists/*
# Pin shellcheck to specific version for security and reproducibility
ARG SHELLCHECK_VERSION=v0.10.0
RUN wget -qO- "https://github.com/koalaman/shellcheck/releases/download/${SHELLCHECK_VERSION}/shellcheck-${SHELLCHECK_VERSION}.linux.x86_64.tar.xz" | tar -xJv && \
    cp "shellcheck-${SHELLCHECK_VERSION}/shellcheck" /usr/bin/ && \
    shellcheck --version
WORKDIR $ACCT_DIR
COPY .bandit .
COPY .coveragerc .
COPY .flake8 .
COPY .mypy.ini .
COPY .pre-commit-config.yaml .
COPY .markdownlintignore .
COPY .markdownlint.yaml .
COPY pyproject.toml .
COPY uv.lock .
COPY run-tests-in-docker.sh .
COPY README.md .
COPY tests/ tests/
RUN git init && git config --global --add safe.directory /acct
RUN uv sync --frozen
RUN uv run pre-commit run -a
ENTRYPOINT ["./run-tests-in-docker.sh"]
CMD ["--cov", "app_catalog_cleanup_tool", "--log-cli-level", "info", "tests/"]
