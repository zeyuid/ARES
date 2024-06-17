# LinuxCNC hardware module test

__run_awlsim_linuxcnc_hal()
{
	local interpreter="$1"
	local test_dir="$2"
	local awl_file="$3"
	shift 3

	export EXTRA_PYTHONPATH="$rootdir/libs/linuxcnc_fake_hal"
	setup_test_environment "$interpreter" "$awl_file" "${awl_file}.linuxcnc"
	local interpreter="$RET"

	FAKEHAL_HALFILE="${test_dir}/linuxcnc.hal" \
		"$interpreter" ./awlsim-linuxcnc-hal \
		--input-base 0 --input-size 32 \
		--output-base 50 --output-size 32 \
		--watchdog off --extended-insns \
		--listen localhost:$(get_port) \
		"$@" \
		"$awl_file" >/dev/null ||\
			test_failed "LinuxCNC test '$(basename "$awl_file")' failed"

	cleanup_test_environment
}

sh_test()
{
	local interpreter="$1"
	local test_dir="$2"
	local test_name="$3"

	cd "$rootdir" || die "Failed to change to rootdir '$rootdir'"

	infomsg
	for testfile in "tc000_base/empty.awl"\
			"tc000_base/shutdown.awl"\
			"tc000_base/EXAMPLE.awlpro"; do
		infomsg "    Running linuxcnc test with: $testfile"

		__run_awlsim_linuxcnc_hal "$interpreter" "$test_dir" \
			"$rootdir/tests/$testfile" \
			--max-runtime 1.0
	done

	infomsg "    Running I/O test"
	__run_awlsim_linuxcnc_hal "$interpreter" "$test_dir" \
		"$test_dir/linuxcnc-iotest.awl__"
}
