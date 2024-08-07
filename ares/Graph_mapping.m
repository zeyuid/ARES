function [Mappings, mapping_cyclic_num, mappings_files_path] = Graph_mapping(G_code, G_data, data_raw, redundant_id, constant_id, threshold, greedy, savefilepath ) 
% Outs2Coms_mappping, Multiple Outs to multiple commands, 

global cycle_time
cycle_time = 0;

[input_row, ~] = size(data_raw) ; 
data_raw(:, [end+1, end+2] ) = [ zeros(input_row,  1, 'logical') , ones(input_row,  1, 'logical') ] ; 


codefield_name = ["OUT_sym", "INPUT_sym", "OUT", "IN", "Deg"] ; 
mapfield_name = ["OUT", "COM", "IN", "SENSOR", "Deg"] ; 

mapping_saving_path = sprintf("/mapping_starting1_length%d_greedypara_%d/",  input_row, greedy ) ;
mappings_files_path = savefilepath + mapping_saving_path ; 

if ~exist(mappings_files_path, 'dir')
    mkdir( mappings_files_path );
end


% Define: Mappings (Out_addr, Comms, In_addr, Sensors, fitness ) 
% Define: previous_Mappings, (the mapped Out_addr and Comms, and, In_addr and Sensors ) 
% Define: Using_Mappings (Mapped_Out_addr, Mapped_Comms, Selected_In_addr, Selected_Sensors, fitness ) 
% Define: Non_Using_Mappings (Mapped_Out_addr, Mapped_Out_addr, Non_Selected_In_addr, Non_Selected_Sensors, fitness ) 

mapping_cyclic_num = zeros(1, size(G_code, 2) ) ; 
Mappings = cell(5, 1) ; 


