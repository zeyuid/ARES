# -*- coding: utf-8 -*-
#
# subprocess wrapper
#
# Copyright 2014-2016 Michael Buesch <m@bues.ch>
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

import distutils.spawn


__all__ = [
	"findExecutable",
	"PopenWrapper",
]


if isIronPython or isMicroPython:
	import os
	import signal
else:
	import subprocess

def findExecutable(executable):
	return distutils.spawn.find_executable(executable)

class PopenWrapper(object):
	def __init__(self, argv, env, stdio=False, hideWindow=False):
		if isMicroPython:
			pid = os.fork()
			if not pid: # child
				os.execvpe(argv[0], argv, env)
			else: # parent
				self.__pid = pid
		elif isIronPython:
			self.__pid = os.spawnve(os.P_NOWAIT,
						argv[0], argv, dict(env))
		else:
			if osIsWindows and hideWindow:
				startupinfo = subprocess.STARTUPINFO()
				startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
				startupinfo.wShowWindow = subprocess.SW_HIDE
			else:
				startupinfo = None
			self.__proc = subprocess.Popen(
				argv,
				env=dict(env),
				shell=False,
				stdin=subprocess.PIPE if stdio else None,
				stdout=subprocess.PIPE if stdio else None,
				stderr=subprocess.PIPE if stdio else None,
				startupinfo=startupinfo
			)

	def terminate(self):
		if isIronPython or isMicroPython:
			try:
				os.kill(self.__pid, signal.SIGTERM)
			except ValueError:
				pass
		else:
			self.__proc.terminate()

	def wait(self):
		if isIronPython or isMicroPython:
			pass#TODO
		else:
			self.__proc.wait()

	def poll(self):
		if isIronPython or isMicroPython:
			raise NotImplementedError()
		return self.__proc.poll()

	def communicate(self, input = None):
		if isIronPython or isMicroPython:
			raise NotImplementedError()
		return self.__proc.communicate(input)

	@property
	def stdin(self):
		if isIronPython or isMicroPython:
			raise NotImplementedError()
		return self.__proc.stdin

	@property
	def stdout(self):
		if isIronPython or isMicroPython:
			raise NotImplementedError()
		return self.__proc.stdout

	@property
	def stderr(self):
		if isIronPython or isMicroPython:
			raise NotImplementedError()
		return self.__proc.stderr

	@property
	def returncode(self):
		if isIronPython or isMicroPython:
			raise NotImplementedError()
		return self.__proc.returncode
