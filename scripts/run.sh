#!/bin/bash

TEXT_RED="\033[0;31m"
TEXT_GREEN="\033[0;32m"
TEXT_ORANGE="\033[0;33m"
TEXT_NONE="\033[0m"

PORT=4040

pids=()

trap terminate EXIT

terminate() {
    for p in ${pids[@]}; do
        echo "killing $p"
        kill $p
    done
}

printf "$TEXT_ORANGE Starting redis server...\n"
redis-server &
pids+=($!)

printf "$TEXT_RED Running python speech diarization...\n"
./server/speech_diarization/test_redis.py &
pids+=($!)

printf "$TEXT_GREEN Running rest server on port $PORT...\n $TEXT_NONE"
npm start --prefix server/rest/ $PORT
pids+=($!)