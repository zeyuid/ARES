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
from awlsim.common.datatypehelpers import * #+cimport

from awlsim.core.instructions.main import * #+cimport
from awlsim.core.operatortypes import * #+cimport
from awlsim.core.operators import * #+cimport

#from libc.stdlib cimport abs #@cy


class AwlInsn_ITB(AwlInsn): #+cdef

	__slots__ = ()

	def __init__(self, cpu, rawInsn=None, **kwargs):
		AwlInsn.__init__(self, cpu, AwlInsn.TYPE_ITB, rawInsn, **kwargs)
		self.assertOpCount(0)

	def run(self): #+cdef
#@cy		cdef S7StatusWord s
#@cy		cdef uint32_t accu1
#@cy		cdef int32_t binval
#@cy		cdef uint32_t binvalabs
#@cy		cdef uint16_t bcd

		s = self.cpu.statusWord
		accu1 = self.cpu.accu1.get()
		binval, bcd = wordToSignedPyInt(accu1), 0
		if binval < 0:
			bcd = 0xF000
		binvalabs = abs(binval)
		if binvalabs > 999:
			s.OV, s.OS = 1, 1
			return
		bcd |= binvalabs % 10			#+suffix-u
		bcd |= ((binvalabs // 10) % 10) << 4	#+suffix-u
		bcd |= ((binvalabs // 100) % 10) << 8	#+suffix-u
		self.cpu.accu1.setWord(bcd)
		s.OV = 0
