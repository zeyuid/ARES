function [mapping_cyclic_num, Mapping_solution_num, input_unique_ratio, in_right_ratio, output_unique_ratio, out_right_ratio] = GRAPH_MAPING_CENTOR(identify_length, occupation_min, info_delta_min, transferdelay, autocorrelation, tau, mapping_data_period, mapping_threshold, mapping_greedy, mapping_data_start, trainning_data_path, savefilepath ) 
% inputs: identify_length, occupation_min, info_delta_min, transferdelay, autocorrelation, tau, mapping_data_length, mapping_threshold, mapping_greedy ) ;
% outputs: Mapping_solution_num, input_unique_ratio, in_right_ratio, output_unique_ratio, out_right_ratio

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%     Part I     %%%%%%%%%%%
%%%%%%%%%%% Astract G_code %%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%% obtaining the G_code %%%%%%%
%%%%%%%%% "cd ../STL_sparser"
%%%%%%%%% running "python -m core.main"

IOmap_path = "./normal_elevator_pro_IO.json" ;
G_code = Get_G_code(IOmap_path) ;
for i = 1:size(G_code, 2)
    G_code{5, i} = length(G_code{2,i}) ;
end
G_code = sortrows(G_code',5)';
input_num = length(setdiff([G_code{4, :}], 0)) ; 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%    Part II      %%%%%%%%%%
%%%%%%%%%%% Astract G_data %%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%% Parameters setting of EdgeSetConstruction
%%%%%%%%%%%%%%%%%%%%                      %%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%                      %%%%%%%%%%%%%%%%%%%%
%%%%%%%%% load the trainning data  
load(trainning_data_path); 
savefilepath = erase(savefilepath, "/mapping_results") ; 

if ~exist(savefilepath, 'dir')
    mkdir( savefilepath );
end
graphspath = sprintf(savefilepath + "/Graphs_length%d_occup%d_info_%d.mat", identify_length, occupation_min, info_delta_min) ;

if ~exist(graphspath, 'file')
    % Identify sensor/command set from the data_raw
    threshold = 0.1;
    [sensor_set, command_set, command_delayed_set, ~, ~, ~, redundant_id, constant_id] = node_classification(data_raw, threshold, input_num);
        
    % Abstracting Edges from data_raw, given the classfied sensor/command nodes sets
    [G_data, ~] = EdgeSetConstruction(data_raw(1:identify_length, :), sensor_set, command_set, command_delayed_set, redundant_id, info_delta_min,occupation_min, transferdelay, autocorrelation, tau) ;
    redundant_id = sortrows(redundant_id', 1)' ;
    save(graphspath, "G_code", "G_data", "data_raw", "sensor_set", "command_set", "redundant_id", "constant_id" ) ;
else
    load(graphspath)
end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%    Part III     %%%%%%%%%%
%%%%%%%%% Map G_code G_data %%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%% Parameters setting of EdgeSetConstruction
%%%%%%%%%%%%%%%%%%%%                      %%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%                      %%%%%%%%%%%%%%%%%%%%
%%%%%%%% data length:
%%%%%%%% solution selcetion threshold, which doesn't affect the mapping results, but save the storing space when mapping
%%%%%%%% greedy, if set as 1, then totally greedy

data_mapping = data_raw( mapping_data_period, :) ; 
tic ;
[Mappings, mapping_cyclic_num, mappings_files_path] = Graph_mapping(G_code, G_data, data_mapping, redundant_id, constant_id, mapping_threshold, mapping_greedy, savefilepath , mapping_data_start) ;
toc ;

fid = fopen(mappings_files_path+'cyclic_number_logs.txt', 'a') ;
cycle_time_sym = sprintf("!!! the total Execution time is %d seconds !!!", toc)
fprintf(fid, "\n" ) ;
fprintf(fid, cycle_time_sym );
fclose(fid);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%    Part IV      %%%%%%%%%%
%%%%%%%%%% Analyse Mappings %%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%% for the finial solution compare 
[Mapping_solution_num, input_unique_ratio, in_right_ratio, output_unique_ratio, out_right_ratio] = mapping_analysis(Mappings) ; 










