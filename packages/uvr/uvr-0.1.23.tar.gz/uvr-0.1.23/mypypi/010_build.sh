#!/usr/bin/bash
set -e
set -x

pushd .. &> /dev/null
pwd

# build packages for pypi
# clean dist
rm -rf dist/
rm -rf build/

uv build

popd &> /dev/null




