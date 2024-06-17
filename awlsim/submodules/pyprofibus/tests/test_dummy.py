from __future__ import division, absolute_import, print_function, unicode_literals
from pyprofibus_tstlib import *
initTest(__file__)

import pyprofibus
import pyprofibus.dp
import pyprofibus.phy_dummy
import pyprofibus.phy_serial


class Test_DummyPhy(TestCase):
	def test_dummy_phy(self):
		phy = pyprofibus.phy_dummy.CpPhyDummySlave(debug=True)
		phy.setConfig(baudrate=19200)

		master = pyprofibus.DPM1(phy=phy,
					 masterAddr=42,
					 debug=True)

		slaveDesc = pyprofibus.DpSlaveDesc(gsd=None,
						   slaveAddr=84)

		slaveDesc.setCfgDataElements([
			pyprofibus.dp.DpCfgDataElement(pyprofibus.dp.DpCfgDataElement.ID_TYPE_OUT),
			pyprofibus.dp.DpCfgDataElement(pyprofibus.dp.DpCfgDataElement.ID_TYPE_IN),
		])

		slaveDesc.setUserPrmData(bytearray([1, 2, 3, 4, ]))

		slaveDesc.setSyncMode(True)
		slaveDesc.setFreezeMode(True)
		slaveDesc.setGroupMask(1)
		slaveDesc.setWatchdog(300)

		master.addSlave(slaveDesc)
		master.initialize()

		# Run slave initialization state machine.
		for i in range(25):
			slaveDesc.setOutData(bytearray([1, ]))
			master.run()
		# Check dummy-slave response to Data_Exchange.
		for i in range(100):
			print("testing %d" % i)
			j = 0
			while True:
				j += 1
				self.assertTrue(j < 10)
				slaveDesc.setOutData(bytearray([i, ]))
				master.run()
				ret = slaveDesc.getInData()
				if j >= 5 and ret is not None:
					break
			self.assertEqual(bytearray(ret), bytearray([i ^ 0xFF, ]))
