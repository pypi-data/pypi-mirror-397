#!/bin/bash

pushd $(dirname "$0") > /dev/null
[ ! -d ./build ] && mkdir build
pushd build > /dev/null

ignoredWarnings="-Wno-parentheses"

gcc -O3 -o keyedDecrypt.so ../keyedDecrypt.c -Wall -Wextra -Werror $ignoredWarnings -shared -fPIC

# generate a file for testing
# gcc -ggdb -O0 ../runner.c -Wall -Wextra -Werror $ignoredWarnings

popd > /dev/null

# regenerate the interop code
# python ctypes_autogen.py keyedDecrypt.c build/keyedDecrypt.so ../interop.py

popd > /dev/null