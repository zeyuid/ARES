######################################################
# FPGA make library                                  #
# Original author: Michael Buesch <m@bues.ch>        #
# This code is Public Domain.                        #
# Version 1.0                                        #
######################################################


# Tools.
YOSYS		:= yosys
NEXTPNR		:= nextpnr
ICEPACK		:= icepack
ICETIME		:= icetime
ICEPLL		:= icepll
TINYPROG	:= tinyprog
PYTHON		:= python3
CAT		:= cat
GREP		:= grep
PRINTF		:= printf
RM		:= rm
FALSE		:= false
TR		:= tr
TEST		:= test
TOUCH		:= touch
GIT		:= git

# Target name transformations.
TARGET_NAME	:= $(TARGET)_$(NAME)
TARGET_LOWER	:= $(shell $(PRINTF) '%s' '$(TARGET)' | $(TR) A-Z a-z)
TARGET_UPPER	:= $(shell $(PRINTF) '%s' '$(TARGET)' | $(TR) a-z A-Z)

# Target specific options and commands.
ifeq ($(TARGET_LOWER),tinyfpga_bx)
YOSYS_SYNTH_CMD	= 'synth_ice40 -top $(TOP_MODULE) -json $(patsubst %.blif,%.json,$@) -blif $@'
PNR_PACKAGE	:= cm81
NEXTPNR_ARCH	:= ice40
DEVICE		:= lp8k
else
$(error TARGET $(TARGET) is unknown)
endif

# Log files.
YOSYS_LOG	:= $(TARGET_NAME)_yosys.log
NEXTPNR_LOG	:= $(TARGET_NAME)_nextpnr.log
ICEPACK_LOG	:= $(TARGET_NAME)_icepack.log
ICETIME_LOG	:= $(TARGET_NAME)_icetime.log
LOG		= >$(1) 2>&1 || ( $(CAT) $(1); $(FALSE) )

# PLL sanity check.
ifneq ($(PLL_MOD_V_FILE),)
ifeq ($(PLL_HZ),)
$(error PLL_HZ is not defined)
endif
endif

# Clock speeds.
ifeq ($(TARGET_LOWER),tinyfpga_bx)
CLK_HZ		:= 16000000
ifeq ($(PLL_MOD_V_FILE),)
PLL_HZ		:= $(CLK_HZ)
else
CLK_MHZ		:= $(shell expr $(CLK_HZ) / 1000000)
PLL_MHZ		:= $(shell expr $(PLL_HZ) / 1000000)
$(PLL_MOD_V_FILE):
	$(ICEPLL) -q -f $@ -m -n pll_module -i $(CLK_MHZ) -o $(PLL_MHZ)
endif
endif

# MyHDL to Verilog
%.v: %.py $(wildcard *.py) $(EXTRA_DEP_PY)
	$(PYTHON) -B $<

# Synthesis
%.blif: $(TOP_FILE) $(wildcard *.v) $(GENERATED_V) $(PLL_MOD_V_FILE) $(EXTRA_DEP_V)
	$(YOSYS) -p 'read_verilog -DTARGET_$(TARGET_UPPER)=1 -DCLK_HZ=$(CLK_HZ) -DPLL_HZ=$(PLL_HZ) $(if $(filter-out 0,$(DEBUG)),-DDEBUG=1) $<' \
		-p $(YOSYS_SYNTH_CMD) \
		$(call LOG,$(YOSYS_LOG))

# Place and route
%.asc: $(PCF_FILE) %.blif
	$(NEXTPNR)-$(NEXTPNR_ARCH) --$(DEVICE) --package $(PNR_PACKAGE) --json $(TARGET_NAME).json --pcf $< --asc $@ \
		$(call LOG,$(NEXTPNR_LOG))

# Binary packing
%.bin: %.asc
ifeq ($(TARGET_LOWER),tinyfpga_bx)
	$(ICEPACK) $< $@ $(call LOG,$(ICEPACK_LOG))
endif

# Report generation
%.rpt: %.asc %.bin
ifeq ($(TARGET_LOWER),tinyfpga_bx)
	$(ICETIME) -d $(DEVICE) -p $(PCF_FILE) -m -t -r $@ $< \
		$(call LOG,$(ICETIME_LOG))
	-@$(PRINTF) '\n'
endif
	-@$(GREP) -i -e 'Total' $@
	-@$(GREP) -i -Ee 'Max frequency|Max delay' $(NEXTPNR_LOG)
	-@$(PRINTF) '\n'
	-@$(GREP) --color=auto -H -n -i -e 'Warning' $(YOSYS_LOG) $(NEXTPNR_LOG) $(ICEPACK_LOG)
	-@$(PRINTF) '\n'
	-@$(GREP) -A6 -i -e 'Device utilisation' $(NEXTPNR_LOG)

# Flashing
install: $(TARGET_NAME).bin
ifeq ($(TARGET_LOWER),tinyfpga_bx)
	$(TINYPROG) -p $<
endif

# Rebooting
boot:
ifeq ($(TARGET_LOWER),tinyfpga_bx)
	$(TINYPROG) -b
endif

# Cleanup
clean:
	$(RM) -rf *.blif *.json *.asc *.bin *.rpt __pycache__ $(YOSYS_LOG) $(NEXTPNR_LOG) $(ICEPACK_LOG) $(ICETIME_LOG) $(GENERATED_V) $(PLL_MOD_V_FILE) $(CLEAN_FILES)

# Default goal
all: $(TARGET_NAME).bin $(TARGET_NAME).rpt

.DEFAULT_GOAL := all
.PHONY: all install boot clean
.PRECIOUS: %.json %.blif %.asc $(GENERATED_V)
