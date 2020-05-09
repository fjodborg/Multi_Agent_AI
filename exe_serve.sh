#!/bin/bash

# Script to run the server

# abs path to directory of repository
SERVER="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
if [ -z "$1" ];then
  echo -e "You must supply a level\n" && exit 1
else
  lvl=$1
fi

method="-astar"
[ -z "$2" ] || method=$2
mem=2048
[ -z "$3" ] || mem=$3

echo "Memory allocated: $mem"

java -jar "$SERVER/server.jar" -l "$SERVER/levels/$lvl" -c "python $SERVER/multi_sokoban/searchclient.py $method --max-memory $mem" -g 150 -t 300
