function [Outnode_Mappings] = Out2Coms_mapping( Outaddr_pair, G_data, data_raw, Mappings_before, threshold, greedy, redundant_id, constant_num)  
% One Out to multiple commands

% Generate Mappings_updated, atop on the previous Mappings and current Outaddr_pair 
% Map "Outaddr" with all "G_data" pairs, the solution is the mapping with maximum fitness(larger than a thershold (0.95))   

% data_raw has been padded with 2 column: one for false, one for true. 
% False vol.num : size(data_raw,2)-1
% True vol.num : size(data_raw,2)

% length(constant_id) 


[input_row, ~] = size(data_raw) ; 



commandfield_name = ["command", "SENSOR", "weight", "occupation", "Deg"] ; 
codefield_name = ["OUT_sym", "INPUT_sym", "OUT", "IN", "Deg"] ; 
mapfield_name = ["OUT", "COM", "IN", "SENSOR", "Deg"] ; 

Outnode = cell2struct(Outaddr_pair, codefield_name , 1) ; 
degree_out = Outnode.Deg ; 




if ~isempty(Mappings_before)
    
    In_addr_left = setdiff(Outnode.IN, Mappings_before{3, 1} ) ;
    if isempty(In_addr_left)
        % only keep the diveristy of sensor permutaion, 
        % ignore the diveristy of commands permutation,  
	    % because in the following, we don't use the historical commands mapping information   
        % this will reduce the the times from 128 to 16 
        correlated_sensors_permutations = reshape([Mappings_before{4, :}],  length(Mappings_before{4, 1} ), size(Mappings_before, 2) )' ; 
        
        
        correlated_sensors_permutations = unique(correlated_sensors_permutations ,  'rows', 'stable') ; 
        
        Using_Mappings = cell(5, size(correlated_sensors_permutations, 1) ) ; 
        for permute = 1: size(correlated_sensors_permutations, 1) 
            Using_Mappings{1, permute} = Mappings_before{1, 1} ; % can be any value, because it is useless in the following steps   
            Using_Mappings{2, permute} = Mappings_before{2, 1} ; % can be any value, because it is useless in the following steps   
            Using_Mappings{3, permute} = Mappings_before{3, 1} ; % same ones, (all mapped input node address in previous Mappings)
            Using_Mappings{4, permute} = correlated_sensors_permutations(permute , :) ;  % (solutions for last items) 
            Using_Mappings{5, permute} = Mappings_before{5, 1} ; % can be any value, because it is useless in the following steps    
        end
        Mappings_before = Using_Mappings ;
    else
        correlated_sensors_permutations = reshape([Mappings_before{4, :}],  length(Mappings_before{4, 1} ), size(Mappings_before, 2) )' ; 
        
        correlated_sensors_permutations = unique(correlated_sensors_permutations ,  'rows', 'stable') ; 
        

        cyclic_time_using_command_info = size(Mappings_before, 2) * (21-length(Mappings_before{2,1}) ) ; 
        cyclic_time_nonusing_command_info =  size(correlated_sensors_permutations, 1) * (21) ; 
        
        if cyclic_time_nonusing_command_info < cyclic_time_using_command_info
            % update the Mappings_before without the command info. 
            
            Using_Mappings = cell(5, size(correlated_sensors_permutations, 1) ) ; 
            for permute = 1: size(correlated_sensors_permutations, 1) 
                Using_Mappings{1, permute} = [] ; % can be any value, because it is useless in the following steps   
                Using_Mappings{2, permute} = [] ; % can be any value, because it is useless in the following steps   
                Using_Mappings{3, permute} = Mappings_before{3, 1} ; % same ones, (all mapped input node address in previous Mappings)
                Using_Mappings{4, permute} = correlated_sensors_permutations(permute , :) ;  % (solutions for last items) 
                Using_Mappings{5, permute} = Mappings_before{5, 1} ; % can be any value, because it is useless in the following steps    
            end
            Mappings_before = Using_Mappings ;
            
        end
    end

    Outnode_Mappings = cell(5, 0) ;
    % Outnode_Mappings record all mappings, under all Mappings_before  
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%% debug: for solution = 1
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % do the mapping under the each given mapping solution 
    for solution = 1:size( Mappings_before , 2) 
        Outaddrmappings = cell(5, 0 ) ;
        % Given solution(:, i), Outaddrmappings record all mappings between Outnode and Commandnode 
        
        % update the code variables with data, under Mapping  
        partial_map = Mappings_before(:, solution) ;
        partial_mapping = cell2struct(partial_map, mapfield_name , 1) ; 
        
        
        In_addr_left = setdiff(Outnode.IN, partial_mapping.IN ) ; % can be omitted  
        if ~isempty(In_addr_left)
            % the input address is not totally decided by "partial_map"  
            
            % map Outaddr_pair with all command node in G_data 
             
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            %%%%%%%%%%%% debug: for solution = 1
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            for i = 1 : size(G_data, 2) 
                %%%%%%%%% if partial_map.COM include G_data{1, i}, continue  
                if intersect( G_data{1, i}, partial_mapping.COM ) 
                    continue ; 
                end
                
                %%%%%%%%% else, do the mapping  
                Commandnode = cell2struct(G_data(:, i), commandfield_name , 1) ; 
                degree_com = Commandnode.Deg ; 
                
                Sensor_left = setdiff(Commandnode.SENSOR, partial_mapping.SENSOR ) ; 
                
                % 3 is number of i 
                if length(In_addr_left) - length(Sensor_left)<0 || length(In_addr_left) - length(Sensor_left)> constant_num 
                    continue ; 
                end
                %%%%%%%%% if the "degree_out < degree_com" breaks the PLC graphs degree rule  
                %%%%%%%%% if the "Commandnode.occupation" < 0.999, we believe the G_data{:, i} is not well constructed, 
                %%%%%%%%% and indicates a larger node degree for command G_data{1, i}  
                if (degree_out < degree_com) || (degree_out == degree_com && Commandnode.occupation < 0.999)
                    continue ; 
                else
                    % return the map for Un-ordered input address: 
                    Out2Com = Out2Com_mapping(partial_map, Outaddr_pair, G_data(:, i), data_raw, redundant_id, threshold , greedy) ; 
                    Outaddrmappings = [Outaddrmappings, Out2Com] ; 
                    % Outaddrmapping logs results for Commandnode among all G_data command node 
                end 
            end
            
        else
            % the input addresses are totally decided by "partial_map",  
            % only runs one time awlsim 
            
            input_addr_posi_exist = partial_mapping.IN ; 
            % INPUTS = zeros( input_row , ceil( max( [input_addr_posi_exist, input_addr_posi]+1 )/8 ) *8, 'logical') ; 
            INPUTS = zeros( input_row, 32, 'logical') ; % adjust by the input length  
            INPUTS(:, end - input_addr_posi_exist) = data_raw(:, partial_mapping.SENSOR) ; 
            
            % add the initialzation 
            initialization = cell(2,1) ;
            initialization{1, 1} = data_raw(1, 1:25) ;
            initialization{2, 1} = data_raw(1, 26:46 ) ;

            
            % run alwsim given the INPUTS  
            OUTPUTS = IL_analyzer_CORE(INPUTS, initialization);
            output_estimate = OUTPUTS(:, end - Outnode.OUT) ; % from the bottom direction 
            
            % only keep the diveristy of sensor permutaion, 
            % ignore the diveristy of commands permutation,  
            % because in the following, we don't use the historical commands mapping information   
            % this will reduce the the times from 128 to 16   
            for i = 1: size(G_data, 2)
                
