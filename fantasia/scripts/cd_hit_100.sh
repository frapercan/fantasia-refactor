#!/bin/bash

INPUT=$1
OUTPUT=$2

cd-hit -i $INPUT -o $OUTPUT -c 1
