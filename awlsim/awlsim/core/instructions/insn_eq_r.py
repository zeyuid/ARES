# -*- coding: utf-8 -*-
#
# AWL simulator - instructions
#
# Copyright 2012-2017 Michael Buesch <m@bues.ch>
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


class AwlInsn_EQ_R(AwlInsn): #+cdef

	__slots__ = ()

	def __init__(self, cpu, rawInsn=None, **kwargs):
		AwlInsn.__init__(self, cpu, AwlInsn.TYPE_EQ_R, rawInsn, **kwargs)
		self.assertOpCount(0)

	def run(self): #+cdef
#@cy		cdef S7StatusWord s
#@cy		cdef double diff

		s = self.cpu.statusWord
		if isNaN(self.cpu.accu1.getDWord()) or\
		   isNaN(self.cpu.accu2.getDWord()):
			s.A0, s.A1, s.OV, s.OS, s.STA = 1, 1, 1, 1, 0
		else:
			diff = self.cpu.accu2.getPyFloat() -\
			       self.cpu.accu1.getPyFloat()
			s.setForFloatingPoint(diff)
			s.STA = (s.A0 ^ 1) & (s.A1 ^ 1)
		s.OR, s.VKE, s.NER = 0, s.STA, 1
