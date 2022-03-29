#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

usage() {
    echo "Usage: $0 <conf.ini> <freeplane_doc.mm>"
    echo "  <conf.ini> is the configuration file for the Freeplane map"
    echo "  <freeplane_doc.mm> is the Freeplane map to convert"
    exit 1
}

cfile="${1:-}"
mfile="${2:-}"
test -z "${cfile}" && usage
test -z "${mfile}" && usage

conf=$(readlink -f "$1")
mindmap="$(readlink -f "$2")"
test -f "$mindmap" || usage
test -f "$conf" || usage
test "${conf##*.}" == "ini" || usage

docker \
    run --rm -it \
    -v "$(pwd):/app" \
    -v "$conf:/config/conf.ini" \
    -v "$mindmap:/config/freeplane_doc.mm" \
    -e "JIRA_USER=${JIRA_USER}" \
    -e "JIRA_PASS=${JIRA_PASS}" \
    -w "/app" \
    -u "$(id -u):$(id -g)" \
    jira_mindmap jirafp \
    /config/conf.ini \
    /config/freeplane_doc.mm