% Mappings updating  
for i = 1 : size(G_code, 2) 
    
    % setting interrupt 
    % this is used for checking the interupted version   
    checkfilename = sprintf('mapping_%d.mat', i)  ; 
    if exist(mappings_files_path + checkfilename, "file") 
        load(mappings_files_path + checkfilename)
        continue ; 
    end
    
    
    %%%%%%%% PART I
    %%%%%%%% Unify the "all_sensors_permutations" by using the "redundant_id" information from G_data  
    %%%%%%%% 
    %%%%%%%% clear up the variable "Mappings" as the way, high efficiently   
    %%%%%%%% 
    %%%%%%%% unique the redundant sensors, only keep one permutation for redundant variables  
    
    
    % % % find the related input addresses and its sensor ids  
    previous_Mappings = cell2struct(Mappings(:, 1), mapfield_name , 1) ; 
    
    % % % construct the using/non-using Sensor_permutations (for Input_address)  
    all_sensors_permutations = reshape([Mappings{4, :}],  length(previous_Mappings.IN), size(Mappings, 2) )' ;  
    
    % for each column of correlated_sensors_permutations, if all its sensor solution belongs to one "redundant_id" variables pair  
    % then, only keep one of them, as the sensor solutions  
    % else, continue to skip 
    for sensor = 1: size(all_sensors_permutations, 2) 
        % justify whether sensor in the redundant sensor variables list  
        Input_sensors = unique(all_sensors_permutations(:, sensor) ,  'rows', 'stable') ; 
        
        % for a inout addrsss, if and only if all the solusions belong to one redundant variables  
        if length(Input_sensors) > 1 && length(Input_sensors) <= size(redundant_id, 2) 
            
            [row, ~] = find( redundant_id == Input_sensors(1) ) ; 
            if ~isempty(setdiff( Input_sensors, redundant_id(row, :) )) 
                continue ; 
            end
            
            m = 1 ;
            while intersect( redundant_id(row, m), all_sensors_permutations(1, 1 : sensor-1 ) ) 
                m = m+1 ; 
                if m > size(redundant_id, 2) 
                    sprintf("!!! Error: violate the one sensor for one input address rule: %d !!!", redundant_id(row, m) )  
                    break ; 
                end
            end
            if m <= size(redundant_id, 2) 
                all_sensors_permutations(:, sensor) = redundant_id(row, m) ; 
            end
        end
    end
    
    
    %%%%%%%% PART II 
    %%%%%%%% generate the "Clean_Using_Mappings", using for combining/updating   
    %%%%%%%% theoritcally, "Clean_Using_Mappings" is "Mappings"  
    
    all_fitness = reshape([Mappings{5, :}],  length(Mappings{5, 1} ), size(Mappings, 2) )' ;  
    all_command_sensors_permutations = [reshape([Mappings{2,:}], length(Mappings{2,1}), size(Mappings, 2) )' , all_sensors_permutations, all_fitness] ; 
    all_command_sensors_permutations = unique(all_command_sensors_permutations, 'rows', 'stable') ;   % sensor permutations matrix  
    Clean_Using_Mappings = cell(5, size(all_command_sensors_permutations, 1) ) ; 
    
    
    for permute = 1: size(all_command_sensors_permutations, 1) 
        
        if isempty(all_command_sensors_permutations)
            Clean_Using_Mappings{1, permute} = zeros(1, 0) ; 
            Clean_Using_Mappings{3, permute} = zeros(1, 0) ; 
            Clean_Using_Mappings{5, permute} = zeros(1, 0) ; 
        else
            Clean_Using_Mappings{1, permute} = previous_Mappings.OUT ; % (all mapped output node address in previous Mappings)
            Clean_Using_Mappings{3, permute} = previous_Mappings.IN ;  % (all mapped input node address in previous Mappings)
            Clean_Using_Mappings{5, permute} = all_command_sensors_permutations(permute, end) ; 
        end
        
        Clean_Using_Mappings{2, permute} = all_command_sensors_permutations(permute, 1: length(previous_Mappings.COM) ) ; % (solutions for last items)
        Clean_Using_Mappings{4, permute} = all_command_sensors_permutations(permute, length(previous_Mappings.COM)+1 : end-1 ) ;  % (solutions for last items)
    end
    
    
    %%%%%%%% PART III 
    %%%%%%%% generate the "Using_Mappings"  
    
    Outaddr_pair = G_code(:, i) ;  % cell type 
    Outnode = cell2struct(Outaddr_pair, codefield_name , 1) ;     
    correlated_In_addr = Outnode.IN ; 
    correlated_I_posi = zeros(1, length(correlated_In_addr)) ; 
    for in_addr = 1:length(correlated_In_addr)
        % the positions in 1:length(previous_Mappings.IN) 
        position = find( previous_Mappings.IN == correlated_In_addr( in_addr ) ); 
        if ~isempty(position) 
            correlated_I_posi(in_addr) = position ; 
        end
    end
    correlated_I_posi(correlated_I_posi == 0) = []; 
    
    % find the useful solultions for OutNode, and useless solultions for OutNode  
    correlated_sensors_permutations = all_sensors_permutations(:, correlated_I_posi ) ;  
    % combine the sensors permutation with its commands order  
    commands_correlated_sensors = [reshape([Mappings{2,:}], length(Mappings{2,1}), size(Mappings, 2) )' , correlated_sensors_permutations, all_fitness] ; 
    % in each row, [1: length(previous_Mappings.COM)] record the commands' id,  
    % in each row, [length(previous_Mappings.COM)+1: end] record the sensors' id,  

    % remove the repeated solutions for the pair of commands and sensors 
    commands_correlated_sensors = unique(commands_correlated_sensors, 'rows', 'stable') ;   % sensor permutations matrix  
    
    
    % % %  the Mapped Output_address  
    Mapped_Out_addr = previous_Mappings.OUT ; 
    % % %  the using Input_address  
    Using_Mapping_In_addr = previous_Mappings.IN(correlated_I_posi) ; 
    
    if Using_Mapping_In_addr
        % sort the commands_correlated_sensors, to decide the length of repeated sensor permutation solutions     
        commands_correlated_sensors = sortrows(commands_correlated_sensors, length(Mappings{2,1}) + 1 ) ; 
        
        Using_Mappings = cell(5, size(commands_correlated_sensors, 1) ) ; 
        permute_count = 0; 
        for permute = 1: size(commands_correlated_sensors, 1) 
            
            if permute_count == 0 
                % if updating_init or new sensors permutation shows up  
                permute_count = permute_count +1 ;
                Using_Mappings{1, permute_count} = Mapped_Out_addr ; 
                Using_Mappings{2, permute_count} = commands_correlated_sensors(permute, 1: length(previous_Mappings.COM) ) ; 
                Using_Mappings{3, permute_count} = Using_Mapping_In_addr ; 
                Using_Mappings{4, permute_count} = commands_correlated_sensors(permute, length(previous_Mappings.COM)+1 : end-1 ) ; 
                Using_Mappings{5, permute_count} = commands_correlated_sensors(permute, end) ; 
                same_sensor_permute = 0 ; 
            else
                new_sensor_exist = sum(commands_correlated_sensors(permute , length(previous_Mappings.COM)+1 : end-1 ) == Using_Mappings{4, permute_count} ) ~= length(Using_Mappings{4, permute_count})  ; 
                
                if new_sensor_exist
                    % if updating_init or new sensors permutation shows up  
                    permute_count = permute_count +1 ;
                    Using_Mappings{1, permute_count} = Mapped_Out_addr ; 
                    Using_Mappings{2, permute_count} = commands_correlated_sensors(permute, 1: length(previous_Mappings.COM) ) ; 
                    Using_Mappings{3, permute_count} = Using_Mapping_In_addr ; 
                    Using_Mappings{4, permute_count} = commands_correlated_sensors(permute, length(previous_Mappings.COM)+1 : end-1 ) ; 
                    Using_Mappings{5, permute_count} = commands_correlated_sensors(permute, end) ; 
                    same_sensor_permute = 0 ; 
                else
                    % check whether this values include this command sets 
                    same_sensor_permute = same_sensor_permute+1; 
                    for check = permute-same_sensor_permute : permute-1 
                        
                        command_permu_ans = commands_correlated_sensors(permute, 1: length(previous_Mappings.COM)) ; 
                        command_permu_ans_check = commands_correlated_sensors(check, 1: length(previous_Mappings.COM)) ; 
                        
                        new_command_exist = ~isempty( setdiff( command_permu_ans, command_permu_ans_check )); 

                        if new_command_exist
                            permute_count = permute_count +1 ;
                            Using_Mappings{1, permute_count} = Mapped_Out_addr ; 
                            Using_Mappings{2, permute_count} = commands_correlated_sensors(permute, 1: length(previous_Mappings.COM) ) ; 
                            Using_Mappings{3, permute_count} = Using_Mapping_In_addr ; 
                            Using_Mappings{4, permute_count} = commands_correlated_sensors(permute, length(previous_Mappings.COM)+1 : end-1 ) ; 
                            Using_Mappings{5, permute_count} = commands_correlated_sensors(permute, end) ; 
                            break ;
                        else
                            continue ;
                        end
                    end
                end
            end
            
        end
        Using_Mappings(:, permute_count+1 :end) = [] ; 
        
    else
        Using_Mappings = cell(5, 0) ; 
    end
    
    
    %%%%%%%% PART IV 
    %%%%%%%% generate the Using_Mappings_updated
    
    Using_Mappings_updated = Out2Coms_mapping( Outaddr_pair, G_data, data_raw, Using_Mappings, threshold, greedy, redundant_id, length(constant_id) ) ; 
    
    %%%%% store the varibles "Using_Mappings_updated" before combining with the Clean_Using_Mappings(Whole mapping before)  
	filename = sprintf("Using_Mappings_updated%d.mat", i ) ; 
    save(mappings_files_path + filename, "Using_Mappings_updated") 
    
    % store the middle-information in the mappings_files_path .txt file 
    mapping_cyclic_num(1, i) = cycle_time ; 
    fid = fopen(mappings_files_path+'cyclic_number_logs.txt', 'a') ;
    cycle_time_sym = sprintf("!!!Execute %d cyclcs for the %dth G code !!!\n", cycle_time, i)  
    fprintf(fid, "\n" ) ; 
    fprintf(fid, cycle_time_sym );
    fclose(fid); 
    cycle_time = 0 ;
    
    
    %%%%%%%% PART V %%%%%%%%
    %%%%%%%% combine the updated "Using_Mappings_updated" 
    %%%%%%%% with the Clean_Using_Mappings(Whole mapping before)  
    
    Mappings_updated = cell(5, 0) ;
    for clean_update = 1 : size(Clean_Using_Mappings, 2) 
        used_command_solution = Clean_Using_Mappings{2, clean_update}; 
        used_sensor_solution = Clean_Using_Mappings{4 , clean_update}(correlated_I_posi) ; 
        all_sensor_solution_before = Clean_Using_Mappings{4 , clean_update} ; 
        for using_update = 1 : size(Using_Mappings_updated, 2) 
            added_com = Using_Mappings_updated{2, using_update} ; 
            added_sen_permu = Using_Mappings_updated{4, using_update} ; 
            
            % the incremental commands solution not exist in used_command_solution   
            command_satified = isempty(intersect(added_com, used_command_solution)) ;
            % the used historical sensors solution are selected from Clean_Using_Mappings{4 , clean_update} 
            % i.e., equally to added_sen_permu  
            sensor_satified = sum(used_sensor_solution == added_sen_permu(1: length(correlated_I_posi)) ) == length(correlated_I_posi) ;
            confilicted_solutions = intersect(setdiff(all_sensor_solution_before, used_sensor_solution), added_sen_permu); 
            
            not_solutions_confilict = isempty(setdiff( confilicted_solutions,  [size(data_raw, 2)-1, size(data_raw, 2)] ));
            
            
            if command_satified && sensor_satified && not_solutions_confilict 
                updating_store = cell(5, 1) ; 
                
                updating_store{1,1} = [ Clean_Using_Mappings{1, clean_update} , Using_Mappings_updated{1, using_update} ] ;   
                updating_store{2,1} = [used_command_solution, added_com] ; 
                updating_store{3,1} = [ Clean_Using_Mappings{3, clean_update} , Using_Mappings_updated{3, using_update}(length(correlated_I_posi)+1 : end) ] ; 
                updating_store{4,1} = [ Clean_Using_Mappings{4, clean_update} , added_sen_permu(length(correlated_I_posi)+1 : end) ] ; 
                updating_store{5,1} = Using_Mappings_updated{5, using_update} ; 
                
                Mappings_updated = [Mappings_updated, updating_store ] ; 
            end
        end
    end
    
    %%%%%%%% PART VI 
    %%%%%%%% replace variables "Mappings" with the combined/updated "Using_Mappings_updated"  
    %%%%%%%% i.e., Mappings_updated  
    
    if isempty(Mappings_updated)
        sprintf("Can not find a mapping for output variable %d!" , i ) 
        % Mappings is still the Clean_Using_Mappings in last cycle  
        Mappings = Clean_Using_Mappings ; 
    else
        Mappings = Mappings_updated ;
    end
    
    
    %%%%%%%%%%%%% %%%%%%%%%%%%% %%%%%%%%%%%%% %%%%%%%%%%%%% 
	%%%%%%%%%%%%% replace all the redunant variables 
    %%%%%%%%%%%%% 
    %%%%%%%%%%%%% %%%%%%%%%%%%% %%%%%%%%%%%%% %%%%%%%%%%%%% 
    all_sensors_permutations = reshape([Mappings{4, :}],  length(Mappings{4, 1}), size(Mappings, 2) )' ;  
    if  size(all_sensors_permutations, 1) > 1
        for sensor = 1: size(all_sensors_permutations, 2)
            % justify whether sensor in the redundant sensor variables list
            Input_sensors = all_sensors_permutations(:, sensor) ;
            % for a inout addrsss, if and only if all the solusions belong to one redundant variables

            for sensor_instance = 1:length(Input_sensors)

                [row, ~] = find( redundant_id == Input_sensors(sensor_instance) ) ;
                if isempty( row )
                    % if sensor_instance not in the redundant_id, skip
                    continue ;
                else
                    m = 1 ;
                    while intersect( redundant_id(row, m), all_sensors_permutations(sensor_instance, 1 : sensor-1 ) ) 
                        m = m+1 ;
                        if m > size(redundant_id, 2)
                            sprintf("!!! Mapping error !!!\n")
                            sprintf("!!! Error: violate the one sensor for one input address rule: \n for %d colunm  %d row of correlated_sensors_permutations !!!",sensor, sensor_instance )
                            break ;
                        end
                    end
                    replaced_reduantant  = redundant_id(row, m) ;
                    Input_sensors(sensor_instance) = replaced_reduantant ;
                    
                    % then replace all redunant variable in redundant_set_backup with replaced_reduantant  
                    for mmm = sensor_instance+1 : length(Input_sensors)
                        if isempty(find( redundant_id(row, :) == Input_sensors(mmm), 1))
                            continue ;
                        else
                            Input_sensors(mmm) = replaced_reduantant ;
                        end
                    end
                end
            end
            all_sensors_permutations(:, sensor) = Input_sensors ; 
        end
    end

    
    %%%%%%%%%%%%% %%%%%%%%%%%%% %%%%%%%%%%%%% %%%%%%%%%%%%% 
	%%%%%%%%%%%%% remove the repeated Mappings solutions 
    %%%%%%%%%%%%% 
    %%%%%%%%%%%%% %%%%%%%%%%%%% %%%%%%%%%%%%% %%%%%%%%%%%%% 
    all_command_permutations = reshape([Mappings{2,:}], length(Mappings{2,1}), size(Mappings, 2) )'  ; 
    all_fitness = reshape([Mappings{5, :}],  length(Mappings{5, 1} ), size(Mappings, 2) )' ;  
    all_command_sensors_permutations = [all_command_permutations, all_sensors_permutations, all_fitness] ; 
    all_command_sensors_permutations = unique(all_command_sensors_permutations, 'rows', 'stable') ;   % sensor permutations matrix  
    
    % construct: Updating_Mappings (Mapped_Out_addr, Mapped_Out_addr, Non_Selected_In_addr, Non_Selected_Sensors, fitness ) 
    Updating_Mappings = cell(5, size(all_command_sensors_permutations, 1) ) ; 
        
    for permute = 1: size(all_command_sensors_permutations, 1) 
        Updating_Mappings{1, permute} = Mappings{1, 1} ;  % (all mapped output node address in previous Mappings)
        Updating_Mappings{2, permute} = all_command_sensors_permutations(permute, 1: length(Mappings{2, 1} )) ; % (solutions for last items)
        Updating_Mappings{3, permute} = Mappings{3, 1} ;  % (all mapped input node address in previous Mappings)
        Updating_Mappings{4, permute} = all_command_sensors_permutations(permute, length(Mappings{2, 1}) + 1 : end-1 ) ;  % (solutions for last items)
        Updating_Mappings{5, permute} = all_command_sensors_permutations(permute, end) ;
    end
    
    Mappings = Updating_Mappings ; 
    
    sprintf("Mapping progress: %d/%d ... ", i, size(G_code, 2)) 
    filename = sprintf('mapping_%d.mat', i)  ; 
    save(mappings_files_path + filename, "Mappings", "mapping_cyclic_num") ;
end
sprintf("Mapping finished! ") 

end



