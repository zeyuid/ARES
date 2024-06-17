print("boot.py")

# Start the watchdog first.
if 1:
	import machine
	watchdog = machine.WDT(timeout=5000).feed
	print("Watchdog active.")
else:
	watchdog = None
	print("Watchdog inactive.")

import sys, gc

# Add stubs to Python path.
sys.path.insert(0, "/stublibs")

# Enable gc after allocation of this many bytes:
gc.threshold(2**11)
gc.collect()
