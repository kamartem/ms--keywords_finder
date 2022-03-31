#!/bin/bash

# Available parameters are:
# --service-name <service-name> - starts specific service with its dependencies
# --down - stops and removes containers of running services
# --logs - displays logs output for all services or only for service specified by '--service-name' parameter
# --pull - pulls fresh images before starting containers

set -ea

export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

#./scripts/templater.sh ./scripts/.env.template ./scripts/.env.vars > .env
#./scripts/post-process-env.sh .env >> .env
./scripts/env-set.sh ./scripts/.env.template ./scripts/.env.vars ./.env

[ -f .env ] && source .env

UNKNOWN_POSITIONAL_PARAMS=()

while [ "$#" -gt 0 ]; do
    key="$1"

    case $key in
        --service-name)
            SERVICE_NAME="$2"
            shift # past parameter
            shift # past value

            if [ -z "${SERVICE_NAME-false}" ]; then
                printf '%s\n' "Value for '--service-name' parameter is required!"
                exit 1
            fi
            ;;
        --down)
            DOWN="$1"
            shift # past parameter
            ;;
        --push)
            PUSH="$1"
            shift # past parameter
            ;;
        --logs)
            LOGS="$1"
            shift # past parameter
            ;;
        --pull)
            PULL="$1"
            shift # past parameter
            ;;
        --restore)
            RESTORE="$1"
            shift # past parameter
            ;;
        *)    # unknown option
            UNKNOWN_POSITIONAL_PARAMS+=("$1")
            shift # past parameter
            ;;
    esac
done

if [ "${#UNKNOWN_POSITIONAL_PARAMS[@]}" -ne 0 ]; then
    printf '%s\n' "Unrecognized parameters: '${UNKNOWN_POSITIONAL_PARAMS[*]}'"
    printf '%s\n' "Available parameters are:"
    printf '%s\n' "--service-name <service-name> - specifies service that should be started or for which logs should be displayed"
    printf '%s\n' "--down - stops and removes containers of running services"
    printf '%s\n' "--logs - displays logs output for all services or only for service specified by '--service-name' parameter"
    printf '%s\n' "--pull - pulls fresh images before starting containers"
    printf '%s\n' "--restore - removed volumes, networks and images for compose"
    exit 0
fi

COMPOSE_PROFILES_PREFIX="COMPOSE_PROFILES=${COMPOSE_PROFILES}"
printf '%s\n' "Start with profiles: ${COMPOSE_PROFILES}"

DOCKER_COMPOSE_CONFIG="${COMPOSE_PROFILES_PREFIX} docker-compose -f docker-compose.yml"
DOCKER_COMPOSE_UP_OPTIONS=""

PROJECT_STAGE=${PROJECT_STAGE:-prod}

printf '%s\n' "Start mode: ${PROJECT_STAGE}"

STAGE_YML="${PROJECT_STAGE}.yml"
if test -f "$STAGE_YML"; then
    DOCKER_COMPOSE_CONFIG+=" -f ${STAGE_YML}"
else
    echo "$STAGE_YML does not exist"
    exit 0
fi

case ${PROJECT_STAGE} in
    local)
        DOCKER_COMPOSE_UP_OPTIONS=""
        ;;
    dev)
        DOCKER_COMPOSE_UP_OPTIONS=""
        ;;
    stage)
        DOCKER_COMPOSE_UP_OPTIONS="--no-build -d"
        ;;
    prod | *)
        DOCKER_COMPOSE_UP_OPTIONS="--no-build -d"
        ;;
esac

#### RESTORE ####
DOCKER_COMPOSE_RESTORE=("${DOCKER_COMPOSE_CONFIG}" "down -v --remove-orphans")
if [ "${RESTORE}" == "--restore" ]; then
    printf '%s\n' "Stopping containers, removing containers, networks, volumes ..."
    printf '%s\n' "Running command: ${DOCKER_COMPOSE_RESTORE[*]}"
    eval "${DOCKER_COMPOSE_RESTORE[@]}"
    exit 0;
fi
#### END RESTORE ####

