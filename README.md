# ARES
Reverse Engineering Physical Semantics of PLC Program Variables Using Control Invariants


## Prepare the PLC-Twin
1. Software PLC: develop based on the Awlsim - S7 compatible Programmable Logic Controller 
	https://github.com/mbuesch/awlsim

2. Hardware PLC: 

python ./data_segmentation/segmenting_utils.py

## Obtain the Gcode

python ./data_segmentation/segmenting_utils.py

## Obtain the Gdata

python ./data_segmentation/segmenting_utils.py

## Obtain the Gcross

python ./data_segmentation/segmenting_utils.py

## Detect semantic attacks

python ./data_segmentation/segmenting_utils.py

## Respond semantic attacks

The response to semantic attacks utilizes the "Force" function of industrial communication protocols. However, the "Force" function may also be utilized by adversaries and further threaten the real critical infrastructure. For the legal and ethical considerations, the exploitation of "Force" function for Siemens PLC and Rockwell PLC will be published when the authentication weakness is fixed. 
