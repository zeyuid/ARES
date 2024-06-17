# -*- coding: utf-8 -*-
#
# AWL simulator - instructions
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

from awlsim.common.exceptions import *

from awlsim.core.instructions.main import * #+cimport
from awlsim.core.operatortypes import * #+cimport
from awlsim.core.operators import * #+cimport


class AwlInsn_RRD(AwlInsn): #+cdef

	__slots__ = ()

	def __init__(self, cpu, rawInsn=None, **kwargs):
		AwlInsn.__init__(self, cpu, AwlInsn.TYPE_RRD, rawInsn, **kwargs)
		self.assertOpCount((0, 1))
		if self.opCount:
			self.op0.assertType(AwlOperatorTypes.IMM, 0, 255)

	def run(self): #+cdef
#@cy		cdef S7StatusWord s
#@cy		cdef uint64_t accu1
#@cy		cdef uint32_t count

		s = self.cpu.statusWord
		accu1 = self.cpu.accu1.getDWord()
		if self.opCount:
			count = self.op0.immediate
		else:
			count = self.cpu.accu2.getByte()
		if count <= 0:
			return
		if count > 32:
			count = 32
		accu1 &= 0xFFFFFFFF							#+suffix-u
		accu1 = ((accu1 >> count) | (accu1 << (32 - count))) & 0xFFFFFFFF	#+suffix-u
		self.cpu.accu1.set(accu1)
		s.A0, s.A1, s.OV = 0, (accu1 >> 31) & 1, 0
