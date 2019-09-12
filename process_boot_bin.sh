#!/bin/bash
BOARD=$1
echo $BOARD
IFS=","
FILES=$(find ../test/BINS/ -type f -name "*$BOARD*.BIN" -printf "'%f',")
for bin in $FILES
do
  echo "Checking $bin"
  cp $bin BOOT.BIN
  python3 -m pytest -v test_$BOARD.py
done
