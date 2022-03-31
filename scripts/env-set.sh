#!/bin/sh

# $1 - (in) (optional) template (.env.template)
# $2 - (in) (optional) vars (.env.vars)
# $3 - (out) (optional) out (.env)

set -eu # unset variables are errors & non-zero return values exit the whole script
[ "${DEBUG:-}" = "true" ] && set -x

ENV_FILE="${3:-./.env}"
ENV_FILE_EXAMPLE="${3:-${ENV_FILE}}.example"
ENV_FILE_TMP="${3:-${ENV_FILE}}.tmp"
ENV_FILE_VARS="${2:-${ENV_FILE}.vars}"
ENV_FILE_TEMPLATE="${1:-${ENV_FILE}.template}"

path="$(dirname "$0")"

> "${ENV_FILE}"
[ -f "${path}/pre-process-env.sh" ] && . "${path}/pre-process-env.sh" "${ENV_FILE_VARS}"
"${path}/templater.sh" "${ENV_FILE_TEMPLATE}" "${ENV_FILE_VARS}" >> "${ENV_FILE}"
if [ -f "${path}/post-process-env.sh" ] ; then
    if bash --version >/dev/null 2>&1; then
        "${path}/post-process-env.sh" "${ENV_FILE}";
    else
        echo bash not installed
        docker stop bash || true
        docker rm bash || true
        docker run -i -w=/work --name bash -d bash:5
        docker cp ./ bash:/work
        # патамушо в образе bash находится по другому пути
        docker exec -i bash ln /usr/local/bin/bash /bin/bash;
        docker exec -i bash "${path}/post-process-env.sh" "${ENV_FILE}";
        docker cp bash:"/work/${ENV_FILE}" "${ENV_FILE}"
        docker stop bash || true
        docker rm bash || true
    fi
fi
