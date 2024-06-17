# -*- coding: utf-8 -*-
#
# PROFIBUS DP - Master
#
# Copyright (c) 2013-2020 Michael Buesch <m@bues.ch>
#
# Licensed under the terms of the GNU General Public License version 2,
# or (at your option) any later version.
#

from __future__ import division, absolute_import, print_function, unicode_literals
from pyprofibus.compat import *

from pyprofibus.fdl import *
from pyprofibus.dp import *
from pyprofibus.util import *

import gc
import math

__all__ = [
	"DpSlaveDesc",
	"DPM1",
	"DPM2",
]

class DpSlaveState(object):
	"""Run time state of a DP slave that is managed by a DPM instance.
	"""

	_STATE_INVALID	= -1
	STATE_INIT	= 0 # Initialize
	STATE_WDIAG	= 1 # Wait for diagnosis
	STATE_WPRM	= 2 # Wait for Prm telegram
	STATE_WCFG	= 3 # Wait for Cfg telegram
	STATE_WDXRDY	= 4 # Wait for Data_Exchange ready
	STATE_DX	= 5 # Data_Exchange

	state2name = {
		_STATE_INVALID	: "invalid",
		STATE_INIT	: "init",
		STATE_WDIAG	: "wait for diag",
		STATE_WPRM	: "wait for Prm",
		STATE_WCFG	: "wait for Cfg",
		STATE_WDXRDY	: "wait for Data_Exchange-ready",
		STATE_DX	: "Data_Exchange",
	}

	# State timeouts in seconds
	stateTimeLimits = {
		STATE_INIT	: TimeLimit.UNLIMITED,
		STATE_WDIAG	: 1.0,
		STATE_WPRM	: 0.5,
		STATE_WCFG	: 0.5,
		STATE_WDXRDY	: 1.0,
		STATE_DX	: 0.5,
	}

	__slots__ = (
		"__nextState",
		"__prevState",
		"__state",
		"__stateTimeout",
		"dxStartTime",
		"faultDeb",
		"fcb",
		"inData",
		"master",
		"outData",
		"pendingReq",
		"pendingReqTimeout",
		"rxQueue",
		"shortAckReceived",
		"slaveDesc",
	)

	def __init__(self, master, slaveDesc):
		self.master = master
		self.slaveDesc = slaveDesc

		# Fault counter
		self.faultDeb = FaultDebouncer()

		self.__state = self._STATE_INVALID
		self.__nextState = self._STATE_INVALID
		self.__prevState = self._STATE_INVALID
		self.__stateTimeout = TimeLimit()
		self.setState(self.STATE_INIT)
		self.applyState()

		# Context for FC-Bit toggeling
		self.fcb = FdlFCB()

		# Currently running request telegram
		self.pendingReq = None
		self.pendingReqTimeout = TimeLimit()
		self.shortAckReceived = False

		# Data_Exchange context
		self.dxStartTime = 0.0

		# Received telegrams
		self.rxQueue = []

		# In/Out user data
		self.outData = None
		self.inData = None

	def getRxQueue(self):
		rxQueue = self.rxQueue
		self.rxQueue = []
		return rxQueue

	def flushRxQueue(self):
		self.rxQueue = []

	def getState(self):
		return self.__state

	def getNextState(self):
		return self.__nextState

	def setState(self, state, stateTimeLimit=None):
		if stateTimeLimit is None:
			stateTimeLimit = self.stateTimeLimits[state]
		self.__nextState = state
		self.__stateTimeout.start(stateTimeLimit)
		self.master.phy.clearTxQueueAddr(self.slaveDesc.slaveAddr)
		self.master._releaseSlave(self)

	def applyState(self):
		# Enter the new state
		self.__prevState, self.__state = self.__state, self.__nextState

		# Handle state switch
		if self.stateJustEntered():
			self.pendingReq = None

	def stateJustEntered(self):
		# Returns True, if the state was just entered.
		return self.__prevState != self.__state

	def stateIsChanging(self):
		# Returns True, if the state was just changed.
		return self.__nextState != self.__state

	def restartStateTimeout(self, timeout = None):
		self.__stateTimeout.start(timeout)

	def stateHasTimeout(self):
		return self.__stateTimeout.exceed()