#### DOWN ####
DOCKER_COMPOSE_DOWN=("${DOCKER_COMPOSE_CONFIG}" "down --remove-orphans")
if [ "${SERVICE_NAME:=false}" != "false" ]; then
    DOCKER_COMPOSE_DOWN=("${DOCKER_COMPOSE_DOWN[@]}" "${SERVICE_NAME}")
fi

if [ "${DOWN}" == "--down" ]; then
    printf '%s\n' "Stopping containers, removing containers and networks ..."
    printf '%s\n' "Running command: ${DOCKER_COMPOSE_DOWN[*]}"
    eval "${DOCKER_COMPOSE_DOWN[@]}"
    exit 0;
fi
#### END DOWN ####

#### BUILD  ####
BUILD_ARGS="--build-arg BACKEND_GIT_COMMIT=$(cd backend && git rev-parse --short HEAD) --build-arg BACKEND_GIT_DATE='$(cd backend && git show -s --format=%ci HEAD)'"
DOCKER_COMPOSE_BUILD=("${DOCKER_COMPOSE_CONFIG}" "build --pull ${BUILD_ARGS}")
if [ "${SERVICE_NAME:=false}" != "false" ]; then
    DOCKER_COMPOSE_BUILD=("${DOCKER_COMPOSE_BUILD[@]}" "${SERVICE_NAME}")
fi

if [ "${BUILD}" == "--build" ]; then
    printf '%s\n' "Building containers ..."
    printf '%s\n' "Running command: ${DOCKER_COMPOSE_BUILD[*]}"
    eval "${DOCKER_COMPOSE_BUILD[@]}"
    exit 0;
fi
#### END BUILD  ####

#### LOG ####
DOCKER_COMPOSE_LOGS=("${DOCKER_COMPOSE_CONFIG}" "logs" "${SERVICE_NAME}")
if [ "${SERVICE_NAME:=false}" != "false" ]; then
    DOCKER_COMPOSE_LOGS=("${DOCKER_COMPOSE_LOGS[@]}" "${SERVICE_NAME}")
fi

if [ "${LOGS}" == "--logs" ]; then
    printf '%s\n' "Displaying logs output ..."
    printf '%s\n' "Running command: ${DOCKER_COMPOSE_LOGS[*]}"
    eval "${DOCKER_COMPOSE_LOGS[@]}"
    exit 0;
fi
#### END LOG ####

#### PUSH ####
DOCKER_COMPOSE_PUSH=("${DOCKER_COMPOSE_CONFIG}" "push")
if [ "${SERVICE_NAME:=false}" != "false" ]; then
    DOCKER_COMPOSE_PUSH=("${DOCKER_COMPOSE_PUSH[@]}" "${SERVICE_NAME}")
fi

if [ "${PUSH}" == "--push" ]; then
    printf '%s\n' "Enforced push of fresh images ..."
    eval "${DOCKER_COMPOSE_PUSH[@]}"
    exit 0;
fi
#### END PUSH ####

#### UP ####
DOCKER_COMPOSE_UP=("${DOCKER_COMPOSE_CONFIG}" "up" "${DOCKER_COMPOSE_UP_OPTIONS}")

DOCKER_COMPOSE=(
    "${DOCKER_COMPOSE_DOWN[@]}" "&&"
    "${DOCKER_COMPOSE_BUILD[@]}" "&&"
    "${DOCKER_COMPOSE_UP[@]}"
)

DOCKER_COMPOSE_PULL=("${DOCKER_COMPOSE_CONFIG}" "pull")

if [ "${PULL}" == "--pull" ]; then
    printf '%s\n' "Enforced pull of fresh images ..."
    DOCKER_COMPOSE=("${DOCKER_COMPOSE[@]:0:3}" "${DOCKER_COMPOSE_PULL[@]}" "&&" "${DOCKER_COMPOSE[@]:3}")
fi

if [ "${SERVICE_NAME:=false}" != "false" ]; then
    DOCKER_COMPOSE=("${DOCKER_COMPOSE[@]}" "${SERVICE_NAME}")
fi

printf '%s\n' "Running command: ${DOCKER_COMPOSE[*]}"

eval "${DOCKER_COMPOSE[@]}"
#### END UP ####

set +a
