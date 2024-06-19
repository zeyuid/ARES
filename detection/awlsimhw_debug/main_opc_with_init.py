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

# check the dependencies
import adodbapi as adod
from sys import exit
import os
from multiprocessing import Process
from threading import Thread
import PLCrecover.ForceConnect
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
		self.distance = 0.5
		self.cusumVec = [0 for i in range(self.cmdSize)]
		self.alarm = [0 for i in range(self.cmdSize)]
		self.alarmThreshold = 1
		# self.conn_str = "Provider=WinCCOLEDBProvider.1;Catalog=CC_wincc_20_11_03_21_26_04R;Data Source=WIN-SABDP768LOD\WINCC"
		# self.readQuerySensor = "TAG:R,(59;58;57;56;55;54;53;52;51;50;49;48;47;46;45;44;43;42;41;40;39;38;37;36;35),'0000-00-00 00:00:00.400','0000-00-00 00:00:00.000'"
		# self.readQueryCmd = "TAG:R,(81;80;79;78;77;76;75;73;72;71;70;69;68;67;66;64;65;63;62;61;60),'0000-00-00 00:00:00.400','0000-00-00 00:00:00.000'"
		## read both sensor and cmd
		# self.readAll = "TAG:R,(59;58;57;56;55;54;53;52;51;50;49;48;47;46;45;44;43;42;41;40;39;38;37;36;35;81;80;79;78;77;76;75;73;72;71;70;69;68;67;66;64;65;63;62;61;60),'0000-00-00 00:00:00.100','0000-00-00 00:00:00.000'"
		self.cmdMemory = ['Q0.1','Q0.2','Q0.3','Q0.4','Q0.5','Q0.6','Q0.7','Q1.1','Q1.2','Q1.3','Q1.4','Q1.5','Q1.6','Q1.7','Q2.0','Q2.1','Q2.2','Q2.3','Q2.4','Q2.5','Q2.6']
		self.PLC_IP = "192.168.0.2"
		self.PLC_PORT = 102
		self.record_all = []
		self.estimate_all = []
		self.scada_log_format = "C:\\Users\\Guo wei\\Desktop\\awlsim-opc\\awlsim\\awlsim-master\\awlsimhw_debug\\command_generated.mat"
		self.scada_log_export = "C:\\Users\\Guo wei\\Desktop\\awlsim-opc\\awlsim\\awlsim-master\\awlsimhw_debug\\scada_log_202104211.mat"
		self.bool_result = None
		# add opc init here
		self.wincc_opc = opc()
		self.wincc_opc.connect()
		self.symbol = "+"
		# for 500ms
		self.time_rec = time.time()
		self.init = True

	def doShutdown(self):
		print("HW module debug is shutting down")
		command_generated = loadmat(self.scada_log_format)
		del command_generated['command']
		command_generated['data_raw'] = self.record_all
		command_generated['estimate_raw'] = self.estimate_all
		savemat(self.scada_log_export, command_generated)
		print("data is stored in {}".format(self.scada_log_export))
		
		self.wincc_opc.close()
		print("opc connection close")

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

			# 500ms
			while time.time() - self.time_rec < 0.5:
				time.sleep(0.01)
			self.time_rec = time.time()
			
			self.bool_result = self.wincc_opc.readVars()
			
			# for mat debug
			# self.bool_result = self.simu_data[self.cursor_mat]
			# self.cursor_mat += 1
			
			print(self.symbol)
			self.symbol = "+" if self.symbol == "-" else "-" 
				
			print("Sensor: ")
			print(self.bool_result[0:25])
			self.record_all.append(self.bool_result)
			
			# add something to change the bool bit array to byte array
			inByte = formatInput(self.bool_result[0:25])
			# todo, check the format
			print([i for i in inByte])
			byteOffset = 0
			self.sim.cpu.storeInputRange(byteOffset, inByte)
		else:
			self.cycle_cnt = (self.cycle_cnt + 1) % self.cycle

	def writeOutputs(self):
		if self.cycle_cnt == 0:
		# check the output bytearray size of cmd read, in wincc all are bytes
			outputCnt = self.cmdSize // 8 + 1 # change to byte
			byteOffset = 0
			outByte = self.sim.cpu.fetchOutputRange(byteOffset, outputCnt)  # '1' is self-defined by the largest register address in code
			# change the bytearray to list for comparison
			command_estimated = list(outByte)
			command_estimated = formatOutput(command_estimated)
			self.estimate_all.append(command_estimated)
			print("command_estimated")
			print(command_estimated)
			# read the cmd from sql server
			command_logged = self.bool_result[-21:]
			print("command_logged")
			print(command_logged)
			
			# compare the cmdRead with outByte transformed array
			predict_error = [command_logged[i] - command_estimated[i] for i in range(self.cmdSize)]
			# set the cusum vector
			self.cusumVec = [max(0, self.cusumVec[i] + abs(predict_error[i] - self.average) - self.distance) for i in range(self.cmdSize)]
			# find the alarm ones, clean the cusum with alarmed ones
			corrupted_memory = []
			for i in range(self.cmdSize):
				if self.cusumVec[i] > self.alarmThreshold:
					self.cusumVec[i] = 0.0
					self.alarm[i] = 1
					corrupted_memory.append(self.cmdMemory[i])
				else:
					self.alarm[i] = 0
			# send packet the recover from attack state
			# for debug
			print("The memory corrupted is: ")
			print(corrupted_memory)
			# send packet, glue the code here, consider to spawn a child process to handle it!
			# use Multiprocessing with Process, don't join the process since we don't wait for the child process
			
			if ( len(corrupted_memory)!=0 ):
				proc_recover = Thread(target=PLCrecover.ForceConnect.deleteForceJob, args=(self.PLC_IP, self.PLC_PORT,), \
					name='PLCrecover') # here we only delete the force job, for the cmd will be recalculated??
				proc_recover.daemon = True
				proc_recover.start()
				print("handle attack")
		

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
