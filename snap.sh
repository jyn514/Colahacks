#!/bin/sh

FILE="$1"
ZIP="$2"

if [ -z "$ZIP" ]; then ZIP="$FILE.zip"; fi

TMP=`mktemp -d`
TIME=`date +%s`

if [ "$#" -lt 1 ]; then
  echo "Usage: snap <directory> [zipfile]";
  exit 1;
fi

if [ ! -d "$FILE" ]; then
  echo "$FILE is not a directory"
  exit 1;
fi

if [ -e "$ZIP" ]; then
  unzip -q "$ZIP" -d $TMP
fi

cp -r $FILE/. $TMP/$TIME

here=`pwd`
cd $TMP
zip -rq $here/$ZIP *
cd $here

rm -r $TMP/*
