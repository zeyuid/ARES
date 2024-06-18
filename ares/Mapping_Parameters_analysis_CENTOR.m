clear

trainning_data_path = './data_withoutattack/elevator_data20201110.mat' ; 
data_version = '\d*';

trainning_data_version = regexp(trainning_data_path, data_version, 'match') ;
trainning_data_version=trainning_data_version{1};


mapping_greedy_list = [1] ;
mapping_data_length_list = [7000] ; 
repeat_times = 1 ;

greedy_impact_total = cell(1, length(mapping_greedy_list)) ;

for k = 1: length(mapping_greedy_list)
    % if set as 1, then totally greedy
    mapping_greedy = mapping_greedy_list(k) ;
    
    length_impact_total = cell(1, length(mapping_data_length_list)) ;
    length_impact = cell(7, repeat_times) ;
    for i = 1 : length(mapping_data_length_list)
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        %%%%%%%%%%%    Part I      %%%%%%%%%%%
        %%%%%%%%% G_data parameters %%%%%%%%%%
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        identify_length = 7000 ; 
        occupation_min = 1;  % the end occupation
        info_delta_min = 0.1 ;  % the end information delta
        
        transferdelay = 0; % delay from sensor to command
        autocorrelation = 1;  % delay from history command and current command
        tau = 1; % sample length of correlation, tau+1 samples is a sample, sequence

        savefilepath = sprintf("./data/Graphs/Graphs_length%d_occup%d_info_%d/mapping_results", identify_length, occupation_min, info_delta_min) ;
        if ~exist(savefilepath, 'dir')
            mkdir(savefilepath ) ;
        end
        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        %%%%%%%%%%%    Part II      %%%%%%%%%%
        %%%%%%%%% Mapping parameters   %%%%%%%
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        mapping_data_length = mapping_data_length_list(1, i) ;
        selection_end = identify_length - mapping_data_length ;
        mapping_data_start_list = randi( [1 selection_end+1], 1, repeat_times ) ;
        mapping_data_start_list(1) = 1;
        
        mapping_threshold = 0.95 ;
        
        for j = 1 : repeat_times
            
            mapping_data_start = mapping_data_start_list(j) ;
            mapping_data_period = mapping_data_start : mapping_data_start + mapping_data_length - 1 ;
            % for each parameter, do the "GRAPH_MAPING_CENTOR", and log the analysis results
            % cyclic_num: a number; Mapping_solution_num: number; input_unique_ratio: number; in_right_ratio: number; output_unique_ratio: number; out_right_ratio: number
            [cyclic_num, Mapping_solution_num, input_unique_ratio, input_right_ratio, output_unique_ratio, output_right_ratio] = GRAPH_MAPING_CENTOR(identify_length, occupation_min, info_delta_min, transferdelay, autocorrelation, tau, mapping_data_period, mapping_threshold, mapping_greedy, mapping_data_start, trainning_data_path, savefilepath ) ;
            
            length_impact{1, j} = mapping_data_length_list(i) ;
            length_impact{2, j} = cyclic_num ; 
            length_impact{3, j} = Mapping_solution_num ;
            length_impact{4, j} = input_unique_ratio ;
            length_impact{5, j} = input_right_ratio ;
            length_impact{6, j} = output_unique_ratio ;
            length_impact{7, j} = output_right_ratio ;
        end
        length_impact_total{1, i} = length_impact ;
    end
    
    savefilepath_length = sprintf("./data/Graphs/Graphs_length%d_occup%d_info_%d/mapping_results/greedy_%d/mapping_length", identify_length, occupation_min, info_delta_min, mapping_greedy) ;
    if ~exist(savefilepath_length, 'dir')
        mkdir(savefilepath_length ) ;
    end
    save(savefilepath_length + "/length_impact" , "length_impact_total") ;
    
    fid = fopen(savefilepath_length + '/length_parameters_logs.txt', 'a') ;
    fprintf(fid, "the analyzed impact are collected as rows: mapping_data_length_list, cyclic_num_list, Mapping_solution_num_list, input_unique_ratio_list, input_right_ratio_list, output_unique_ratio_list , output_right_ratio_list " ) ;
    parameters_logs = sprintf("!!! The evaluated lenght parameters are %d !!!\n", mapping_data_length_list ) ; 
    fprintf(fid, "\n" ) ;
    fprintf(fid, parameters_logs );
    fclose(fid);
    
    greedy_impact_total{1, k} = length_impact_total ;
end


savefilepath_greedy = sprintf("./data/Graphs/Graphs_length%d_occup%d_info_%d/mapping_results", identify_length, occupation_min, info_delta_min ) ;
if ~exist(savefilepath_greedy, 'dir')
    mkdir(savefilepath_greedy ) ;
end
save(savefilepath_greedy + "/greedy_impact" , "greedy_impact_total") ;



fid = fopen(savefilepath_greedy + '/greedy_parameters_logs.txt', 'a') ;
fprintf(fid, "the analyzed impact are collected as rows: mapping_greedy_list  " ) ;
parameters_logs = sprintf("!!! The evaluated greedy parameters are %d !!!\n", mapping_greedy_list ) ; 
fprintf(fid, "\n" ) ;
fprintf(fid, parameters_logs );
fclose(fid);







