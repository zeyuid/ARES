function [Inaddr] = Out2Com_mapping(partial_map, Outaddr_pair, Comdata, data_raw, redundant_id, threshold, greedy ) 
% return the map of Un-ordered input address: 
% Inaddr: Outnode.OUT ; Commandnode.command ; In_addr_left; sensor_plan; mapping_fitness ; 
  
        
[input_row, ~] = size(data_raw) ; 

% data_raw has been padded with 2 column: one for false, one for true. 
% False vol.num : size(data_raw,2)-1
% True vol.num : size(data_raw,2)



codefield_name = ["OUT_sym", "INPUT_sym", "OUT", "IN", "Deg"] ; 
Outnode = cell2struct(Outaddr_pair, codefield_name , 1) ; 

commandfield_name = ["command", "SENSOR", "weight", "occupation", "Deg"] ; 
Commandnode = cell2struct(Comdata, commandfield_name , 1) ; 



mapfield_name = ["OUT", "COM", "IN", "SENSOR", "Deg"] ; 
if ~isempty(partial_map)
    % fill the address with the "partial_map"
    partial_mapping = cell2struct(partial_map, mapfield_name , 1) ; 
    
%     INPUTS = zeros( input_row , ceil( max( [input_addr_posi_exist, input_addr_posi]+1 )/8 ) *8, 'logical') ; 
    INPUTS = zeros( input_row, 32, 'logical') ; 
    INPUTS(:, end - partial_mapping.IN) = data_raw(:, partial_mapping.SENSOR) ; 
else
    partial_map = cell(5,1 ) ; 
    partial_mapping = cell2struct(partial_map, mapfield_name , 1) ; 
    INPUTS = zeros( input_row, 32, 'logical') ; 
%     INPUTS = zeros( input_row , ceil( max(input_addr_posi+1)/8 ) *8, 'logical') ; 
end

In_addr_left = setdiff(Outnode.IN, partial_mapping.IN ) ; 
Sensor_left = setdiff(Commandnode.SENSOR, partial_mapping.SENSOR ) ; 




if length(In_addr_left) < length(Sensor_left)
    Inaddr = cell(5, 0 ) ; 

% can be omitted, coverd by the length(In_addr_left) > length(Sensor_left)    
elseif length(In_addr_left) == length(Sensor_left)   
    % mapping the In_addr_left with Sensor_left
    % by enumerating all the sensor permutation
    
    % remove some redundant sensor id permutation from permutations 
