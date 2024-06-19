# -*- coding: utf-8 -*-
#
# AWL simulator - FUP compiler - Inline AWL element
#
# Copyright 2017-2018 Michael Buesch <m@bues.ch>
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

from awlsim.fupcompiler.elem import *


class FupCompiler_ElemAWL(FupCompiler_Elem):
	"""FUP compiler - Inline AWL element.
	"""

	ELEM_NAME		= "Inline-AWL"
	DUMP_SHOW_CONTENT	= False

	@classmethod
	def parse(cls, grid, x, y, subType, content):
		return FupCompiler_ElemAWL(grid=grid,
					   x=x, y=y,
					   content=content)

	def __init__(self, grid, x, y, content, **kwargs):
		FupCompiler_Elem.__init__(self, grid=grid, x=x, y=y,
					  elemType=FupCompiler_Elem.TYPE_AWL,
					  subType=None, content=content,
					  **kwargs)

	def isCompileEntryPoint(self):
		return True

	def _doCompile(self):
		if not self.enabled:
			return []
		insns = []

		insns.append(self.newInsn_INLINEAWL(self.content))

		return insns
