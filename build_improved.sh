#!/bin/bash

set -e

# Constants
DEFAULT_IMAGE="yet_another_flask_template"
DEFAULT_TAG="latest"
DEFAULT_PORT="3000"
DEFAULT_HOST="0.0.0.0"

# Default values
IMAGE_NAME="${DEFAULT_IMAGE}"
IMAGE_FULL_NAME="${DEFAULT_IMAGE}:${DEFAULT_TAG}"
PORT="${DEFAULT_PORT}"
HOST="${DEFAULT_HOST}"
DAEMONIZE=false
USE_SHELL=false

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
  echo "Error: Docker is not installed. Please install Docker and try again."
  exit 1
fi

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -i|--image)
    IMAGE_NAME="$2"
    shift # past argument
    shift # past value
    ;;
    -p|--port)
    PORT="$2"
    shift # past argument
    shift # past value
    ;;
    -H|--host)
    HOST="$2"
    shift # past argument
    shift # past value
    ;;
    -d|--daemonize)
    DAEMONIZE=true
    shift # past argument
    ;;
    -s|--shell)
    USE_SHELL=true
    shift # past argument
    ;;
    -h|--help)
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
  -s, --shell               Run an interactive shell inside the container
  -h, --help                Show this help message and exit
EOM
    exit 0
    ;;
    *)
    COMMAND="$1"
    shift # past argument
    ;;
  esac
done

# Function to build the Docker image
build() {
  echo "Building Docker image..."
  docker buildx build --platform=linux/arm64/v8 --tag "${IMAGE_FULL_NAME}" .
  echo "Docker image built successfully."
}

# Function to start the Docker container
start() {
  FLAGS=""
  [ $DAEMONIZE = true ] && FLAGS="-d"
  [ $USE_SHELL = true ] && FLAGS="${FLAGS} -it"

  CMD=""
  [ $USE_SHELL = true ] && CMD="/bin/bash"

  echo "Starting Docker container..."
  docker run --rm ${FLAGS} \
    -p "${HOST}:${PORT}:3000" \
    --name "${IMAGE_NAME}" \
    "${IMAGE_FULL_NAME}" \
    ${CMD}
  echo "Docker container started successfully."
}

# Function to rebuild the Docker container
rebuild() {
  build
  start
}

# Function to remove the Docker container
remove() {
  echo "Removing Docker container..."
  docker rm -f "${IMAGE_NAME}"
  echo "Docker container removed successfully."
}

# Perform the specified command using the defined functions
case "${COMMAND}" in
  build)
  build
  ;;

  start)
  start
  ;;

  rebuild)
  rebuild
  ;;

  remove)
  remove
  ;;

  *)
  # If the command is unknown, print an error message and exit
  echo "Unknown command. Available commands: build, start, rebuild, remove"
  exit 1
  ;;
esac
