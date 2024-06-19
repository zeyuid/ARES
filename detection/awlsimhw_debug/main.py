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

# the dependencies for attack detection and response 
import adodbapi as adod
from sys import exit
import os
from multiprocessing import Process
from threading import Thread
# import PLCrecover # removed, due to the ethical considerations 
from utilsConvert.utilsConvert import *
from scipy.io import loadmat, savemat
from .readOpc import opc
import time


class HardwareInterface_Debug(AbstractHardwareInterface): #+cdef #@nocov
	name		= "debug"
	description	= "Debugging hardware module.\n"\
			  "This can be used to generate sensor values and collecte the induced command values."

	def __init__(self, sim, parameters={}):
		AbstractHardwareInterface.__init__(self, sim = sim,  parameters = parameters)


	def doStartup(self, iter_num=0):
		"""Startup the hardware module. generate the sensor values
		"""
		self.cycle = 3 
		self.cycle_cnt = 0
		self.inputSensor = None
		self.commandRead = None
		self.commandCal = None
		self.allSize = 46
		self.sensorSize = 25
		self.cmdSize = 21
		self.average = 0.0
		self.distance = 0.3 
		self.cusumVec = [0 for i in range(self.cmdSize)]
		self.alarm = [0 for i in range(self.cmdSize)]
		self.alarmThreshold = 1 # by default 
		self.cmdMemory = ['Q0.1','Q0.2','Q0.3','Q0.4','Q0.5','Q0.6','Q0.7','Q1.1','Q1.2','Q1.3','Q1.4','Q1.5','Q1.6','Q1.7','Q2.0','Q2.1','Q2.2','Q2.3','Q2.4','Q2.5','Q2.6']
		
		# context we record
		self.record_all = []
		self.estimate_all = []
		self.cusum_all = []
		self.alarm_all = []
		# give the path of detection logs file 
		self.scada_log_format = "./awlsimhw_debug/command_generated.mat"
		self.scada_log_export = "./awlsimhw_debug/awlsimhw_debug/scada_log_" + time.strftime("%Y%m%d-%H%M%S") + ".mat"
		self.bool_result = None
		# add opc init here
		self.wincc_opc = opc()
		self.wincc_opc.connect()
		self.symbol = "+"
		self.time_rec = time.time()
		self.init = True
		self.alarm_count = 0

		# for recovery
		self.recoverPositive = False
		
		# record the context
		self.context = []

	def doShutdown(self):
		print("HW module debug is shutting down")
		print(time.strftime("%Y%m%d-%H%M%S"))
		
		# # remove all recover job, due to the ethical considerations 
		# proc_recover = ... # initiate Thread for PLC recovery 

		# save context
		command_generated = loadmat(self.scada_log_format)
		del command_generated['command']
		command_generated['data_raw'] = self.record_all
		command_generated['estimate_raw'] = self.estimate_all
		command_generated['cusum'] = self.cusum_all
		command_generated['alarm'] = self.alarm_all
		savemat(self.scada_log_export, command_generated)
		print("data is stored in {}".format(self.scada_log_export))
		
		self.wincc_opc.close()
		print("opc connection close")
		for i in self.context:
			print(i)

	def readInputs(self):
		if self.cycle_cnt == 0:
			# for init
			if self.init == True:
				self.init = False
				self.bool_result = self.wincc_opc.readVars()
				inByte = formatInput(self.bool_result[0:25], init=True)
				byteOffset = 0
				self.sim.cpu.storeInputRange(byteOffset, inByte)
				return

			# print alarm count
			print('total FPs:')
			print(self.alarm_count)
			# 500ms
			while time.time() - self.time_rec < 0.5:
				time.sleep(0.01)
			self.time_rec = time.time()
			
			self.bool_result = self.wincc_opc.readVars()
			
			print(self.symbol)
			self.symbol = "+" if self.symbol == "-" else "-" 
				
			print("Sensor: ")
			print(self.bool_result[0:25])
			self.record_all.append(self.bool_result)
			
			# change the bool bit array to byte array 
			inByte = formatInput(self.bool_result[0:25])
			byteOffset = 0
			self.sim.cpu.storeInputRange(byteOffset, inByte)
		else:
			self.cycle_cnt = (self.cycle_cnt + 1) % self.cycle

	def writeOutputs(self):
		if self.cycle_cnt == 0:
		# check the output bytearray size of cmd read, in wincc all are bytes
			outputCnt = self.cmdSize // 8 + 1 # change to byte
			byteOffset = 0
			outByte = self.sim.cpu.fetchOutputRange(byteOffset, outputCnt)  
			# change the bytearray to list for comparison
			command_estimated = list(outByte)
			command_estimated = formatOutput(command_estimated)
			self.estimate_all.append(command_estimated)
			print("command_estimated")
			print(command_estimated)
			# read the cmds from the opc server 
			command_logged = self.bool_result[25:46]
			print("command_logged")
			print(command_logged)
			
			# alarming based on the logged commands and predicted commands 
			# compare the cmdRead with outByte transformed array 
			predict_error = [command_logged[i] - command_estimated[i] for i in range(self.cmdSize)]
			# set the cusum vector
			self.cusumVec = [max(0, self.cusumVec[i] + abs(predict_error[i] - self.average) - self.distance) for i in range(self.cmdSize)]
			self.cusum_all.append(self.cusumVec)
			# find the alarm ones, clean the cusum with alarmed ones
			corrupted_memory = []
			alarm_here = [0] * self.cmdSize
			wanted_vals = []
			for i in range(self.cmdSize):
				threshold = self.alarmThreshold if i != 8 else 2
				if self.cusumVec[i] > threshold:
					self.cusumVec[i] = 0.0
					alarm_here[i] = 1
					corrupted_memory.append(self.cmdMemory[i])
					wanted_vals.append(command_estimated[i])
				else:
					alarm_here[i] = 0
			self.alarm_all.append(alarm_here)
			# send packet the recover from attack state
			print("The memory corrupted is: ")
			print(corrupted_memory)
			print("The vals we want are: ")
			print(wanted_vals)
			
			# # Here invokes the PLC recovery functions, which are removed due to the ethical considerations 
			# if self.recoverPositive and len(corrupted_memory) == 0:
			# 	print("----------Control handled back to PLC-------------")
			# 	self.recoverPositive = False
			# 	proc_recover = ... # deactivate the recovery 
			
			if ( len(corrupted_memory)!=0 ):
				self.context.append({"estimated":command_estimated, "logged":command_logged, "error":corrupted_memory})
				self.alarm_count += 1 
			# 	print("----------Control commands are forced by prediction---------")
			# 	self.recoverPositive = True
			# 	proc_recover = ... # activate the recovery 
			
				
		
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