%     permutations = perms( 1: length(Sensor_left)) ; 
%     if ~isempty(intersect(Sensor_left, redundant_id))
%         if length(intersect(Sensor_left, redundant_id)) > 1
%             % remove the redundant sensor id permutation from permutations 
%             % first find the redundant sensor column.id in Sensor_left 
%             % and only keep one of the the permutation, in   
%             permutations
%         end
%     end

    
    permutations = perms( 1: length(Sensor_left)) ; 
    
    % remove some redundant sensor id permutation from permutations
    if ~isempty(intersect(Sensor_left, redundant_id))
        if length(intersect(Sensor_left, redundant_id)) > 1
            % remove the redundant sensor id permutation from permutations
            % first find the redundant sensor column.id in Sensor_left
            % and only keep one of the the permutation, in

            for redu_id = 1: size(redundant_id, 1)
                % redu_in_sen_pemu = zeros( size(permutations, 1), size(redundant_id ,2) ) ;
                for sen_per_row = 1: size(permutations, 1) 
                    [a, ~] = find( repmat(Sensor_left(permutations(sen_per_row, :))', 1, length(redundant_id(redu_id, :))) == repmat(redundant_id(redu_id, :), length( permutations(1, :) ), 1) ) ;

                    if ~isempty(a)
                        % redu_in_sen_pemu((redu_id-1)*size(permutations, 1)+sen_per_row , : ) =  a';
                        permutations(sen_per_row, sort(a)') = permutations(sen_per_row, a) ;
                    end
                end

            end

        end
    end
    permutations = unique(permutations, 'rows', 'stable') ;

	fitness = zeros( size(permutations, 1), 1 ) ;
    
    INPUTS1 = INPUTS ;
    
    for i = 1 : size(permutations, 1) 
        
        INPUTS = INPUTS1 ;
        
        sensor_perm = Sensor_left( permutations(i, :) ) ; 
        INPUTS(:, end - In_addr_left) = data_raw(:, sensor_perm) ; 
        
        
        
        % add the initialzation
        initialization = cell(2,1) ;
        initialization{1, 1} = data_raw(1, 1:25) ;
        initialization{2, 1} = data_raw(1, 26:46 ) ;
        
        
        % run alwsim given the INPUTS  
        OUTPUTS = IL_analyzer_CORE(INPUTS, initialization);
        output_estimate = OUTPUTS(:, end - Outnode.OUT) ; % from the bottom direction 
        
        output_expected = data_raw(:, Commandnode.command ) ; 
        fitness(i, 1) = Out2Com_Fit(output_expected, output_estimate) ; 
        
    end
    
    max_fitness = max( fitness );
    if max_fitness > threshold  % selected 0.95 
        
        % build and update the mapping table for the Outnode and the Commandnode     
        % Inaddrmapping = {Commandnode.command; partial_mapping.IN; partial_mapping.SENSOR; fitness } ; 
        
        sensor_mapping = permutations( fitness >= greedy*max_fitness , : ); 
        fitness_selected = fitness( fitness >= greedy*max_fitness , : ); 
        
        
        Inaddr = cell(5, size(sensor_mapping, 1) ) ; 
        
        for j = 1:size(sensor_mapping, 1)
            
            Inaddr{1, j} = Outnode.OUT ; 
            Inaddr{2, j} = Commandnode.command ; 
            Inaddr{3, j} = [partial_mapping.IN, In_addr_left ] ;  % In_addr_left ; 
            Inaddr{4, j} = [partial_mapping.SENSOR , Sensor_left(sensor_mapping(j, :)) ] ; % Sensor_left(sensor_mapping(j, :)) ;
            % % if fitness >= greedy*max_fitness, we believe that it has the maximum fitness, but be smaller becaust of the intermitent observation  
            % Inaddr{5, j} = max_fitness ; 
            
            % % record the corresponding fitness 
            Inaddr{5, j} = fitness_selected(j, 1) ;  
        end
    else
        Inaddr = cell(5, 0 ) ; 
    end
% can be omitted 
    
else
    
    % length(In_addr_left) > length(Sensor_left) 
    % need select some input address to be 1 
    Inaddr = cell(5, 0 ) ; 
    
    In_addr_left_id = 1:length(In_addr_left) ; 
    
    if (length(In_addr_left_id) == 1 ) && (isempty(Sensor_left))
        combinations = nchoosek([1,2], 0) ;   % generate a 1*0 empty vector  
    else
        combinations = nchoosek(In_addr_left_id, length(Sensor_left));
    end
    
    
    
	% enumerate all state under the conbination, and calculate the fitness 
    for j = 1 : size(combinations, 1)
        
        
        In_addr_chosen = combinations(j, :) ; 
        % return the mapping of sensors, (including true) with maximum fitness  
        [Inaddrmapping] = addr_sensor_enumarate(In_addr_left, In_addr_chosen, Sensor_left, INPUTS, Outnode, Commandnode, data_raw, partial_mapping, redundant_id, threshold, greedy ) ; 
        
        % record comparison results under all In_address combination   
        Inaddr = [Inaddr, Inaddrmapping] ;
    end
    
    % find the largest fitness among all input address combinations   
    fitness_all = [Inaddr{5, :}] ;
    max_fitness = max( fitness_all ); 
    
    if max_fitness > threshold  % selected 0.95 
        Inaddr = Inaddr(:, fitness_all >= greedy*max_fitness ) ; 
    else
        Inaddr = cell(5, 0 );
    end
    
end


end






function [Inaddr] = addr_sensor_enumarate(In_addr_left, In_addr_chosen, Sensor_left, INPUTS, Outnode, Commandnode, data_raw, partial_mapping, redundant_id, threshold, greedy )  
    % the length of In_addr_left is larger than Sensor_left 
    
    INPUTS1 = INPUTS ; 
    % permutations = perms( 1: length(Sensor_left)) ; 
    
    
    
    permutations = perms( 1: length(Sensor_left)) ; 
    
    % remove some redundant sensor id permutation from permutations
    if ~isempty(intersect(Sensor_left, redundant_id))
        if length(intersect(Sensor_left, redundant_id)) > 1
            % remove the redundant sensor id permutation from permutations
            % first find the redundant sensor column.id in Sensor_left
            % and only keep one of the the permutation, in

            for redu_id = 1: size(redundant_id, 1)
                % redu_in_sen_pemu = zeros( size(permutations, 1), size(redundant_id ,2) ) ;
                for sen_per_row = 1: size(permutations, 1) 
                    [a, ~] = find( repmat(Sensor_left(permutations(sen_per_row, :))', 1, length(redundant_id(redu_id, :))) == repmat(redundant_id(redu_id, :), length( permutations(1, :) ), 1) ) ;

                    if ~isempty(a)
                        % redu_in_sen_pemu((redu_id-1)*size(permutations, 1)+sen_per_row , : ) =  a';
                        permutations(sen_per_row, sort(a)') = permutations(sen_per_row, a) ;
                    end
                end

            end

        end
    end
    permutations = unique(permutations, 'rows', 'stable') ;
    
    
    
    
    
    
    Inaddr = cell(5, 0 ) ; 
    
    for i = 1 : size(permutations, 1) 
        
        INPUTS = INPUTS1 ; 
        sensor_perm = Sensor_left( permutations(i, :) ) ; 
        % update INPUTS with sensor_perm 
        % the if-else is designed in case length(Sensor_left) == 0   
        %%%%%if ~isempty(sensor_perm)
        INPUTS(:, end - In_addr_left(In_addr_chosen) ) = data_raw(:, sensor_perm) ;  
        %%%%%end
        
        % update INPUTS by filling the "In_addr_unchosen" with trues  
        In_addr_left_id = 1:length(In_addr_left) ; 
        In_addr_unchosen = setdiff(In_addr_left_id, In_addr_chosen) ; 
        
        % fill In_addr_unchosen with 0,1,2,...,all True, enumerate all combination of true setting. 
        % totally 2^n filling strategies  
        Inaddrmapping = cell(5, 2^length(In_addr_unchosen) ) ; 
        map_update = 1 ;
        
        
        INPUTS2 = INPUTS ; 
        for True_num = 0 : length(In_addr_unchosen)
            % choose True_num address to be true. 
            
            if (length(In_addr_unchosen) == 1 ) && (True_num==0)
                True_address_strategies = nchoosek([1,2], 0) ;   % generate a 1*0 empty vector  
            else
                True_address_strategies = nchoosek(In_addr_unchosen, True_num );  % In_addr_unchosen is the id of In_addr_left  
            end
            
            
            True_vector = ones(size(data_raw , 1),  True_num, 'logical'); 
            
            for j = 1: size(True_address_strategies, 1) 
                % the chosen In_addr_left id , to be filled true. 
                INPUTS = INPUTS2 ; 
                
                True_address = True_address_strategies(j, : ) ; 
                INPUTS(:, end - In_addr_left(True_address) ) = True_vector ; 
                
                
                

                % add the initialzation 
                initialization = cell(2,1) ;
                initialization{1, 1} = data_raw(1, 1:25) ;
                initialization{2, 1} = data_raw(1, 26:46 ) ;

                % run alwsim given the INPUTS  
                OUTPUTS = IL_analyzer_CORE(INPUTS, initialization);
                output_estimate = OUTPUTS(:, end - Outnode.OUT) ; % from the bottom direction 

                output_expected = data_raw(:, Commandnode.command ) ; 
                mapping_fitness = Out2Com_Fit(output_expected, output_estimate) ; 
                
                
                % logs the input address and sensor permutation mapping, with its fitness  
                

                Inaddrmapping{1, map_update} = [Outnode.OUT ] ; 
                Inaddrmapping{2, map_update} = [Commandnode.command ] ; 
                % add partial_mapping.SENSOR
                Inaddrmapping{3, map_update} = [partial_mapping.IN, In_addr_left] ; 
                
                sensor_plan = ones(1, length(In_addr_left) ) * (size(data_raw, 2)-1) ; % (size(data_raw, 2)-1) represent False volumn
                
                % %%In_addr_chosen is position id in In_addr_left 
                % if ~isempty(sensor_perm)
                sensor_plan(In_addr_chosen) = sensor_perm ; 
                % end
                
                % True_address is position id in In_addr_left 
                sensor_plan(True_address) = ones(1, length(True_address) ) * size(data_raw, 2) ; % size(data_raw, 2) represent True volumn
                
                % add partial_mapping.SENSOR
                Inaddrmapping{4, map_update} = [partial_mapping.SENSOR, sensor_plan] ; 
                Inaddrmapping{5, map_update} = mapping_fitness ; 
                map_update = map_update + 1 ;
            end
        end
        % the same sensor_perm for the chosen In_addr in In_addr_left  
        % find the max fitness, and justify whether exist one input address, 
        
        fitness_all = [Inaddrmapping{5, :}] ; 
        max_fitness = max( fitness_all ) ;
        
        if max_fitness > threshold  % selected 0.95 
            Inaddr_sensorpermute = Inaddrmapping(:, fitness_all >= greedy*max_fitness ) ; 
                        
            if size(Inaddr_sensorpermute, 2) > 1
                % If yes, then ignore the address that can be assigned with false or true   
                
                % settle the sensor permutation answer  
                sensor_ans = reshape([Inaddr_sensorpermute{4, :}], length(partial_mapping.IN)+length(In_addr_left) , size(Inaddr_sensorpermute, 2) )' ; 
                
                % given the "In_addr_unchosen" that obtained in previous process, which stays unchanged  
                % justify the unchosen bit in "In_addr_unchosen" whether should assignment   
                
                
                bits_ignore = [] ; 
                for bitig = length(partial_mapping.IN)+In_addr_unchosen %  length(In_addr_chosen)+1: length(In_addr_left)
                    
                    % whether all assignment belong to FALSE;   
                    if sum(sensor_ans(:, bitig) == (size(data_raw, 2)-1)) == size(Inaddr_sensorpermute, 2) 
                        continue ; 
                    % whether all assignment belong to TRUE; 
                    elseif sum(sensor_ans(:, bitig) == size(data_raw, 2) ) == size(Inaddr_sensorpermute, 2) 
                        continue ; 
                    else
                        % records the bits (positions) that should be ignored 
                        bits_ignore = [bits_ignore, bitig] ; 
                    end
                end
                % delete bits_ignore from or Inaddr_sensorpermute  
                for ans_sensor = 1: size(Inaddr_sensorpermute, 2)
                    Inaddr_sensorpermute{3, ans_sensor}(bits_ignore) = []; 
                    Inaddr_sensorpermute{4, ans_sensor}(bits_ignore) = []; 
                end
            end
            
        else
            Inaddr_sensorpermute = cell(5, 0 ) ; 
        end
        
        % logs the sensor permutation solutions, under the condition: sensor_perm = Sensor_left( permutations(i, :) ) ;   
        Inaddr = [Inaddr, Inaddr_sensorpermute] ;
    end
    
    % find the best fitness answer in Inaddr, i.e., all sensors'
    % permutation   
    fitness_all = [Inaddr{5, :}] ;
    max_fitness = max( fitness_all ); 
    
    if max_fitness > threshold  % selected 0.95 
        Inaddr = Inaddr(:, fitness_all >= greedy*max_fitness ) ; 
    else
        Inaddr = cell(5, 0 );
    end
    
    % return Inaddr, which has the best fitness input address filling, 
    % under the pair of Outaddr_pair and Comdata 
    
end






