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

	cd ./STL_Parser
	python -m core.main

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

	%%% exemplary parameters %%%
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

3. An integrated example for constructing the Gcross. 
	
	```
	cd ./ares
	mrun Mapping_Parameters_analysis_CENTOR.m 
	```

# Usages of Cross-domain invariants (the Gcross)

## Mount semantic attacks <br>

The exploitation of "Force" function for Siemens PLC and Rockwell PLC is coming soon!

## Detect semantic attacks <br>

python ./data_segmentation/segmenting_utils.py

Example: 

## Respond to semantic attacks <br>

The exploitation of "Force" function for Siemens PLC and Rockwell PLC is coming soon!




# Legal and Ethical Considerations <br>

<!-- The response to semantic attacks utilizes the "Force" function of industrial communication protocols. However,  -->
The utilization of the "Force" function may be utilized by adversaries and further threaten the real critical infrastructure. For the legal and ethical considerations, the exploitation of "Force" function for Siemens PLC and Rockwell PLC will be published when the authentication weakness of protocols is fixed. 