%                 %%%%%%%%% if partial_map.COM include G_data{1, i}, continue  
%                 if intersect( G_data{1, i}, partial_mapping.COM ) 
%                     continue ; 
%                 end
                
                Commandnode = cell2struct(G_data(:, i), commandfield_name , 1) ; 
                
                degree_com = Commandnode.Deg ; 
                % if the candidate command node satisfies degree pricinple before/after filling current solution  
                if (degree_out <  degree_com ) || (degree_out == degree_com && Commandnode.occupation < 0.999)
                    continue ;
                else
                    % if the Commandnode.SENSOR is not fully filled, break the degree rules   
                    Sensor_left = setdiff(Commandnode.SENSOR, partial_mapping.SENSOR ) ; 
                    if isempty(Sensor_left)
                        output_expected = data_raw(:, Commandnode.command ) ;
                        
                        fitness = Out2Com_Fit(output_expected, output_estimate) ; 
                        % build and update the mapping table for the Outnode and the Commandnode     
                        Out2Com = {Outnode.OUT; Commandnode.command; [partial_mapping.IN]; [partial_mapping.SENSOR]; fitness } ; 
                        Outaddrmappings = [Outaddrmappings, Out2Com] ; 
                    end
                end
            end
        end
        % Given solution(:, i), Outaddrmappings record all mappings between Outnode and Commandnode 
        
        
        % find the largest fitness among all input address combinations   
        fitness_all = [Outaddrmappings{5, :}] ; 
        max_fitness = max( fitness_all ); 
        if max_fitness > threshold  % selected 0.95 
            Mappings_part_solution = Outaddrmappings(:, fitness_all >= greedy*max_fitness ) ; 
        else
            Mappings_part_solution = cell(5, 0 );
            sprintf("Mappings(:, %d) meets conflicts !", solution) 
        end 
        Outnode_Mappings = [Outnode_Mappings, Mappings_part_solution] ;
    end
    
    % end generate "Mappings_part_solution" when all "Mappings_before" is used 
    % Outnode_Mappings record all mappings, under all Mappings_before  
    % Select Outnode_Mappings as those with maximum Outnode_Mappings{5, :}  
    
    fitness_all = [Outnode_Mappings{5, :}] ; 
	max_fitness = max( fitness_all ); 
    if max_fitness > threshold  % selected 0.95 
        Outnode_Mappings = Outnode_Mappings(:, fitness_all >= greedy*max_fitness ) ; 
        
        
        % if exist the length of (sensor-input) pair smaller than degree_out, then non-validated   
        % because the input memory cannot be assigned with any values, else, the system is not specifed controlled 
        validated_mapping = [] ; 
        validated_mapping_length = 0 ; 
        for mapping_solution_id = 1: size(Outnode_Mappings , 2)
            if length(Outnode_Mappings{3, mapping_solution_id}) >= validated_mapping_length
                validated_mapping_length = length(Outnode_Mappings{3, mapping_solution_id}) ;
            end
        end
        
        for mapping_solution_id = 1: size(Outnode_Mappings , 2)
            if length(Outnode_Mappings{3, mapping_solution_id}) == validated_mapping_length 
                validated_mapping = [validated_mapping, mapping_solution_id] ; 
            end
        end
        
        Outnode_Mappings = Outnode_Mappings(:, validated_mapping) ; 
        
        
        
         % unique the Outnode_Mappings 
        try 
            all_command_permutations = reshape([Outnode_Mappings{2, :}],  length(Outnode_Mappings{2, 1} ), size(Outnode_Mappings, 2) )' ;  
        catch
            savepath  = strcat('3000_Index_in_position_2_exceeds_array_bound-', datestr(now,'HH-MM-SS')) ;
            save(savepath)
        end
        all_inputs_sequences = reshape([Outnode_Mappings{3, :}],  length(Outnode_Mappings{3, 1} ), size(Outnode_Mappings, 2) )' ;  
        all_sensors_permutations = reshape([Outnode_Mappings{4, :}],  length(Outnode_Mappings{4, 1} ), size(Outnode_Mappings, 2) )' ;  
        all_fitness = reshape([Outnode_Mappings{5, :}],  length(Outnode_Mappings{5, 1} ), size(Outnode_Mappings, 2) )' ;  
        
        commands_correlated_sensors = [all_command_permutations, all_inputs_sequences, all_sensors_permutations, all_fitness] ; 
        commands_correlated_sensors = unique(commands_correlated_sensors, 'rows', 'stable') ;   % sensor permutations matrix  
        
        Unique_Mappings = cell(5, size(commands_correlated_sensors, 1) ) ; 
        for permute = 1: size(commands_correlated_sensors, 1) 
            Unique_Mappings{1, permute} = Outnode.OUT ; % (all mapped output node address in previous Mappings)
            Unique_Mappings{2, permute} = commands_correlated_sensors(permute, 1: length(Outnode_Mappings{2, 1}) ) ; % (solutions for last items)
            Unique_Mappings{3, permute} = commands_correlated_sensors(permute, length(Outnode_Mappings{2, 1})+[1:length(Outnode_Mappings{3, 1})] ) ; % (solutions for last items)            
            Unique_Mappings{4, permute} = commands_correlated_sensors(permute, length(Outnode_Mappings{2, 1})+length(Outnode_Mappings{3, 1})+[1:length(Outnode_Mappings{4, 1})] ) ;  % (solutions for last items)
            Unique_Mappings{5, permute} = commands_correlated_sensors(permute, end) ; 
        end
        Outnode_Mappings = Unique_Mappings ; 
    else
        Outnode_Mappings = cell(5, 0 );
    end
    
    % Outnode_Mappings are the mappings of Outaddr_pair, under all "Mappings_before"  
