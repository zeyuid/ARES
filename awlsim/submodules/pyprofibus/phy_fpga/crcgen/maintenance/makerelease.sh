#!/bin/sh

srcdir="$(dirname "$0")"
[ "$(echo "$srcdir" | cut -c1)" = '/' ] || srcdir="$PWD/$srcdir"

srcdir="$srcdir/.."

die() { echo "$*"; exit 1; }

# Import the makerelease.lib
# http://bues.ch/gitweb?p=misc.git;a=blob_plain;f=makerelease.lib;hb=HEAD
for path in $(echo "$PATH" | tr ':' ' '); do
	[ -f "$MAKERELEASE_LIB" ] && break
	MAKERELEASE_LIB="$path/makerelease.lib"
done
[ -f "$MAKERELEASE_LIB" ] && . "$MAKERELEASE_LIB" || die "makerelease.lib not found."

hook_get_version()
{
	local file="$1/crcgen/version.py"
	local maj="$(cat "$file" | grep -Ee '^VERSION_MAJOR\s+=\s+' | head -n1 | awk '{print $3;}')"
	local min="$(cat "$file" | grep -Ee '^VERSION_MINOR\s+=\s+' | head -n1 | awk '{print $3;}')"
	local ext="$(cat "$file" | grep -Ee '^VERSION_EXTRA\s+=\s+' | head -n1 | awk '{print $3;}' | cut -d'"' -f2)"
	version="${maj}.${min}${ext}"
}

hook_post_checkout()
{
	default_hook_post_checkout "$@"

	rm -r "$1"/maintenance
}

hook_regression_tests()
{
	default_hook_regression_tests "$@"

	# Run selftests
	python3 "$1/crcgen_test.py"
}

project=crcgen
default_archives=py-sdist-xz
makerelease "$@"
