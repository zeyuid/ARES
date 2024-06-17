# ARES
Reverse Engineering Physical Semantics of PLC Program Variables Using Control Invariants


## Prepare the PLC-Twin
1. Software PLC is developed based on [Awlsim - S7 compatible Programmable Logic Controller](https://github.com/mbuesch/awlsim).

	The modifications include: 
	1). Supplemented a Process mimicking module (i.e., Process_mimic), which should be stored at the root. \\
	2). Revised the awlsimhw_debug module, to support the online attack detection. \\
	3). Supplemented an interface of PLC simulation, to support the quick rebooting of the PLC execution, i.e., Elevator_300project.awlpro. \\
	4). Revised the functions, such as .awlsim.core.hardware.py, to define the data interface with Process_mimic

		cd ./awlsim
		python awlsim-server Elevator_300project.awlpro
		python awlsim-client -r RUN  
		python awlsim-client -r Stop 

2. Hardware PLC: 

python ./data_segmentation/segmenting_utils.py

## Obtain the Gcode
	cd ./STL_Parser
	python -m core.main

python ./data_segmentation/segmenting_utils.py

## Obtain the Gdata

python ./data_segmentation/segmenting_utils.py

## Obtain the Gcross

python ./data_segmentation/segmenting_utils.py

## Detect semantic attacks

python ./data_segmentation/segmenting_utils.py

## Respond semantic attacks

The response to semantic attacks utilizes the "Force" function of industrial communication protocols. However, the "Force" function may also be utilized by adversaries and further threaten the real critical infrastructure. For the legal and ethical considerations, the exploitation of "Force" function for Siemens PLC and Rockwell PLC will be published when the authentication weakness is fixed. 
