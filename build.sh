#!/bin/bash

set -e

# Constants
# Set default image name, port, and host values
DEFAULT_IMAGE="yet_another_flask_template"
DEFAULT_TAG="latest"
DEFAULT_PORT="3000"
DEFAULT_HOST="0.0.0.0"

# Default values
# Assign default values to variables
IMAGE_NAME="${DEFAULT_IMAGE}"
IMAGE_FULL_NAME="${DEFAULT_IMAGE}:${DEFAULT_TAG}"
PORT="${DEFAULT_PORT}"
HOST="${DEFAULT_HOST}"
DAEMONIZE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -i|--image)
    # If --image or -i is specified, set IMAGE_NAME to the provided value
    IMAGE_NAME="$2"
    shift # past argument
    shift # past value
    ;;

    --shell)
    # If --shell is specified, enable shell mode
    USE_SHELL=true
    shift # past argument
    ;;

    -p|--port)
    # If --port or -p is specified, set PORT to the provided value
    PORT="$2"
    shift # past argument
    shift # past value
    ;;

    -H|--host)
    # If --host or -H is specified, set HOST to the provided value
    HOST="$2"
    shift # past argument
    shift # past value
    ;;

    -d|--daemonize)
    # If --daemonize or -d is specified, enable daemonize mode
    DAEMONIZE=true
    shift # past argument
    ;;

    -h|--help)
    # If --help or -h is specified, display help message and exit
    cat <<EOM
Usage: $0 COMMAND [OPTIONS]

Commands:
  build       Build the Docker image
  start       Start the Docker container
  rebuild     Rebuild the Docker container (build and start)
  remove      Remove the Docker container

Options:
  -i, --image IMAGE_NAME    Set the image name (default: ${DEFAULT_IMAGE})
  -p, --port PORT           Set the port (default: ${DEFAULT_PORT})
  -H, --host HOST           Set the host (default: ${DEFAULT_HOST})
  -d, --daemonize           Run the container in daemon mode (detached)
  -h, --help                Show this help message and exit
EOM
    exit 0
    ;;
    *)
    # Otherwise, set COMMAND to the provided value
    COMMAND="$1"
    shift # past argument
    ;;
  esac
done

# Function to build the Docker image
build() {
  docker buildx build --platform=linux/arm64/v8 --tag "${IMAGE_FULL_NAME}" .
}

# Function to start the Docker container
start() {
  FLAGS=""
  [ $DAEMONIZE = true ] && FLAGS="-d"
  [ $USE_SHELL = true ] && FLAGS="${FLAGS} -it"

  CMD=""
  [ $USE_SHELL = true ] && CMD="/bin/bash"

  docker run --rm ${FLAGS} \
    -p "${HOST}:${PORT}:80" \
    --name "${IMAGE_NAME}" \
    "${IMAGE_FULL_NAME}" \
    ${CMD}
}

# Function to rebuild the Docker container
rebuild() {
  build
  remove
  start
}

# Function to remove the Docker container
remove() {
  docker rm -f "${IMAGE_NAME}"
}

# Function to open a Bash shell in the running Docker container
shell() {
  docker exec -it "${IMAGE_NAME}" /bin/bash
}

# Perform the specified command using the defined functions
case "${COMMAND}" in
  build)
  # If the command is 'build', run the build() function
  build
  ;;

  shell)
  # If the command is 'shell', run the shell() function
  shell
  ;;

  start)
  # If the command is 'start', run the start() function
  start
  ;;

  rebuild)
  # If the command is 'rebuild', run the rebuild() function
  rebuild
  ;;

  remove)
  # If the command is 'remove', run the remove() function
  remove
  ;;

  *)
  # If the command is unknown, print an error message and exit
  echo "Unknown command. Available commands: build, start, rebuild, remove"
  exit 1
  ;;
esac
