#!/bin/sh

basedir="$(dirname "$0")"
[ "$(echo "$basedir" | cut -c1)" = '/' ] || basedir="$PWD/$basedir"

awlsim_base="$basedir/.."

set -e

if ! [ -x "$awlsim_base/awlsim-test" -a -x "$awlsim_base/setup.py" ]; then
	echo "basedir sanity check failed"
	exit 1
fi

cd "$awlsim_base"

find . \( \
	\( -name '__pycache__' \) -o \
	\( -name '*.pyo' \) -o \
	\( -name '*.pyc' \) -o \
	\( -name '*$py.class' \) \
       \) -delete

rm -rf build dist .pybuild
rm -f MANIFEST

rm -f *.html
find ./doc -name '*.html' -delete

rm -rf tests/build
find ./tests -name '__init__.py' -delete

rm -f debian/files \
      debian/*.debhelper \
      debian/*.log \
      debian/*.substvars \
      debian/debhelper-build-stamp
rm -rf debian/destdir-* \
       debian/python-awlsim \
       debian/python-awlsimhw-dummy \
       debian/python-awlsimhw-linuxcnc \
       debian/python-awlsimhw-profibus \
       debian/python-awlsimhw-rpigpio \
       debian/python-awlsimhw-pixtend \
       debian/python-awlsim-gui \
       debian/cython-awlsim \
       debian/cython-awlsimhw-dummy \
       debian/cython-awlsimhw-linuxcnc \
       debian/cython-awlsimhw-profibus \
       debian/cython-awlsimhw-rpigpio \
       debian/cython-awlsimhw-pixtend \
       debian/python3-awlsim \
       debian/python3-awlsim-gui \
       debian/python3-awlsimhw-dummy \
       debian/python3-awlsimhw-linuxcnc \
       debian/python3-awlsimhw-profibus \
       debian/python3-awlsimhw-rpigpio \
       debian/python3-awlsimhw-pixtend \
       debian/cython3-awlsim \
       debian/cython3-awlsimhw-dummy \
       debian/cython3-awlsimhw-linuxcnc \
       debian/cython3-awlsimhw-profibus \
       debian/cython3-awlsimhw-rpigpio \
       debian/cython3-awlsimhw-pixtend \
       debian/awlsim-client \
       debian/awlsim-server \
       debian/awlsim-symtab \
       debian/awlsim-test \
       debian/awlsim-linuxcnc-hal \
       debian/awlsim-gui \
       debian/awlsim-proupgrade
