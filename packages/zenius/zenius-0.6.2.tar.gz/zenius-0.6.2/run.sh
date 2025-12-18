#!/bin/bash

set -o pipefail
set -o errexit

source .venv/bin/activate
version="$(uv version)"
if [[ -z "${version}" ]]; then
    exit 1
fi
project="$(echo "${version}" | awk '{print $1}')"

function lint       # Lint bash and project files
{
    shellcheck -xo "all" "$0"
    args=$*
    if [[ $# -eq 0 ]]; then
        args="${project}"
    fi
    ruff check --fix --select I,F,UP,B "${args}"
    ruff format "${args}"
}

function typing     # Type checking - mypy
{
    mypy --strict "$@"
}

function lsf        # List project files
{
    git ls-files "$@"
    git ls-files --exclude-standard --others "$@"
}

function clean      # Clean python cache/ lock
{
    # shellcheck disable=SC2312
    mapfile -t modules < <( lsf "$@" | grep / | cut -d/ -f1 | sort -u )
    cache_files="$(find "${modules[@]}" -name '*.pyc' -or -name '*.pyo')"
    echo "${cache_files}" | xargs rm -f
    rm -rf .mypy_cache .ruff_cache
}

function install    # Install package
{
    uv sync
}

function main       # Run all funcs
{
    clean "."
    lint "${project}"
    typing "${project}"
    install
}

function help       # Show a list of functions
{
    grep -oP "(?<=function\s).*" "$0"
}

if [[ "_$1" = "_" ]]; then
    help
else
    "$@"
fi
