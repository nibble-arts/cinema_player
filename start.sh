#!/bin/bash

ROOT="$( cd "$(dirname "$0")" ; pwd -P )"

unclutter -idle 0.01 -root &
$ROOT/cinema_player
