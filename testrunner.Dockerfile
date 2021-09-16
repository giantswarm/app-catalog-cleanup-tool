FROM quay.io/giantswarm/app-catalog-cleanup-tool:latest

ARG ACCT_DIR="/ats"

RUN pip install --no-cache-dir pipenv==${PIPENV_VER}
RUN apt-get update && apt-get install -y wget git xz-utils && rm -rf /var/lib/apt/lists/*
RUN wget -qO- "https://github.com/koalaman/shellcheck/releases/download/latest/shellcheck-latest.linux.x86_64.tar.xz" | tar -xJv && cp "shellcheck-latest/shellcheck" /usr/bin/
WORKDIR $ACCT_DIR
COPY .bandit .
COPY .coveragerc .
COPY .flake8 .
COPY .mypy.ini .
COPY .pre-commit-config.yaml .
COPY .markdownlintignore .
COPY .markdownlint.yaml .
COPY pyproject.toml .
COPY run-tests-in-docker.sh .
COPY setup.py .
COPY README.md .
COPY Pipfile .
COPY Pipfile.lock .
COPY tests/ tests/
COPY .git/ ./.git/
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --clear --dev
RUN pipenv run pre-commit install-hooks
ENTRYPOINT ["./run-tests-in-docker.sh"]
CMD ["--cov", "app_catalog_cleanup_tool", "--log-cli-level", "info", "tests/"]