else
    % do mapping without Mappings solutions exist 
    partial_map = cell(5, 0) ; 
    Outaddrmappings = cell(5, 0) ; 
    
	%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
	%%%%%%%%%% debug: change the iterations 
	%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    for i = 1 : size(G_data, 2) 
        % periodiclly connect "Outaddr_pair" with G_data(i)
        Commandnode = cell2struct(G_data(:, i), commandfield_name , 1) ; 
        degree_com = Commandnode.Deg; 
        if (degree_out < degree_com) || (degree_out == degree_com && Commandnode.occupation < 0.999)
            continue;
        else
%             if exist('unique_debugging.mat', "file")
%                 load('unique_debugging.mat', 'Outaddrmappings') ;
%             else
            Out2Com = Out2Com_mapping(partial_map, Outaddr_pair, G_data(:, i), data_raw, redundant_id, threshold, greedy) ; 
            Outaddrmappings = [Outaddrmappings, Out2Com] ; 
%             end
        end
    end
    % find the largest fitness among all input address combinations   
    fitness_all = [Outaddrmappings{5, :}] ; 
    max_fitness = max( fitness_all ); 
    if max_fitness > threshold  % selected 0.95 
        Outnode_Mappings = Outaddrmappings(:, fitness_all >= greedy*max_fitness ) ;     
        
        % if exist the length of (sensor-input) pair smaller than degree_out, then non-validated   
        % because the input memory cannot be assigned with any values, else, the system is not specifed controlled 
        validated_mapping = [] ; 
        validated_mapping_length = 0 ; 
        for mapping_solution_id = 1: size(Outnode_Mappings , 2)
            if length(Outnode_Mappings{3, mapping_solution_id}) >= validated_mapping_length
                validated_mapping_length = length(Outnode_Mappings{3, mapping_solution_id}) ;
            end
        end
        
        for mapping_solution_id = 1: size(Outnode_Mappings , 2)
            if length(Outnode_Mappings{3, mapping_solution_id}) == validated_mapping_length 
                validated_mapping = [validated_mapping, mapping_solution_id] ; 
            end
        end
        Outnode_Mappings = Outnode_Mappings(:, validated_mapping) ; 
        
        
        % unique the Outnode_Mappings 
        all_command_permutations = reshape([Outnode_Mappings{2, :}],  length(Outnode_Mappings{2, 1} ), size(Outnode_Mappings, 2) )' ;  
        all_inputs_sequences = reshape([Outnode_Mappings{3, :}],  length(Outnode_Mappings{3, 1} ), size(Outnode_Mappings, 2) )' ;
        all_sensors_permutations = reshape([Outnode_Mappings{4, :}],  length(Outnode_Mappings{4, 1} ), size(Outnode_Mappings, 2) )' ;  
        all_fitness = reshape([Outnode_Mappings{5, :}],  length(Outnode_Mappings{5, 1} ), size(Outnode_Mappings, 2) )' ;  
        
        commands_correlated_sensors = [all_command_permutations, all_inputs_sequences, all_sensors_permutations, all_fitness] ;
        commands_correlated_sensors = unique(commands_correlated_sensors, 'rows', 'stable') ;   % sensor permutations matrix  

        Unique_Mappings = cell(5, size(commands_correlated_sensors, 1) ) ; 
        for permute = 1: size(commands_correlated_sensors, 1) 
            Unique_Mappings{1, permute} = Outnode.OUT ; % (all mapped output node address in previous Mappings)
            Unique_Mappings{2, permute} = commands_correlated_sensors(permute, 1: length(Outnode_Mappings{2, 1}) ) ; % (solutions for last items)
            Unique_Mappings{3, permute} = commands_correlated_sensors(permute, length(Outnode_Mappings{2, 1})+[1:length(Outnode_Mappings{3, 1})] ) ; % (solutions for last items)
            Unique_Mappings{4, permute} = commands_correlated_sensors(permute, length(Outnode_Mappings{2, 1})+length(Outnode_Mappings{3, 1})+[1:length(Outnode_Mappings{4, 1})] ) ;  % (solutions for last items)
            Unique_Mappings{5, permute} = commands_correlated_sensors(permute, end) ;
    
        end
        Outnode_Mappings = Unique_Mappings ; 
        
    else
        Outnode_Mappings = cell(5, 0 );
    end
    
end


end





