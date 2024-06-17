# -*- coding: utf-8 -*-
#
# AWL simulator - CPU core feature specification
#
# Copyright 2012-2018 Michael Buesch <m@bues.ch>
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

from awlsim.common.util import *
from awlsim.common.enumeration import *
from awlsim.common.exceptions import *


__all__ = [
	"S7CPUSpecs",
]


class S7CPUSpecs(object): #+cdef
	"""STEP 7 CPU core specifications"""

	DEFAULT_NR_ACCUS	= 2
	DEFAULT_NR_TIMERS	= 256
	DEFAULT_NR_COUNTERS	= 256
	DEFAULT_NR_FLAGS	= 2048
	DEFAULT_NR_INPUTS	= 128
	DEFAULT_NR_OUTPUTS	= 128
	DEFAULT_NR_LOCALBYTES	= 1024
	DEFAULT_PARENSTACK_SIZE	= 7
	DEFAULT_CALLSTACK_SIZE	= 256

	__slots__ = (
		"cpu",
		"nrAccus",
		"nrTimers",
		"nrCounters",
		"nrFlags",
		"nrInputs",
		"nrOutputs",
		"nrLocalbytes",
		"parenStackSize",
		"callStackSize",
	)

	def __init__(self, cpu=None):
		self.cpu = None
		self.setNrAccus(self.DEFAULT_NR_ACCUS)
		self.setNrTimers(self.DEFAULT_NR_TIMERS)
		self.setNrCounters(self.DEFAULT_NR_COUNTERS)
		self.setNrFlags(self.DEFAULT_NR_FLAGS)
		self.setNrInputs(self.DEFAULT_NR_INPUTS)
		self.setNrOutputs(self.DEFAULT_NR_OUTPUTS)
		self.setNrLocalbytes(self.DEFAULT_NR_LOCALBYTES)
		self.setParenStackSize(self.DEFAULT_PARENSTACK_SIZE)
		self.setCallStackSize(self.DEFAULT_CALLSTACK_SIZE)
		self.cpu = cpu

	def assignFrom(self, otherCpuSpecs):
		self.setNrAccus(otherCpuSpecs.nrAccus)
		self.setNrTimers(otherCpuSpecs.nrTimers)
		self.setNrCounters(otherCpuSpecs.nrCounters)
		self.setNrFlags(otherCpuSpecs.nrFlags)
		self.setNrInputs(otherCpuSpecs.nrInputs)
		self.setNrOutputs(otherCpuSpecs.nrOutputs)
		self.setNrLocalbytes(otherCpuSpecs.nrLocalbytes)
		self.setParenStackSize(otherCpuSpecs.parenStackSize)
		self.setCallStackSize(otherCpuSpecs.callStackSize)

	def __copy__(self):
		new = self.__class__()
		new.assignFrom(self)
		new.cpu = self.cpu
		return new

	def __deepcopy__(self, memo):
		raise NotImplementedError

	def setNrAccus(self, count):
		if count not in (2, 4):
			raise AwlSimError("Invalid number of accus") #@nocov
		self.nrAccus = count
		if self.cpu:
			self.cpu.reallocate()

	def setNrTimers(self, count):
		self.nrTimers = clamp(count, 0, 0x7FFFFFFF)
		if self.cpu:
			self.cpu.reallocate()

	def setNrCounters(self, count):
		self.nrCounters = clamp(count, 0, 0x7FFFFFFF)
		if self.cpu:
			self.cpu.reallocate()

	def setNrFlags(self, count):
		self.nrFlags = clamp(count, 0, 0x7FFFFFFF)
		if self.cpu:
			self.cpu.reallocate()

	def setNrInputs(self, count):
		self.nrInputs = clamp(count, 0, 0x7FFFFFFF)
		if self.cpu:
			self.cpu.reallocate()

	def setNrOutputs(self, count):
		self.nrOutputs = clamp(count, 0, 0x7FFFFFFF)
		if self.cpu:
			self.cpu.reallocate()

	def setNrLocalbytes(self, count):
		self.nrLocalbytes = clamp(count, 0, 0x7FFFFFFF)
		if self.cpu:
			self.cpu.reallocate()

	def setParenStackSize(self, count):
		self.parenStackSize = clamp(count, 0, 0x7FFF)
		if self.cpu:
			self.cpu.reallocate()

	def setCallStackSize(self, count):
		self.callStackSize = clamp(count, 1, 0x7FFFFFFF)
		if self.cpu:
			self.cpu.reallocate()
