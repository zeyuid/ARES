# -*- coding: utf-8 -*-
#
# AWL simulator - Debug hardware interface
#
# Copyright 2013-2017 Michael Buesch <m@bues.ch>
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
from awlsim.common.exceptions import *

#from awlsimhw_debug.main cimport * #@cy

from awlsim.core.hardware_params import *
from awlsim.core.hardware import * #+cimport
from awlsim.core.operatortypes import * #+cimport
from awlsim.core.operators import * #+cimport
from awlsim.core.offset import * #+cimport
from awlsim.core.cpu import * #+cimport

import re
import numpy as np
import pickle
from scipy.io import loadmat, savemat

# import tensorflow as tf
# # Settings
# flags = tf.app.flags
# FLAGS = flags.FLAGS
#
# # core params..
# flags.DEFINE_integer('cal_cyc', 7, 'version of elevator data.')




class HardwareInterface_Debug(AbstractHardwareInterface): #+cdef #@nocov
	name		= "debug"
	description	= "Debugging hardware module.\n"\
			  "This can be used to generate sensor values and collecte the induced command values."

	# paramDescs = [
	# 	HwParamDesc_bool("dummyParam", description = "Unused dummy parameter"),
	# ]


	def __init__(self, sim, parameters={}):
		AbstractHardwareInterface.__init__(self, sim = sim,  parameters = parameters)


	def doStartup(self, iter_num=0):
		"""Startup the hardware module. generate the sensor values
		"""
		self.__saved = False
		self.cnt = 0
		self.cycle = 3  # default=3 times a computation.
		pass

	def doShutdown(self):
		# print("shutdown")
		# AbstractHardwareInterface.doShutdown(self)
		pass

	def readInputs(self):
		# Import the Raspberry Pi GPIO module
		if not (self.cnt % self.cycle == 0):
			# print(self.cnt)
			self.cnt += 1
			# pass

		else:
			# print("input")
			self.cnt = 0
			# print(self.cnt)
			self.cnt += 1

			# print("write to cpu")
			# set the sensor reading's clock as awlsim's

			try:
				# from Process_mimic.GPIO import process_simulation as Process_GPIO
				import Process_mimic.GPIO as Process_GPIO
				self.__Process_GPIO = Process_GPIO
			except ImportError as e: #@nocov
				self.raiseException("Failed to import Raspberry Pi Mimic GPIO "
					"module 'Process_mimic.GPIO': %s" % str(e))

			# Copy shortcuts to Raspberry Pi GPIO module
			# sensor_int_value, sensor_exist

			self.__Process_GPIO_input = self.__Process_GPIO.input
			self.__Process_GPIO_output = self.__Process_GPIO.output
			self.__Process_GPIO_input_value, self.hw_shutdown, self.__Process_GPIO_output_value, self.command_initialization, self.__Process_GPIO_sensorINIT_value, self.sensor_init_initialization = self.__Process_GPIO_input()


			if self.command_initialization:
				byteOffset = 0
				inoutByte = self.__Process_GPIO_output_value
				# self.sim.cpu.storeOutputByte(byteOffset, inoutByte)
				self.sim.cpu.storeOutputRange(byteOffset, inoutByte)

			if self.sensor_init_initialization:
				byteOffset = 0
				insensorINITByte = self.__Process_GPIO_sensorINIT_value
				# self.sim.cpu.storeOutputByte(byteOffset, inoutByte)
				self.sim.cpu.storeInputRange(byteOffset, insensorINITByte)
			elif not self.hw_shutdown:
				# print("command generating ... ")
				byteOffset = 0
				inByte = self.__Process_GPIO_input_value
				# self.sim.cpu.storeInputByte(byteOffset, inByte)
				self.sim.cpu.storeInputRange(byteOffset, inByte)

				self.__saved = False
				# print("write to cpu: \n", self.__Process_GPIO.list2array(inByte))
				# print("input = {}".format(self.sim.cpu.fetchInputByte(byteOffset)))

			# if not self.hw_shutdown:
			# 	byteOffset = 0
			# 	inByte = self.__Process_GPIO_input_value
			# 	# self.sim.cpu.storeInputByte(byteOffset, inByte)
			# 	self.sim.cpu.storeInputRange(byteOffset, inByte)
			# 	# print("input = {}".format(self.sim.cpu.fetchInputByte(byteOffset)))


	def writeOutputs(self):

		# self.connnn += 1

		if not (self.cnt % self.cycle == 0):
			# print(self.cnt-1)
			# print("nop nop nop nop")
			pass
		else:
			# print(self.cnt-1)
			# print("output")
			# print("store the output in the last cycle")
			# print("cpu running times:{}".format(self.connnn))

			# commandgenerated_path_matlab = "./Process_mimic/Command_trigger/command_generated.mat"
			command_form_path = "./Process_mimic/Command_trigger/command_generated.mat"
			command_generated_path_matlab = "./Process_mimic/Command_trigger/commands.mat"

			if not self.hw_shutdown:
				byteOffset = 0
				# outByte = self.sim.cpu.fetchOutputByte(byteOffset)
				outByte = self.sim.cpu.fetchOutputRange(byteOffset, 3)  # '1' is self-defined by the largest register address in code
				self.__Commands = self.__Process_GPIO_output(byteOffset, outByte)

			elif not (os.path.exists(command_generated_path_matlab) or self.__saved):
				# save mat to file
				try:
					# print("We saving file to disk!\n")
					commands = self.__Commands
					commandsNp = np.array(commands).astype("bool")
					# print(commandsNp.shape)

					command_generated = loadmat(command_form_path)
					command_generated['command'] = commandsNp[0:-1, :]

					savemat(command_generated_path_matlab, command_generated)
					self.__saved = True

					# outByte = self.sim.cpu.fetchOutputRange(0, 3)
					# print("last:\nbyte = {}, outputvalue = {}".format(0, self.__Process_GPIO.list2array(outByte)))
				except:
					pass


		# copy from the awlsimhw_dummy module main.py file, Zeyu
	def directReadInput(self, accessWidth, accessOffset): #@nocy
#@cy	cdef bytearray directReadInput(self, uint32_t accessWidth, uint32_t accessOffset):
		if accessOffset < self.inputAddressBase:
			return bytearray()
		# Just read the current value from the CPU and return it.
		try:
			return self.sim.cpu.fetchInputRange(accessOffset, accessWidth // 8)
		except AwlSimError as e:
			# We may be out of process image range. Just return 0.
			return bytearray( (0,) * (accessWidth // 8) )

	# copy from the awlsimhw_dummy module main.py file
	def directWriteOutput(self, accessWidth, accessOffset, data): #@nocy
#@cy	cdef ExBool_t directWriteOutput(self, uint32_t accessWidth, uint32_t accessOffset, bytearray data) except ExBool_val:
		if accessOffset < self.outputAddressBase:
			return False
		# Just pretend we wrote it somewhere.
		return True


# Module entry point
HardwareInterface = HardwareInterface_Debug
