#!/bin/sh
#
# FPGA toolchain install script.
# v1.1
# This script installs a full Open Source FPGA toolchain to a user directory.
#
# Author: Michael Buesch <m@bues.ch>
#
# This code is Public Domain.
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE
# USE OR PERFORMANCE OF THIS SOFTWARE.
#

die()
{
	echo "$*" >&2
	exit 1
}

show_help()
{
	echo "Usage: build_fpga_toolchain.sh <OPTIONS> [INSTALLDIR]"
	echo
	echo "Options:"
	echo " -j|--jobs NR                  Set the number of build jobs to run in parallel."
	echo "                               Default: Number of CPUs"
	echo " -h|--help                     Print help."
	echo
	echo
	echo "Install toolchain to $HOME/fpga-toolchain"
	echo "  ./build_fpga_toolchain.sh"
	echo
	echo "Install toolchain to another destination"
	echo "  ./build_fpga_toolchain.sh /home/user/directory"
	echo
	echo "The script will create a temporary directory during build to build all tools:"
	echo "  ./fpga-toolchain-build-tmp"
	echo
	echo "The following tools are needed to build the toolchain:"
	echo "- gcc"
	echo "- clang"
	echo "- python3"
	echo "- cmake"
	echo "- git"
	echo "Please ensure that all of these tools are installed in the system."
}

parse_args()
{
	# Defaults:
	PARALLEL="$(getconf _NPROCESSORS_ONLN)"
	BUILDDIR="./fpga-toolchain-build-tmp"
	INSTALLDIR="$HOME/fpga-toolchain"

	# Source repositories:
	REPO_ICESTORM="https://github.com/cliffordwolf/icestorm.git"
	REPO_NEXTPNR="https://github.com/YosysHQ/nextpnr.git"
	REPO_YOSYS="https://github.com/YosysHQ/yosys.git"
	REPO_TINYPROG="https://github.com/tinyfpga/TinyFPGA-Bootloader.git"

	# Parse command line options
	while [ $# -ge 1 ]; do
		[ "$(printf '%s' "$1" | cut -c1)" != "-" ] && break

		case "$1" in
		-h|--help)
			show_help
			exit 0
			;;
		-j|--jobs)
			shift
			PARALLEL="$1"
			[ -z "$PARALLEL" -o -n "$(printf '%s' "$PARALLEL" | tr -d '[0-9]')" ] &&\
				die "--jobs: '$PARALLEL' is not a positive integer number."
			;;
		*)
			echo "Unknown option: $1"
			exit 1
			;;
		esac
		shift
	done

	if [ $# -ge 1 -a -n "$1" ]; then
		# User defined INSTALLDIR
		INSTALLDIR="$1"
	fi
}

checkprog()
{
	local prog="$1"
	which "$prog" >/dev/null ||\
		die "$prog is not installed. Please install it by use of the distribution package manager (apt, apt-get, rpm, etc...)"
}

check_build_environment()
{
	[ "$(id -u)" = "0" ] && die "Do not run this as root!"
	checkprog gcc
	checkprog clang
	checkprog python3
	checkprog cmake
	checkprog git
}

cleanup()
{
	rm -rf "$BUILDDIR" || die "Failed to cleanup BUILDDIR"
}

prepare()
{
	# Resolve paths.
	BUILDDIR="$(realpath -m -s "$BUILDDIR")"
	INSTALLDIR="$(realpath -m -s "$INSTALLDIR")"
	echo "BUILDDIR=$BUILDDIR"
	echo "INSTALLDIR=$INSTALLDIR"
	echo "PARALLEL=$PARALLEL"
	[ -n "$BUILDDIR" -a -n "$INSTALLDIR" ] || die "Failed to resolve directories"
	echo

	# Create the build directories.
	cleanup
	mkdir -p "$BUILDDIR" || die "Failed to create BUILDDIR"
	mkdir -p "$INSTALLDIR" || die "Failed to create INSTALLDIR"

	# Reset the new PATH.
	NEWPATH="\$PATH"
}

