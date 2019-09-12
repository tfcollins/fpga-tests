#!/bin/bash
BOARD=$1
echo $BOARD
FILES=$(find ../test/BINS/ -type f -name "*_$BOARD_*.BIN")
echo $FILES
for bin in $FILES
do
  echo "Checking $bin"
  cp $bin BOOT.BIN
  python3 -m pytest -v test_$BOARD.py
done
