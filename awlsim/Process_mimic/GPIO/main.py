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

# @Zeyu Yang

from __future__ import division, absolute_import, print_function, unicode_literals

import os, pickle
import numpy as np
from scipy.io import loadmat
import time

indexRead = 0
indexWrite = 0
Start_generating = False
lenMat = 0
cmds = []
sensor_reading = []

def array2int(data):
	# data is 1*n bits vector, max(n) = 8

	Bi_conver_op = 2**np.arange(data.shape[0])
	BiValue = data.dot(Bi_conver_op[::-1].T)
	BiValue = BiValue
	# return a int
	return BiValue

def array2list(data):
	# data is 1*n bits vector, calculation with every lower eight bits

	bits_len = len(data)
	byte_len = int(np.ceil( bits_len / 8 ))

	BiValues = []
	for byte in range(byte_len):

		bits_lower = data[max(0, bits_len-(byte+1)*8) : bits_len-(byte)*8]
		BiValues.append(array2int(bits_lower))

	return BiValues


def int2array(data, bits_length):
	# transfer a int to byte, the 8 bits
	item = bin(data)[2:]
	item = format(item, '0>{}'.format(bits_length))  # higher bit is replaced with 0
	bits_array = []
	for i in item:
		bits_array.append(int(i))
	return bits_array


def list2array(data):
	# data is a list for several bytes
	bits_array = []  # bits_array is a list for bits

	for byte in range(len(data)-1, -1, -1):
		bits_higher = int2array(data[byte], 8)
		bits_array.extend(bits_higher)

	return bits_array


def sensor_generation(sensorstored_path_source):
	global indexRead, indexWrite, Start_generating, lenMat, cmds, sensor_reading
	# if mat_exits start to write data

	# When mat is is write in specific name, load them into RAM
	# transfer sensor_int_value to S7CPU
	# time.sleep(0.2) # 停留一会儿 以更好地判断是否真的有文件
	if os.path.exists(sensorstored_path_source):
		# if the sensor_reading_raw is not preprocessed, processing ...
		time.sleep(0.05)  # only called at the first time,  used to weight for .mat file generation
		# print("wait for 50ms")
		sensor_reading_raw = loadmat(sensorstored_path_source)
		# transist the binary sensor readings to int type, which is send to S7CPU
		my_array = np.array([1, 1])
		sensor_reading = []
		for key in sensor_reading_raw:
			if type(sensor_reading_raw[key]) == type(my_array):
				for i in range(sensor_reading_raw[key].shape[0]):
					# calculate every eight bits
					sensor_reading.append(array2list(sensor_reading_raw[key][i]))   # use append, because function array2int return a number, or a

		os.remove(sensorstored_path_source)



		# if the content is not none
		if sensor_reading:
			indexRead = 0
			indexWrite = 0 # now output can write
			cmds = []
			Start_generating = True
			lenMat = len(sensor_reading)
	
	# print("len of mat is : ", lenMat, "index is ", indexRead)
	if Start_generating and indexRead < lenMat:
		sensor_int_value = sensor_reading[indexRead]
		# print(sensor_int_value)
		hw_shutdown = False
		indexRead += 1
	else:
		sensor_int_value = None
		hw_shutdown = True
		Start_generating = False

	return sensor_int_value, hw_shutdown


def output_initial(command_init_stored_path_source):
	# time.sleep(0.2) # 停留一会儿 以更好地判断是否真的有文件
	# transfer command_init to S7CPU
	if os.path.exists(command_init_stored_path_source):
		time.sleep(0.05)
		command_init_raw = loadmat(command_init_stored_path_source)
		# transist the binary sensor readings to int type, which is send to S7CPU
		my_array = np.array([1, 1])
		command_init = []
		for key in command_init_raw:
			if type(command_init_raw[key]) == type(my_array):
				for i in range(command_init_raw[key].shape[0]):
					command_init.append(array2list(command_init_raw[key][i]))

		command_int_value = command_init.pop(0)
		command_initialization = True
		os.remove(command_init_stored_path_source)
		# shutil.move(command_init_stored_path_source, "./Process_mimic/Command_trigger/command_init.mat")
	else:
		command_initialization = False
		command_int_value = None
	return command_int_value, command_initialization

def sensor_initial(sensorinit_path_source):
	# time.sleep(0.2) # 停留一会儿 以更好地判断是否真的有文件
	# transfer sensor_int_value to S7CPU
	if os.path.exists(sensorinit_path_source):
		time.sleep(0.05)
		sensor_init_raw = loadmat(sensorinit_path_source)
		# transist the binary sensor readings to int type, which is send to S7CPU
		my_array = np.array([1, 1])
		sensor_init = []
		for key in sensor_init_raw:
			if type(sensor_init_raw[key]) == type(my_array):
				for i in range(sensor_init_raw[key].shape[0]):
					sensor_init.append(array2list(sensor_init_raw[key][i]))

		sensor_init_int_value = sensor_init.pop(0)
		sensor_init_initialization = True
		os.remove(sensorinit_path_source)
		# shutil.move(command_init_stored_path_source, "./Process_mimic/Command_trigger/command_init.mat")
	else:
		sensor_init_initialization = False
		sensor_init_int_value = None
	return sensor_init_int_value, sensor_init_initialization


def input():
	sensorstored_path_source = r"./Process_mimic/Sensors_mimic/sensors.mat"
	commandstored_path_source = r"./Process_mimic/Sensors_mimic/command_init.mat"
	sensorinit_path_source = r"./Process_mimic/Sensors_mimic/sensor_init.mat"

	# using the local dump to save change the position. but time consouming
	sensor_value, hw_shutdown = sensor_generation(sensorstored_path_source)
	command_init_value, command_initialization = output_initial(commandstored_path_source)
	sensor_init_value, sensor_init_initialization = sensor_initial(sensorinit_path_source)
	
	# if sensor_init_value:
	# 	print(sensor_init_value)



	return sensor_value, hw_shutdown, command_init_value, command_initialization, sensor_init_value, sensor_init_initialization


def output(byteOffset, outByte):
	global indexWrite, Start_generating, lenMat, cmds

	outarray = list2array(outByte)
	print("byte = {}, outputvalue = {}".format(byteOffset, outarray))

	if Start_generating:
		# cmds.append([outarray])
		cmds.append(outarray)

	if len(cmds) == lenMat - 1:
		# cmds.append([outarray])
		cmds.append(outarray)


	# print('now the cmds is like', cmds)
	return cmds


def command_SCADA():
	# obtains the commands vector from SCADA server,
	# arranged according to G_map

	command_SCADA = 0 # shall be removed by Hua Yu

	return command_SCADA



	# if not os.path.exists(commandstored_path_python):
	# 	commands = [outarray]
	# 	if not os.path.exists("./Process_mimic/Command_trigger/"):
	# 		os.makedirs("./Process_mimic/Command_trigger/")
	# 	with open(commandstored_path_python, "wb") as fp:
	# 		pickle.dump(commands, fp)

	# else:
	# 	commands = pickle.load(open(commandstored_path_python, "rb"))
	# 	commands.append(outarray)
	# 	with open(commandstored_path_python, "wb") as fp:
	# 		pickle.dump(commands, fp)
