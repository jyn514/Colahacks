#! /bin/sh

FILE=$1
ZIP=$2
TMP=.tmpsnap
TIME=`date +%s`

if [ "$#" -lt "2" ]; then
  echo "Usage: snap <directory> <zipfile>";
  exit 1;
fi

if [ ! -d "$FILE" ]; then
  echo "Cannot take snapshot of $FILE";
  exit 1;
fi

mkdir -p $TMP

if [ -a "$2" ]; then
  unzip "$ZIP" $TMP
fi

cp ${FILE}/* ${TMP}/${TIME}

here=`pwd`
cd $TMP
zip -r ${here}/${ZIP} *
cd $here

rm -rf ${TMP}/*
