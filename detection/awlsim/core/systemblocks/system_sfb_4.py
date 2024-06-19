# -*- coding: utf-8 -*-
#
# AWL simulator - SFBs
#
# Copyright 2014-2018 Michael Buesch <m@bues.ch>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from __future__ import division, absolute_import, print_function, unicode_literals
#from awlsim.common.cython_support cimport * #@cy
from awlsim.common.compat import *

from awlsim.common.datatypehelpers import * #+cimport
from awlsim.common.exceptions import *
from awlsim.common.util import *

from awlsim.core.systemblocks.systemblocks import * #+cimport
from awlsim.core.blockinterface import *
from awlsim.core.datatypes import *


class SFB4(SFB): #+cdef
	name = (4, "TON", "IEC 1131-3 delayed set")

	interfaceFields = {
		BlockInterfaceField.FTYPE_IN	: (
			BlockInterfaceField(name="IN", dataType="BOOL"),
			BlockInterfaceField(name="PT", dataType="TIME"),
		),
		BlockInterfaceField.FTYPE_OUT	: (
			BlockInterfaceField(name="Q", dataType="BOOL"),
			BlockInterfaceField(name="ET", dataType="TIME"),
		),
		BlockInterfaceField.FTYPE_STAT	: (
			BlockInterfaceField(name="STATE", dataType="BYTE"),
			BlockInterfaceField(name="STIME", dataType="TIME"),
			BlockInterfaceField(name="ATIME", dataType="TIME"),
		),
	}

	# STATE bits
	STATE_RUNNING		= 1 << 0
	STATE_FINISHED		= 1 << 1

	def run(self): #+cpdef
#@cy		cdef S7StatusWord s

		s = self.cpu.statusWord
		s.BIE = 1

		PT = dwordToSignedPyInt(AwlMemoryObject_asScalar(
			self.fetchInterfaceFieldByName("PT")))
		if PT <= 0:
			# Invalid PT. Abort and reset state.
			# A PT of zero is used to reset the timer.
			if PT == 0:
				# S7 resets IN here, for whatever weird reason.
				self.storeInterfaceFieldByName("IN",
					make_AwlMemoryObject_fromScalar(0, 1))
			else:
				# Negative PT. This is an error.
				s.BIE = 0
			self.storeInterfaceFieldByName("Q",
				make_AwlMemoryObject_fromScalar(0, 1))
			self.storeInterfaceFieldByName("ET",
				make_AwlMemoryObject_fromScalar(0, 32))
			self.storeInterfaceFieldByName("STATE",
				make_AwlMemoryObject_fromScalar(0, 8))
			return

		# Get the current time, as S7-time value (31-bit milliseconds)
		ATIME = self.cpu.now_TIME

		STATE = AwlMemoryObject_asScalar(self.fetchInterfaceFieldByName("STATE"))
		IN = AwlMemoryObject_asScalar(self.fetchInterfaceFieldByName("IN"))
		if IN:
			if not (STATE & (self.STATE_RUNNING | self.STATE_FINISHED)):
				# IN is true and we are not running, yet.
				# Start the timer.
				self.storeInterfaceFieldByName("STIME",
					make_AwlMemoryObject_fromScalar(ATIME, 32))
				STATE |= self.STATE_RUNNING
				self.storeInterfaceFieldByName("STATE",
					make_AwlMemoryObject_fromScalar(STATE, 8))
		else:
			# IN is false. Shut down everything.
			STATE &= ~(self.STATE_FINISHED | self.STATE_RUNNING)
			self.storeInterfaceFieldByName("STATE",
				make_AwlMemoryObject_fromScalar(STATE, 8))
			self.storeInterfaceFieldByName("ET",
				make_AwlMemoryObject_fromScalar(0, 32))
			self.storeInterfaceFieldByName("Q",
				make_AwlMemoryObject_fromScalar(0, 1))
		if STATE & self.STATE_RUNNING:
			# The timer is running.
			STIME = AwlMemoryObject_asScalar(
				self.fetchInterfaceFieldByName("STIME"))
			self.storeInterfaceFieldByName("ATIME",
				make_AwlMemoryObject_fromScalar(ATIME, 32))
			ET = (ATIME - STIME) & 0x7FFFFFFF
			if ET >= PT:
				# Time elapsed.
				ET = PT
				self.storeInterfaceFieldByName("Q",
					make_AwlMemoryObject_fromScalar(1, 1))
				STATE &= ~self.STATE_RUNNING
				STATE |= self.STATE_FINISHED
				self.storeInterfaceFieldByName("STATE",
					make_AwlMemoryObject_fromScalar(STATE, 8))
			else:
				self.storeInterfaceFieldByName("Q",
					make_AwlMemoryObject_fromScalar(0, 1))
			self.storeInterfaceFieldByName("ET",
				make_AwlMemoryObject_fromScalar(ET, 32))