class DpSlaveDesc(object):
	"""Static descriptor data of a DP slave that
	is managed by a DPM instance.
	"""

	__slots__ = (
		"index",
		"name",
		"chkCfgTelegram",
		"dpm",
		"gsd",
		"identNumber",
		"setPrmTelegram",
		"setPrmTelegram",
		"slaveAddr",
		"slaveConf",
		"userData",
	)

	def __init__(self,
		     gsd,
		     slaveAddr,
		     slaveConf=None):
		self.gsd = gsd
		self.slaveAddr = slaveAddr
		self.slaveConf = slaveConf
		self.identNumber = gsd.getIdentNumber() if gsd else 0
		self.dpm = None
		self.name = None
		self.index = None
		self.userData = {} # For use by application code.

		# Prepare a Set_Prm telegram.
		self.setPrmTelegram = DpTelegram_SetPrm_Req(
					da = self.slaveAddr,
					sa = None)
		self.setPrmTelegram.identNumber = self.identNumber

		# Prepare a Chk_Cfg telegram.
		self.chkCfgTelegram = DpTelegram_ChkCfg_Req(
					da = self.slaveAddr,
					sa = None)

	def setCfgDataElements(self, cfgDataElements):
		"""Sets DpCfgDataElement()s from the specified list
		in the Chk_Cfg telegram.
		"""
		if cfgDataElements is not None:
			self.chkCfgTelegram.clearCfgDataElements()
			for cfgDataElement in cfgDataElements:
				self.chkCfgTelegram.addCfgDataElement(cfgDataElement)

	def setUserPrmData(self, userPrmData):
		"""Sets the User_Prm_Data of the Set_Prm telegram.
		"""
		if userPrmData is not None:
			self.setPrmTelegram.clearUserPrmData()
			self.setPrmTelegram.addUserPrmData(userPrmData)

	def setSyncMode(self, enabled):
		"""Enable/disable sync-mode.
		Must be called before parameterisation."""

		if enabled:
			self.setPrmTelegram.stationStatus |= DpTelegram_SetPrm_Req.STA_SYNC
		else:
			self.setPrmTelegram.stationStatus &= ~DpTelegram_SetPrm_Req.STA_SYNC

	def setFreezeMode(self, enabled):
		"""Enable/disable freeze-mode.
		Must be called before parameterisation."""

		if enabled:
			self.setPrmTelegram.stationStatus |= DpTelegram_SetPrm_Req.STA_FREEZE
		else:
			self.setPrmTelegram.stationStatus &= ~DpTelegram_SetPrm_Req.STA_FREEZE

	def setGroupMask(self, groupMask):
		"""Assign the slave to one or more groups.
		Must be called before parameterisation."""

		self.setPrmTelegram.groupIdent = groupMask

	def setWatchdog(self, timeoutMS):
		"""Set the watchdog timeout (in milliseconds).
		If timeoutMS is 0, the watchdog is disabled."""

		if timeoutMS <= 0:
			# Disable watchdog
			self.setPrmTelegram.stationStatus &= ~DpTelegram_SetPrm_Req.STA_WD
			return

		# Enable watchdog
		self.setPrmTelegram.stationStatus |= DpTelegram_SetPrm_Req.STA_WD

		# Set timeout factors
		fact1 = timeoutMS / 10
		fact2 = 1
		while fact1 > 255:
			fact2 *= 2
			fact1 /= 2
			if fact2 > 255:
				raise DpError("Watchdog timeout %d is too big" % timeoutMS)
		fact1 = min(255, int(math.ceil(fact1)))
		self.setPrmTelegram.wdFact1 = fact1
		self.setPrmTelegram.wdFact2 = fact2

	def setOutData(self, outData):
		self.dpm.setSlaveOutData(self, outData)

	def getInData(self):
		return self.dpm.getSlaveInData(self)

	def __repr__(self):
		return "DpSlaveDesc(identNumber=%s, slaveAddr=%d)" %\
			(intToHex(self.identNumber), self.slaveAddr)