build_icestorm()
{
	echo "Building icestorm..."
	cd "$BUILDDIR" || die "Failed to cd to builddir."
	git clone "$REPO_ICESTORM" "$BUILDDIR/icestorm" || die "Failed to clone icestorm"
	cd "$BUILDDIR/icestorm" || die "Failed to cd to icestorm."
	export PREFIX="$INSTALLDIR/icestorm"
	make -j "$PARALLEL" PREFIX="$PREFIX" || die "Failed to build icestorm"
	rm -rf "$PREFIX" || die "Failed to clean install icestorm"
	make install PREFIX="$PREFIX" || die "Failed to install icestorm"

	NEWPATH="$PREFIX/bin:$NEWPATH"
}

build_nextpnr()
{
	echo "Building nextpnr..."
	cd "$BUILDDIR" || die "Failed to cd to builddir."
	git clone "$REPO_NEXTPNR" "$BUILDDIR/nextpnr" || die "Failed to clone nextpnr"
	mkdir "$BUILDDIR/nextpnr/builddir" || die "Failed to create nextpnr builddir"
	cd "$BUILDDIR/nextpnr/builddir" || die "Failed to cd to nextpnr."
	export PREFIX="$INSTALLDIR/nextpnr"
	cmake -DARCH=ice40 -DICEBOX_ROOT="$INSTALLDIR/icestorm/share/icebox" -DCMAKE_INSTALL_PREFIX="$PREFIX" .. || die "Failed to build nextpnr"
	make -j "$PARALLEL" || die "Failed to build nextpnr"
	rm -rf "$PREFIX" || die "Failed to clean install nextpnr"
	make install || die "Failed to install nextpnr"

	NEWPATH="$PREFIX/bin:$NEWPATH"
}

build_yosys()
{
	echo "Building yosys..."
	cd "$BUILDDIR" || die "Failed to cd to builddir."
	git clone "$REPO_YOSYS" "$BUILDDIR/yosys" || die "Failed to clone yosys"
	cd "$BUILDDIR/yosys" || die "Failed to cd to yosys."
	export PREFIX="$INSTALLDIR/yosys"
	make config-clang PREFIX="$PREFIX" || die "Failed to configure yosys"
	make -j "$PARALLEL" PREFIX="$PREFIX" || die "Failed to build yosys"
	rm -rf "$PREFIX" || die "Failed to clean install yosys"
	make install PREFIX="$PREFIX" || die "Failed to install yosys"

	NEWPATH="$PREFIX/bin:$NEWPATH"
}

build_tinyprog()
{
	echo "Building tinyprog..."
	cd "$BUILDDIR" || die "Failed to cd to builddir."
	git clone "$REPO_TINYPROG" "$BUILDDIR/TinyFPGA-Bootloader" || die "Failed to clone tinyprog"
	cd "$BUILDDIR/TinyFPGA-Bootloader/programmer" || die "Failed to cd to tinyprog."
	export PREFIX="$INSTALLDIR/tinyprog"
	rm -rf "$PREFIX" || die "Failed to clean install tinyprog"
	mkdir -p "$PREFIX/lib" || die "Failed to create tinyprog lib"
	mkdir -p "$PREFIX/bin" || die "Failed to create tinyprog bin"
	cp -r "$BUILDDIR/TinyFPGA-Bootloader/programmer/tinyprog" "$PREFIX/lib/" || die "Failed to install tinyprog"
	cat > "$PREFIX/bin/tinyprog" <<EOF
#!/bin/sh
export PYTHONPATH="$PREFIX/lib/:\$PYTHONPATH"
exec python3 "$PREFIX/lib/tinyprog" "\$@"
EOF
	[ -f "$PREFIX/bin/tinyprog" ] || die "Failed to install tinyprog wrapper"
	chmod 755 "$PREFIX/bin/tinyprog" || die "Failed to chmod tinyprog"

	NEWPATH="$PREFIX/bin:$NEWPATH"
}


parse_args "$@"
check_build_environment
prepare
build_icestorm
build_nextpnr
build_yosys
build_tinyprog
cleanup

echo
echo
echo
echo "Successfully built and installed all FPGA tools to: $INSTALLDIR"
echo "Please add the following line to your $HOME/.bashrc file:"
echo
echo "export PATH=\"$NEWPATH\""
echo
