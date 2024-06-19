# -*- coding: utf-8 -*-
#
# AWL simulator - FUP compiler - Block declaration
#
# Copyright 2016-2017 Michael Buesch <m@bues.ch>
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

from awlsim.common.namevalidation import *
from awlsim.common.xmlfactory import *
from awlsim.common.project import *
from awlsim.common.version import *
from awlsim.common.cpuconfig import *

from awlsim.fupcompiler.base import *


class FupCompiler_BlockDeclFactory(XmlFactory):
	def parser_open(self, tag=None):
		self.inInstanceDBs = False
		self.inDB = False
		if tag:
			self.decl.setBlockType(tag.getAttr("type", "FC"))
			self.decl.setBlockName(tag.getAttr("name", "FC 1"))
		XmlFactory.parser_open(self, tag)

	def parser_beginTag(self, tag):
		if self.inInstanceDBs:
			if tag.name == "db":
				self.decl.addInstanceDB(tag.getAttr("name", ""))
				self.inDB = True
				return
		else:
			if tag.name == "instance_dbs":
				self.inInstanceDBs = True
				return
		XmlFactory.parser_beginTag(self, tag)

	def parser_endTag(self, tag):
		if self.inInstanceDBs:
			if self.inDB:
				if tag.name == "db":
					self.inDB = False
					return
			else:
				if tag.name == "instance_dbs":
					self.inInstanceDBs = False
					return
		else:
			if tag.name == "blockdecl":
				self.parser_finish()
				return
		XmlFactory.parser_endTag(self, tag)

