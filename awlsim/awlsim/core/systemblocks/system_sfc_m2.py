# -*- coding: utf-8 -*-
#
# AWL simulator - SFCs
#
# Copyright 2012-2018 Michael Buesch <m@bues.ch>
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

from awlsim.common.datatypehelpers import * #+cimport
from awlsim.common.exceptions import *
from awlsim.common.util import *

from awlsim.core.systemblocks.systemblocks import * #+cimport
from awlsim.core.blockinterface import *
from awlsim.core.datatypes import *


class SFCm2(SFC): #+cdef
	name = (-2, "__REBOOT", None)

	interfaceFields = {
		BlockInterfaceField.FTYPE_IN	: (
			BlockInterfaceField(name="REBOOT_TYPE", dataType="INT"),
		),
	}

	def run(self): #+cpdef #@nocov
		rebootType = wordToSignedPyInt(AwlMemoryObject_asScalar(
			self.fetchInterfaceFieldByName("REBOOT_TYPE")))
		if rebootType == 1:
			raise MaintenanceRequest(MaintenanceRequest.TYPE_SOFTREBOOT,
						 "SFC -2 soft reboot request")
		else:
			raise AwlSimError("SFC -2: Unknown REBOOT_TYPE %d" % rebootType)
