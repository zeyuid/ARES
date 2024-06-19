# ARES
Reverse Engineering Physical Semantics of PLC Program Variables Using Control Invariants


## Prepare the PLC-Twin
1. Software PLC is developed based on [Awlsim - S7 compatible Programmable Logic Controller](https://github.com/mbuesch/awlsim).

	The modifications include: <br>
	1). Supplemented a Process mimicking module (./awlsim/Process_mimic) which should be stored at the root. <br>
	2). Revised the original debugging module (./awlsim/awlsimhw_debug) to support the PLC memory state acquisition and online attack detection. <br>
	3). Supplemented an interface of PLC simulation (./awlsim/Elevator_300project.awlpro) to support the quick rebooting of the PLC execution. <br>
	4). Revised original functions of Awlsim (such as the .awlsim/core/hardware.py) to define the data interface of ./awlsim/Process_mimic module. <br>
		
		cd ./awlsim
		python awlsim-server Elevator_300project.awlpro
		python awlsim-client -r RUN  
		python awlsim-client -r Stop 

2. Hardware PLC is developed based on the OpenOPC for Python Library Module. 

	The interface of reading/writing PLC memory is defined as an Opc *class*. 
		
		import ./hardware_interface/Opc

## Construct the Gcode <br>
Taking the PLC IL program as input, the developed parser generates the dependencies between input and output variables. <br>

```
cd ./STL_Parser
python -m core.main
```
## Construct the Gdata <br>

With the historical SCADA data, the developed graph construction generates causalities between sensor readings and control commands. 

The construction of Gdata consists of two basic modules. Specifically, <br>
1. Identify the node set, using the defined function (./ares/node_classification.m). 
	
	```
	examples:
	load('./data_withoutattack/elevator_data_training.mat', 'data_raw'); 
	threshold = 0.1;
	[sensor_set, command_set, command_delayed_set, ~, ~, ~, redundant_id, constant_id] = node_classification(data_raw, threshold)
	```

2. Identify the edge set, using the defined function (./ares/EdgeSetConstruction.m). 
	
	```
	[G_data, ~] = EdgeSetConstruction(data_raw(1:identify_length, :), sensor_set, command_set, command_delayed_set, redundant_id, info_delta_min,occupation_min, transferdelay, autocorrelation, tau)
	```


## Construct the Gcross <br>

With the identified Gcode and Gdata as inputs, the developed matching algorithm enumerates and validates all the feasible one-to-one mapping between PLC program variables and SCADA data variables. 

The construction of Gcross has two essential modules. 
1. Schedule the feasible mapping in a dynamic programming way (./ares/Graph_mapping.m). 

	```
	[Mappings, ~, ~] = Graph_mapping(G_code, G_data, data_for_mapping, redundant_id, constant_id, mapping_threshold, mapping_greedy, savefilepath );

	% exemplary parameters 
	mapping_threshold = 0.95 ;
	mapping_greedy = 1 ;
	savefilepath = "./data/Graphs/Graphs_length7000_occup1_info_1.000000e-01/mapping_results"; 
	mapping_data_period = 1:7000 ; 
	data_for_mapping = data_raw(mapping_data_period, :);
	```
2. Validate the feasible mapping by calling the PLC-Twin (./ares/PLC_Twin_CORE.m). 
	
	```
	% *inputs* are the verifying sensor readings  
	% *initialization* is the first record of the SCADA logs to initializing the PLC-Twin  
	[OUTPUTS] = PLC_Twin_CORE(inputs, initialization); 
	```

An integrated example for constructing the Gcross. 

	cd ./ares
	mrun Mapping_Parameters_analysis_CENTOR.m 


# Defense to ARES 

## Detect semantic attacks <br>
The implementation of online detection relies on the detailed information of ICS devices/software. 
We showcase the deployment of designed attack detection in our [Elevator Control System (ECS)](https://dl.acm.org/doi/10.1145/3560905.3568521), based on the PLC-Twin. 

1. Prepare the ICS detection environment. <br>
	
	1). Install [Siemens WinCC](https://www.siemens.com/global/en/products/automation/industry-software/automation-software/scada/simatic-wincc-v8/simatic-wincc-v7-basic-software.html) software in ECS. <br>
	2). Deploy a SCADA system, supporting the data logging. <br>

2. Prepare the required packets. <br> 

	```
	pip install -r requirements.txt
	```

3. Build the attack detection using PLC-Twin, including: <br>

	1). A setup interface (./detection/Elevator_300project.awlpro) <br>
		
		python awlsim-server Elevator_300project.awlpro
		python awlsim-client -r RUN  
		python awlsim-client -r Stop 
		
	2). An attack detection (./detection/awlsimhw_debug/main.py) <br>
		
		The CUSUM based attack detection is deployed, which will be loaded automatically 
		when start up the ".awlpro" project. 
		
	3). A data acquisition interface based on OpenOPC (./detection/awlsimhw_debug/readOpc.py) <br>
		
		Collect sensor readings and control commands from the SCADA database using OPC UA 
		protocol, which is achieved based on the "OpenOPC" python library. 
		This data collection module will be automatically loaded when start up the ".awlpro" 
		project. 
		
	4). Other utilities for data acquisition and conversion (./detection/utilsConvert/utilsConvert.py) <br>
		
		The data conversion between Awlsim and SCADA database is convert. 
		This conversion module will be automatically loaded when start up the ".awlpro" project. 


## Respond to semantic attacks <br>

Once an attack is detected, the responding strategy will be automatically activated based on the compromised program variables and their corresponding expected values. 

1. Localize the compromised program variables according to the cross-domain mappings between SCADA data and PLC program. <br>

```
Integrated in "./detection/awlsimhw_debug/main.py". 
```

2. Generate the expected values of the compromised program variables. <br>

```
Integrated in "./detection/awlsimhw_debug/main.py". 
```

3. Construct responding packets and send to the victim PLC. 

```
Achieved by exploiting the "Force" functions of industrial communication protocols. 
```
The exploitation of "Force" function for Siemens PLC and Rockwell PLC is coming later... 


## Legal and Ethical Considerations <br>

The response to semantic attacks makes use of the "Force" function of the industrial communication protocols. However, the "Force" function may also be utilized by adversaries, threatening the real industrial control systems. For the legal and ethical considerations, the exploitation of "Force" function will be published when the authentication weakness of protocols is fixed. 

