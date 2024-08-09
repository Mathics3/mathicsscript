#!/bin/bash
function finish {
  cd $mathicsscript_owd
}

# FIXME put some of the below in a common routine
mathicsscript_owd=$(pwd)
trap finish EXIT

cd $(dirname ${BASH_SOURCE[0]})
if ! source ./pyenv-versions ; then
    exit $?
fi

cd ..
for version in $PYVERSIONS; do
    echo --- $version ---
    if ! pyenv local $version ; then
	exit $?
    fi
    make clean && pip install -e .
    if ! make check; then
	exit $?
    fi
    echo === $version ===
done
finish