class DpMaster(object):
	__slots__ = (
		"__runTimer",
		"__runCount",
		"__haveToken",
		"__runNextSlaveIndex",
		"__slaveDescs",
		"__slaveDescsList",
		"__slaveStates",
		"__slowDown",
		"__slowDownFact",
		"__slowDownUntil",
		"debug",
		"dpTrans",
		"dpmClass",
		"fdlTrans",
		"masterAddr",
		"phy",
	)

	def __init__(self, dpmClass, phy, masterAddr, debug=False):
		self.dpmClass = dpmClass
		self.phy = phy
		self.masterAddr = masterAddr
		self.debug = debug

		self.__runTimer = monotonic_time()
		self.__runCount = 0

		# Create the transceivers
		self.fdlTrans = FdlTransceiver(self.phy)
		self.dpTrans = DpTransceiver(self.fdlTrans, thisIsMaster=True)

		mcastSlaveDesc = DpSlaveDesc(gsd=None,
					     slaveAddr=FdlTelegram.ADDRESS_MCAST)
		mcastSlave = DpSlaveState(self, mcastSlaveDesc)

		self.__slaveDescs = {
			FdlTelegram.ADDRESS_MCAST : mcastSlaveDesc,
		}
		self.__slaveStates = {
			FdlTelegram.ADDRESS_MCAST : mcastSlave,
		}
		self.__slaveDescsList = []
		self.__runNextSlaveIndex = 0

		# Do we have the token?
		self.__haveToken = True

		self.__slowDown = False
		self.__slowDownUntil = monotonic_time()
		self.__slowDownFact = 1

	def __debugMsg(self, msg):
		if self.debug:
			print("DPM%d: %s" % (self.dpmClass, msg))

	def __errorMsg(self, msg):
		print("DPM%d:  >ERROR<  %s" % (self.dpmClass, msg))

	def __masterSlowDown(self):
		"""A severe communication error occurred.
		Slow down the state machine a bit.
		"""
		self.__slowDown = True
		self.__slowDownUntil = monotonic_time() + (0.01 * self.__slowDownFact)
		self.__debugMsg("Slow down factor = %d" % self.__slowDownFact)
		self.__slowDownFact = min(self.__slowDownFact + 1, 10)

	def destroy(self):
		if self.phy:
			self.phy.close()
			self.phy = None

	def addSlave(self, slaveDesc):
		"""Register a slave."""

		slaveAddr = slaveDesc.slaveAddr
		if slaveAddr in self.__slaveDescs or\
		   slaveAddr in self.__slaveStates:
			raise DpError("Slave %d is already registered." % slaveAddr)
		slaveDesc.dpm = self
		self.__slaveDescs[slaveAddr] = slaveDesc
		self.__slaveStates[slaveAddr] = DpSlaveState(self, slaveDesc)

		# Rebuild the slave desc list.
		self.__slaveDescsList = [
			desc
			for addr, desc in sorted(self.__slaveDescs.items(),
						 key=lambda x: x[0])
			if addr != FdlTelegram.ADDRESS_MCAST
		]

		self.__runNextSlaveIndex = 0

	def getSlaveList(self):
		"""Get a list of registered DpSlaveDescs, sorted by address.
		"""
		return self.__slaveDescsList

	def __send(self, slave, telegram, timeout):
		"""Asynchronously send a telegram to a slave.
		"""
		slave.pendingReq = telegram
		slave.shortAckReceived = False
		try:
			if FdlTelegram.checkType(telegram):
				transceiver = self.fdlTrans
			else:
				transceiver = self.dpTrans
			transceiver.send(fcb=slave.fcb,
					 telegram=telegram)
		except ProfibusError as e:
			slave.pendingReq = None
			self.__masterSlowDown()
			self.__debugMsg(str(e))
			return False
		self.__slowDownFact = 1
		slave.pendingReqTimeout.start(timeout)
		return True

	def _releaseSlave(self, slave):
		self.phy.releaseBus()

	def __runSlave_init(self, slave):
		if slave.stateJustEntered():
			self.__debugMsg("Trying to initialize slave %d..." % (
				slave.slaveDesc.slaveAddr))
			slave.flushRxQueue()
		else:
			for telegram in slave.getRxQueue():
				if telegram.fc is not None:
					slave.pendingReq = None
					stype = telegram.fc & FdlTelegram.FC_STYPE_MASK
					if telegram.fc & FdlTelegram.FC_REQ:
						self.__debugMsg("Slave %d replied with "
								"request bit set." %\
								slave.slaveDesc.slaveAddr)
					elif stype != FdlTelegram.FC_SLAVE:
						self.__debugMsg("Device %d is not a slave. "
								"Detected type: 0x%02X" % (
								slave.slaveDesc.slaveAddr,
								stype))
					else:
						slave.setState(slave.STATE_WDIAG)
						return None
				else:
					self.__debugMsg("Slave %d replied with a "
						"weird telegram:\n%s" % str(telegram))

		if (not slave.pendingReq or
		    slave.pendingReqTimeout.exceed()):
			# Reset fault debounce counter.
			slave.faultDeb.reset()

			# Disable the FCB bit.
			slave.fcb.enableFCB(False)

			ok = self.__send(slave,
					 telegram=FdlTelegram_FdlStat_Req(
						da=slave.slaveDesc.slaveAddr,
						sa=self.masterAddr),
					 timeout=0.01)
			if not ok:
				self.__debugMsg("FdlStat_Req failed")
				return None
		return None

	def __runSlave_waitDiag(self, slave):
		if slave.stateJustEntered():
			self.__debugMsg("Requesting Slave_Diag from slave %d..." %\
				slave.slaveDesc.slaveAddr)
			slave.flushRxQueue()
		else:
			for telegram in slave.getRxQueue():
				if DpTelegram_SlaveDiag_Con.checkType(telegram):
					slave.setState(slave.STATE_WPRM)
					return None
				else:
					self.__debugMsg("Received spurious "
						"telegram:\n%s" % str(telegram))

		if (not slave.pendingReq or
		    slave.pendingReqTimeout.exceed()):
			# Enable the FCB bit.
			slave.fcb.enableFCB(True)

			# Send a SlaveDiag request
			ok = self.__send(slave,
					 telegram=DpTelegram_SlaveDiag_Req(
						da=slave.slaveDesc.slaveAddr,
						sa=self.masterAddr),
					 timeout=0.05)
			if not ok:
				self.__debugMsg("SlaveDiag_Req failed")
				return None
		return None

	def __runSlave_waitPrm(self, slave):
		if slave.stateJustEntered():
			self.__debugMsg("Sending Set_Prm to slave %d..." %\
				slave.slaveDesc.slaveAddr)
			slave.flushRxQueue()
		else:
			if slave.shortAckReceived:
				slave.fcb.handleReply()
				slave.setState(slave.STATE_WCFG)
				return None

		if (not slave.pendingReq or
		    slave.pendingReqTimeout.exceed()):
			# Send a Set_Prm request
			slave.slaveDesc.setPrmTelegram.sa = self.masterAddr
			ok = self.__send(slave,
					 telegram=slave.slaveDesc.setPrmTelegram,
					 timeout=0.05)
			if not ok:
				self.__debugMsg("Set_Prm failed")
				return None
		return None

	def __runSlave_waitCfg(self, slave):
		if slave.stateJustEntered():
			self.__debugMsg("Sending Chk_Cfg to slave %d..." %\
				slave.slaveDesc.slaveAddr)
			slave.flushRxQueue()
		else:
			if slave.shortAckReceived:
				slave.fcb.handleReply()
				slave.setState(slave.STATE_WDXRDY)

		if (not slave.pendingReq or
		    slave.pendingReqTimeout.exceed()):
			slave.slaveDesc.chkCfgTelegram.sa = self.masterAddr
			ok = self.__send(slave,
					 telegram=slave.slaveDesc.chkCfgTelegram,
					 timeout=0.05)
			if not ok:
				self.__debugMsg("Chk_Cfg failed")
				return None
		return None

	def __runSlave_waitDxRdy(self, slave):
		if slave.stateJustEntered():
			self.__debugMsg("Requesting Slave_Diag (WDXRDY) from slave %d..." %\
				slave.slaveDesc.slaveAddr)
			slave.flushRxQueue()
		else:
			for telegram in slave.getRxQueue():
				if DpTelegram_SlaveDiag_Con.checkType(telegram):
					if telegram.notExist():
						self.__errorMsg("Slave %d is not reachable "
							"via this line." %\
							slave.slaveDesc.slaveAddr)
					if telegram.cfgFault():
						self.__errorMsg("Slave %d reports a faulty "
							"configuration (Chk_Cfg)." %\
							slave.slaveDesc.slaveAddr)
					if telegram.prmFault():
						self.__errorMsg("Slave %d reports a faulty "
							"parameterization (Set_Prm)." %\
							slave.slaveDesc.slaveAddr)
					if telegram.isNotSupp():
						self.__errorMsg("Slave %d replied with "
							"\"function not supported\". "
							"The parameters should be checked "
							"(Set_Prm)." %\
							slave.slaveDesc.slaveAddr)
					if telegram.masterLock():
						self.__errorMsg("Slave %d is already controlled "
							"(locked to) another DP-master." %\
							slave.slaveDesc.slaveAddr)
					if not telegram.hasOnebit():
						self.__debugMsg("Slave %d diagnostic "
							"always-one-bit is zero." %\
							slave.slaveDesc.slaveAddr)

					if telegram.hasExtDiag():
						pass#TODO turn on red DIAG-LED
					if telegram.isReadyDataEx():
						slave.setState(slave.STATE_DX)
						return None
					elif telegram.needsNewPrmCfg():
						slave.setState(slave.STATE_INIT)
						return None
					break
				else:
					self.__debugMsg("Received spurious "
						"telegram:\n%s" % str(telegram))

		if (not slave.pendingReq or
		    slave.pendingReqTimeout.exceed()):
			ok = self.__send(slave,
					 telegram=DpTelegram_SlaveDiag_Req(
						da=slave.slaveDesc.slaveAddr,
						sa=self.masterAddr),
					 timeout=0.05)
			if not ok:
				self.__debugMsg("SlaveDiag_Req failed")
				return None
		return None

	def __runSlave_dataExchange(self, slave):
		#TODO: add support for in/out-only slaves
		dataExInData = None

		if slave.stateJustEntered():
			self.__debugMsg("Initialization finished. "
				"Running Data_Exchange with slave %d..." %\
				slave.slaveDesc.slaveAddr)
			slave.flushRxQueue()
			slave.dxStartTime = monotonic_time()

		if slave.pendingReq:
			for telegram in slave.getRxQueue():
				if not DpTelegram_DataExchange_Con.checkType(telegram):
					self.__debugMsg("Ignoring telegram in "
						"DataExchange with slave %d:\n%s" %(
						slave.slaveDesc.slaveAddr, str(telegram)))
					slave.faultDeb.fault()
					continue
				resFunc = telegram.fc & FdlTelegram.FC_RESFUNC_MASK
				if resFunc in (FdlTelegram.FC_DH,
					       FdlTelegram.FC_RDH,):
					self.__debugMsg("Slave %d requested diagnostics." %\
						slave.slaveDesc.slaveAddr)
					slave.setState(slave.STATE_WDXRDY, 0.2)
				elif resFunc == FdlTelegram.FC_RS:
					raise DpError("Service not active "
						"on slave %d" % slave.slaveDesc.slaveAddr)
				dataExInData = telegram.getDU()

			if dataExInData is None:
				if slave.pendingReqTimeout.exceed():
					self.__debugMsg("Data_Exchange timeout with slave %d" % (
							slave.slaveDesc.slaveAddr))
					slave.faultDeb.fault()
					slave.pendingReq = None
			else:
				# We received some data.
				slave.pendingReq = None
				slave.faultDeb.ok()
				slave.restartStateTimeout()
				self._releaseSlave(slave)
		else:
			# Send the out data telegram, if any.
			outData = slave.outData
			if outData is not None:
				ok = self.__send(slave,
						 telegram=DpTelegram_DataExchange_Req(
							da=slave.slaveDesc.slaveAddr,
							sa=self.masterAddr,
							du=outData),
						 timeout=0.1)
				if not ok:
					self.__debugMsg("DataExchange_Req failed")
					return None
				# We sent it. Reset the data.
				slave.outData = None

		faultCount = slave.faultDeb.get()
		if faultCount >= 5:
			# communication lost
			self.__debugMsg("Communication lost in Data_Exchange.")
			slave.setState(slave.STATE_INIT)
		elif faultCount >= 3 and monotonic_time() >= slave.dxStartTime + 0.2:
			# Diagnose the slave
			self.__debugMsg("Many errors in Data_Exchange. "
				"Requesting diagnostic information...")
			slave.setState(slave.STATE_WDXRDY, 0.2)

		return dataExInData

	__slaveStateHandlers = {
		DpSlaveState.STATE_INIT		: __runSlave_init,
		DpSlaveState.STATE_WDIAG	: __runSlave_waitDiag,
		DpSlaveState.STATE_WPRM		: __runSlave_waitPrm,
		DpSlaveState.STATE_WCFG		: __runSlave_waitCfg,
		DpSlaveState.STATE_WDXRDY	: __runSlave_waitDxRdy,
		DpSlaveState.STATE_DX		: __runSlave_dataExchange,
	}

	def __runSlave(self, slave):
		self.__pollRx()
		if not self.__haveToken:
			return None

		if slave.stateHasTimeout():
			self.__debugMsg("State machine timeout! "
				"Trying to re-initializing slave %d..." %\
				slave.slaveDesc.slaveAddr)
			slave.setState(slave.STATE_INIT)
			dataExInData = None
		else:
			handler = self.__slaveStateHandlers[slave.getState()]
			dataExInData = handler(self, slave)

			if slave.stateIsChanging():
				self.__debugMsg("slave[%02X].state --> '%s'" % (
					slave.slaveDesc.slaveAddr,
					slave.state2name[slave.getNextState()]))
		slave.applyState()

		return dataExInData

	def __pollRx(self):
		try:
			ok, telegram = self.dpTrans.poll()
		except ProfibusError as e:
			self.__debugMsg("RX error: %s" % str(e))
			return
		if ok and telegram:
			if FdlTelegram_token.checkType(telegram):
				pass#TODO handle token
			elif FdlTelegram_ack.checkType(telegram):
				for addr, slave in self.__slaveStates.items():
					if addr != FdlTelegram.ADDRESS_MCAST:
						slave.shortAckReceived = True
			elif telegram.da == FdlTelegram.ADDRESS_MCAST:
				self.__handleMcastTelegram(telegram)
			elif telegram.da == self.masterAddr:
				if telegram.sa in self.__slaveStates:
					slave = self.__slaveStates[telegram.sa]
					slave.rxQueue.append(telegram)
					slave.fcb.handleReply()
				else:
					self.__debugMsg("Received telegram from "
						"unknown station %d:\n%s" %(
						telegram.sa, str(telegram)))
			else:
				self.__debugMsg("Received telegram for "
					"foreign station:\n%s" % str(telegram))
		else:
			if telegram:
				self.__debugMsg("Received corrupt "
					"telegram:\n%s" % str(telegram))

	def __handleMcastTelegram(self, telegram):
		self.__debugMsg("Received multicast telegram:\n%s" % str(telegram))
		pass#TODO

	def run(self):
		"""Run the DP-Master state machine.
		"""
		if self.debug:
			self.__runCount += 1
			now = monotonic_time()
			if now >= self.__runTimer + 10.0:
				cps = self.__runCount / (now - self.__runTimer)
				self.__debugMsg("State machine calls: "
						"%.1f /s = %.3f s/call" % (
						cps, 1.0 / cps))
				self.__runTimer = now
				self.__runCount = 0

		if self.__slowDown:
			# Master slowdown is active.
			# Do not run state machine until the end of the slowdown.
			if monotonic_time() < self.__slowDownUntil:
				return None
			self.__slowDown = False

		slaveDescsList = self.__slaveDescsList
		runNextSlaveIndex = self.__runNextSlaveIndex

		if not slaveDescsList:
			return None

		slaveDesc = slaveDescsList[runNextSlaveIndex]
		self.__runNextSlaveIndex = (runNextSlaveIndex + 1) % len(slaveDescsList)

		slave = self.__slaveStates[slaveDesc.slaveAddr]
		slave.inData = self.__runSlave(slave)

		return slaveDesc

	def setSlaveOutData(self, slaveDesc, outData):
		"""Set the out-data that will be sent the
		next time we are able to send something to that slave.
		"""
		slave = self.__slaveStates[slaveDesc.slaveAddr]
		slave.outData = outData

	def getSlaveInData(self, slaveDesc):
		"""Get the latest received in-data.
		Returns None, if there was no received data.
		"""
		slave = self.__slaveStates[slaveDesc.slaveAddr]
		inData = slave.inData
		slave.inData = None
		return inData

	def initialize(self):
		"""Initialize the DPM."""

		# Initialize the RX filter
		self.fdlTrans.setRXFilter([self.masterAddr,
					   FdlTelegram.ADDRESS_MCAST])
		# Free memory
		gc.collect()

	def __syncFreezeHelper(self, groupMask, controlCommand):
		slave = self.__slaveStates[FdlTelegram.ADDRESS_MCAST]
		globCtl = DpTelegram_GlobalControl(da = FdlTelegram.ADDRESS_MCAST,
						   sa = self.masterAddr)
		globCtl.controlCommand |= controlCommand
		globCtl.groupSelect = groupMask & 0xFF
		self.dpTrans.send(fcb = slave.fcb,
				  telegram = globCtl)

	def syncMode(self, groupMask):
		"""Set SYNC-mode on the specified groupMask.
		If groupMask is 0, all slaves are addressed."""

		self.__syncFreezeHelper(groupMask, DpTelegram_GlobalControl.CCMD_SYNC)

	def syncModeCancel(self, groupMask):
		"""Cancel SYNC-mode on the specified groupMask.
		If groupMask is 0, all slaves are addressed."""

		self.__syncFreezeHelper(groupMask, DpTelegram_GlobalControl.CCMD_UNSYNC)

	def freezeMode(self, groupMask):
		"""Set FREEZE-mode on the specified groupMask.
		If groupMask is 0, all slaves are addressed."""

		self.__syncFreezeHelper(groupMask, DpTelegram_GlobalControl.CCMD_FREEZE)

	def freezeModeCancel(self, groupMask):
		"""Cancel FREEZE-mode on the specified groupMask.
		If groupMask is 0, all slaves are addressed."""

		self.__syncFreezeHelper(groupMask, DpTelegram_GlobalControl.CCMD_UNFREEZE)

class DPM1(DpMaster):
	def __init__(self, phy, masterAddr, debug=False):
		DpMaster.__init__(self, dpmClass=1, phy=phy,
			masterAddr=masterAddr,
			debug=debug)

class DPM2(DpMaster):
	def __init__(self, phy, masterAddr, debug=False):
		DpMaster.__init__(self, dpmClass=2, phy=phy,
			masterAddr=masterAddr,
			debug=debug)
