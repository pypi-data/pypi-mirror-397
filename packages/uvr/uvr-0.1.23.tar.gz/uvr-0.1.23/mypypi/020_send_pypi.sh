#!/usr/bin/bash
set -e
set -x

pushd .. &> /dev/null
pwd

# upload to pypi  (check you have valit token, ~/.pypirc

uv run twine upload dist/*


popd &> /dev/null




