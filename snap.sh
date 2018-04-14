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
  unzip "$ZIP" -d $TMP
fi

echo cp -r $FILE/. $TMP/$TIME
cp -r $FILE/. $TMP/$TIME

here=`pwd`
cd $TMP
zip -r $here/$ZIP *
cd $here

rm -r $TMP/*
