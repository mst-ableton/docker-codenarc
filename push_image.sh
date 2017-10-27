#!/bin/bash
# whitespace

set -e

IMAGENAME=codenarc

REMOTE=dtr.ableton.com/devtools/$IMAGENAME

docker build -t $IMAGENAME .
echo
read -p "About to push to $REMOTE. Proceed? [Y/n] " -r REPLY
REPLY=${REPLY:-Y}
if [[ $REPLY =~ ^[Yy]$ ]]
then
  docker tag $IMAGENAME $REMOTE
  docker push $REMOTE
  docker pull $REMOTE  # just to be in sync
else
  echo "Aborting."
fi
