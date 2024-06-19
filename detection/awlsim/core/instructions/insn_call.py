# -*- coding: utf-8 -*-
#
# AWL simulator - instructions
#
# Copyright 2012-2019 Michael Buesch <m@bues.ch>
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


class AwlInsn_AbstractCall(AwlInsn): #+cdef

	__slots__ = ()

	def staticSanityChecks(self):
#@cy		cdef AwlParamAssign param

		if self.opCount == 1:
			# "CALL FC/SFC" or
			# "CALL #MULTIINSTANCE" or
			# "UC/CC FC/SFC/FB/SFB"
			blockOper = self.op0

			if blockOper.operType == AwlOperatorTypes.BLKREF_FC:
				codeBlock = self.cpu.getFC(blockOper.offset.byteOffset)
				if not codeBlock:
					raise AwlSimError("Called FC not found",
						rawInsn=self.getRawInsn())
			elif blockOper.operType == AwlOperatorTypes.BLKREF_SFC:
				codeBlock = self.cpu.getSFC(blockOper.offset.byteOffset)
				if not codeBlock:
					raise AwlSimError("SFC %d not implemented, yet" %\
						blockOper.offset.byteOffset,
						rawInsn=self.getRawInsn())
			elif blockOper.operType == AwlOperatorTypes.BLKREF_FB:
				if self.insnType == AwlInsn.TYPE_CALL:
					raise AwlSimError("Missing DB in function "
						"block call",
						rawInsn=self.getRawInsn())
				codeBlock = self.cpu.getFB(blockOper.offset.byteOffset)
				if not codeBlock:
					raise AwlSimError("Called FB not found",
						rawInsn=self.getRawInsn())
			elif blockOper.operType == AwlOperatorTypes.BLKREF_SFB:
				if self.insnType == AwlInsn.TYPE_CALL:
					raise AwlSimError("Missing DB in system function "
						"block call",
						rawInsn=self.getRawInsn())
				codeBlock = self.cpu.getSFB(blockOper.offset.byteOffset)
				if not codeBlock:
					raise AwlSimError("SFB %d not implemented, yet" %\
						blockOper.offset.byteOffset,
						rawInsn=self.getRawInsn())
			elif blockOper.operType == AwlOperatorTypes.INDIRECT:
				# Indirect call. (like UC FC[MW 0])
				codeBlock = None
			elif blockOper.operType in (AwlOperatorTypes.MULTI_FB, AwlOperatorTypes.MULTI_SFB):
				# Multi instance call (like CALL #FOO)
				if blockOper.operType == AwlOperatorTypes.MULTI_FB:
					codeBlock = self.cpu.getFB(blockOper.offset.fbNumber)
					if not codeBlock:
						pass#TODO
				else:
					codeBlock = self.cpu.getSFB(blockOper.offset.fbNumber)
					if not codeBlock:
						pass#TODO
			else:
				raise AwlSimError("Invalid CALL operand",
					rawInsn=self.getRawInsn())

			if self.insnType == AwlInsn.TYPE_CALL and\
			   codeBlock and\
			   codeBlock.isFC and\
			   codeBlock.interface.interfaceFieldCount != len(self.params):
				raise AwlSimError("Call interface mismatch. "
					"Passed %d parameters, but expected %d.\n"
					"====  The block interface is:\n%s\n====" %\
					(len(self.params), codeBlock.interface.interfaceFieldCount,
					 str(codeBlock.interface)),
					rawInsn=self.getRawInsn())
		elif self.opCount == 2:
			# "CALL FB/SFB"
			blockOper = self.op0
			dbOper = self.op1

			if dbOper.operType != AwlOperatorTypes.BLKREF_DB:
				raise AwlSimError("Second CALL operand is "
					"not a DB operand.",
					rawInsn=self.getRawInsn())
			db = self.cpu.getDB(dbOper.offset.byteOffset)
			if not db:
				raise AwlSimError("DB used in FB call not found",
					rawInsn=self.getRawInsn())
			if not db.isInstanceDB():
				raise AwlSimError("DB %d is not an instance DB" %\
					dbOper.offset.byteOffset,
					rawInsn=self.getRawInsn())

			if blockOper.operType == AwlOperatorTypes.BLKREF_FB:
				fb = self.cpu.getFB(blockOper.offset.byteOffset)
				if not fb:
					raise AwlSimError("Called FB not found",
						rawInsn=self.getRawInsn())
				# TODO check if this is an FB-DB
				pass#TODO
			elif blockOper.operType == AwlOperatorTypes.BLKREF_SFB:
				fb = self.cpu.getSFB(blockOper.offset.byteOffset)
				if not fb:
					raise AwlSimError("SFB %d not implemented, yet" %\
						blockOper.offset.byteOffset,
						rawInsn=self.getRawInsn())
				# TODO check if this is an SFB-DB
				pass#TODO
			elif blockOper.operType == AwlOperatorTypes.BLKREF_FC or\
			     blockOper.operType == AwlOperatorTypes.BLKREF_SFC:
				raise AwlSimError("Calling function, but "
					"a DB was specified.",
					rawInsn=self.getRawInsn())
			else:
				raise AwlSimError("Invalid CALL operand",
					rawInsn=self.getRawInsn())

			if db.codeBlock.index != fb.index:
				raise AwlSimError("DB %d is not an instance DB for FB %d" %\
					(dbOper.offset.byteOffset,
					 blockOper.offset.byteOffset),
					rawInsn=self.getRawInsn())
		else:
			assert(0)
		# Check parameter assignments
		for param in self.params:
			if param.isOutbound:
				if ((blockOper.operType == AwlOperatorTypes.BLKREF_FB or\
				     blockOper.operType == AwlOperatorTypes.BLKREF_SFB) and\
				    param.rvalueOp.isImmediate()) or\
				   ((blockOper.operType == AwlOperatorTypes.BLKREF_FC or\
				     blockOper.operType == AwlOperatorTypes.BLKREF_SFC) and\
				    param.rvalueOp.isImmediate() and\
				    param.rvalueOp.operType != AwlOperatorTypes.IMM_PTR):
					raise AwlSimError("Immediate value assignment '%s' "
						"to OUTPUT or IN_OUT parameter '%s' is "
						"not allowed." %\
						(str(param.rvalueOp),
						 param.lvalueName),
						rawInsn=self.getRawInsn())