class FupCompiler_BlockDecl(FupCompiler_BaseObj):
	factory			= FupCompiler_BlockDeclFactory
	noPreprocessing		= True

	def __init__(self, compiler):
		FupCompiler_BaseObj.__init__(self)
		self.compiler = compiler	# FupCompiler
		self.setBlockType("FC")
		self.setBlockName("FC 1")
		self.instanceDBs = []

	def setBlockType(self, blockType):
		self.blockType = blockType.upper().strip()
		if self.blockType not in {"FC", "FB", "OB"}:
			raise FupDeclError("Invalid block type: %s" % (
				self.blockType),
				self)

	def setBlockName(self, blockName):
		blockName = blockName.strip()
		if not blockName:
			return
		self.blockName = blockName

	def addInstanceDB(self, dbName):
		dbName = dbName.strip()
		if not dbName:
			return
		if len(dbName) > 3 and\
		   dbName.upper().startswith("DI") and\
		   dbName[2].isspace():
			dbName = "DB" + dbName[2:]
		self.instanceDBs.append(dbName)

	def compile(self, interf):
		"""Compile this FUP block declaration to AWL.
		interf => FupCompiler_Interf
		Returns a tuple: (list of AWL header lines,
				  list of AWL footer lines,
				  list of AWL lines for instance DBs).
		"""
		self.compileState = self.COMPILE_RUNNING
		blockHeader = []
		blockFooter = []
		instDBs = []

		mnemonics = self.compiler.mnemonics
		srcName = AwlName.stripChars(self.compiler.fupSource.name,
					     replaceWith="_",
					     stripAlpha=False,
					     stripNum=False, stripSpace=False)

		strAwl = "AWL" if mnemonics == S7CPUConfig.MNEMONICS_DE else "STL"
		strFup = "FUP" if mnemonics == S7CPUConfig.MNEMONICS_DE else "FBD"
		strMnemonics = "DE (German)" if mnemonics == S7CPUConfig.MNEMONICS_DE\
			       else "EN (international)"

		def mkIntro(lines, blockTypeDecl):
			optimizers = []
			for i, grid in enumerate(self.compiler.grids):
				if self.compiler.optimizerSettingsContainer is None:
					optSettCont = grid.optimizerSettingsContainer
				else:
					optSettCont = self.compiler.optimizerSettingsContainer
				optsStr = str(optSettCont)
				if not optsStr:
					optsStr = "disabled"
				optimizers.append("grid-%d: %s" % (i + 1, optsStr))
			lines.append("// ")
			lines.append("// %s generated by Awlsim %s compiler" % (
				     blockTypeDecl, strFup))
			lines.append("// ")
			lines.append("// Source            : %s" % srcName)
			lines.append("// Compiler version  : %s" % VERSION_STRING)
			lines.append("// %s mnemonics     : %s" % (strAwl, strMnemonics))
			lines.append("// Optimizers        : %s" % "; ".join(optimizers))
			lines.append("// ")

		def mkHdrInfo(lines):
			lines.append("\tTITLE   = %s" % srcName)
			lines.append("\tFAMILY  : %s" % strFup)
			lines.append("\tVERSION : %s" % VERSION_STRING)

		if self.blockType == "FC":
			if not interf.retValField:
				raise FupDeclError("RET_VAL is not defined for %s." % (
					 self.blockName),
					 self)
			retVal = interf.retValField.typeStr
			if not AwlName.mayBeValidType(retVal):
				raise FupDeclError("RET_VAL data type contains "
					"invalid characters.",
					self)
			mkIntro(blockHeader, "FUNCTION")
			blockHeader.append("FUNCTION %s : %s" %(
					   self.blockName, retVal))
			mkHdrInfo(blockHeader)
			blockFooter.append("END_FUNCTION")
		elif self.blockType == "FB":
			mkIntro(blockHeader, "FUNCTION_BLOCK")
			blockHeader.append("FUNCTION_BLOCK %s" %\
					   self.blockName)
			mkHdrInfo(blockHeader)
			blockFooter.append("END_FUNCTION_BLOCK")
		elif self.blockType == "OB":
			mkIntro(blockHeader, "ORGANIZATION_BLOCK")
			blockHeader.append("ORGANIZATION_BLOCK %s" %\
					   self.blockName)
			mkHdrInfo(blockHeader)
			blockFooter.append("END_ORGANIZATION_BLOCK")
		else:
			raise FupDeclError("Unknown block type: %s" % (
				self.blockType),
				self)

		for dbName in self.instanceDBs:
			instDBs.append("")
			instDBs.append("")
			mkIntro(instDBs, "Instance DATA_BLOCK")
			instDBs.append("DATA_BLOCK %s" % dbName)
			mkHdrInfo(instDBs)
			instDBs.append("\t%s" % self.blockName)
			instDBs.append("BEGIN")
			for field in interf.allFields:
				fieldName = field.name
				initValueStr = field.initValueStr.strip()
				comment = field.comment
				if not initValueStr:
					continue
				if not AwlName.isValidVarName(fieldName):
					raise FupDeclError("Variable name "
						"'%s' contains invalid characters." % (
						fieldName),
						self)
				if not AwlName.mayBeValidValue(initValueStr):
					raise FupDeclError("Variable value "
						"'%s' contains invalid characters." % (
						initValueStr),
						self)
				if not AwlName.isValidComment(comment):
					raise FupDeclError("Comment "
						"'%s' contains invalid characters." % (
						comment),
						self)
				instDBs.append("\t%s := %s;%s" %(
					fieldName, initValueStr,
					("  // " + comment) if comment else ""))
			instDBs.append("END_DATA_BLOCK")

		self.compileState = self.COMPILE_DONE
		return blockHeader, blockFooter, instDBs


	def generateCallTemplate(self):
		"""Generate template AWL code for a CALL operation
		to this block.
		Returns a list of AWL lines.
		"""
		awlLines = []

		if self.blockType == "FC":
			awlLines.append("\tCALL %s" % self.blockName)
		elif self.blockType == "FB":
			awlLines.append("\tCALL %s, DB ..." % self.blockName)
		else:
			raise FupDeclError("Cannot generate "
				"CALL to %s block." % (
				self.blockType),
				self)

		return awlLines

	def __repr__(self): #@nocov
		return "FupCompiler_BlockDecl(compiler)"

	def __str__(self): #@nocov
		return "FUP-block-declaration"