class AwlInsn_CALL(AwlInsn_AbstractCall): #+cdef

	__slots__ = ()

	def __init__(self, cpu, rawInsn=None, **kwargs):
		AwlInsn_AbstractCall.__init__(self, cpu, AwlInsn.TYPE_CALL, rawInsn, **kwargs)
		self.assertOpCount((1, 2))

	def run(self): #+cdef
#@cy		cdef S7StatusWord s

		if self.opCount == 1:
			self.cpu.run_CALL(self.op0, None, self.params, False)
		else:
			self.cpu.run_CALL(self.op0, self.op1, self.params, False)
		s = self.cpu.statusWord
		s.OS, s.OR, s.STA, s.NER = 0, 0, 1, 0

class AwlInsn_CC(AwlInsn_AbstractCall): #+cdef

	__slots__ = ()

	def __init__(self, cpu, rawInsn=None, **kwargs):
		AwlInsn_AbstractCall.__init__(self, cpu, AwlInsn.TYPE_CC, rawInsn, **kwargs)
		self.assertOpCount(1)

	def staticSanityChecks(self):
		self._warnDeprecated("Please use CALL instead.")

	def run(self): #+cdef
#@cy		cdef S7StatusWord s

		s = self.cpu.statusWord
		if s.VKE:
			self.cpu.run_CALL(self.op0, None, (), True)
		s.OS, s.OR, s.STA, s.VKE, s.NER = 0, 0, 1, 1, 0

class AwlInsn_UC(AwlInsn_AbstractCall): #+cdef

	__slots__ = ()

	def __init__(self, cpu, rawInsn=None, **kwargs):
		AwlInsn_AbstractCall.__init__(self, cpu, AwlInsn.TYPE_UC, rawInsn, **kwargs)
		self.assertOpCount(1)

	def staticSanityChecks(self):
		self._warnDeprecated("Please use CALL instead.")

	def run(self): #+cdef
#@cy		cdef S7StatusWord s

		self.cpu.run_CALL(self.op0, None, (), True)
		s = self.cpu.statusWord
		s.OS, s.OR, s.STA, s.NER = 0, 0, 1, 0
