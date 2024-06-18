function [Mapping_solution_num, input_unique_ratio, in_right_ratio_unique, output_unique_ratio, out_right_ratio_unique, in_right_ratio_part, in_right_ratio_total, out_right_ratio_part, out_right_ratio_total] = mapping_analysis(Mappings) 

%%%%% Analyse mapping solutions number
Mapping_solution_num = size(Mappings, 2) ;


%%%%% Analyse unique/right mapping solutions raito
ground_outputs_mapping = [26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46] ;
ground_inputs_mapping  = [1,2,3,4,5,6,7,8,9,10,11,12,48,48,15,16,47,18,19,20,21,22,23,24,25] ;

all_outputs_permutations = reshape([Mappings{1, :}],  length(Mappings{1, 1}), size(Mappings, 2) )' ;
all_inputs_permutations = reshape([Mappings{3, :}],  length(Mappings{3, 1}), size(Mappings, 2) )' ;
all_commands_permutations = reshape([Mappings{2, :}],  length(Mappings{2, 1}), size(Mappings, 2) )' ;
all_sensors_permutations = reshape([Mappings{4, :}],  length(Mappings{4, 1}), size(Mappings, 2) )' ;

outputs_mapping = sortrows([unique(all_outputs_permutations, 'rows', 'stable'); unique(all_commands_permutations, 'rows', 'stable')]', 1)' ;
inputs_mapping = sortrows([unique(all_inputs_permutations, 'rows', 'stable'); unique(all_sensors_permutations, 'rows', 'stable')]', 1)' ;

%%%%% Analyse command unique
Unique_output_num = 0 ;
Unique_output_posi = zeros(1, 0) ;
for com_solu = 1:size(outputs_mapping, 2)
    solu_outputs = unique(outputs_mapping(2:end, com_solu), 'rows', 'stable') ;
    if length(solu_outputs) == 1
        Unique_output_num = Unique_output_num + 1;
        Unique_output_posi = [Unique_output_posi, com_solu] ;
    end
end
output_unique_ratio = Unique_output_num/size(outputs_mapping, 2);


%%%%% Analyse sensor unique
Unique_input_num = 0 ;
Unique_input_posi = zeros(1, 0) ;
for sen_solu = 1:size(inputs_mapping, 2)
    solu_inputs = unique(inputs_mapping(2:end, sen_solu), 'rows', 'stable') ;
    if length(solu_inputs) == 1
        Unique_input_num = Unique_input_num + 1;
        Unique_input_posi = [Unique_input_posi, sen_solu] ;
    end
end
input_unique_ratio = Unique_input_num/size(inputs_mapping, 2) ;


%%%%% Analyse the right mapping accuracy
if output_unique_ratio ~=0
    out_right = sum(outputs_mapping(2, Unique_output_posi) == ground_outputs_mapping(1, Unique_output_posi)) ; 
    out_right_ratio_unique = out_right / Unique_output_num ;
    out_right_ratio_part = out_right / size(outputs_mapping, 2);
    out_right_ratio_total = out_right / length(ground_outputs_mapping) ; 
else
    out_right_ratio_unique = 0 ;
    out_right_ratio_part = 0 ;
    out_right_ratio_total = 0 ;
end

if input_unique_ratio~=0
    in_right = sum(inputs_mapping(2, Unique_input_posi) == ground_inputs_mapping(1, Unique_input_posi)) ; 
    in_right_ratio_unique  = in_right / Unique_input_num ;
    in_right_ratio_part = in_right / size(inputs_mapping, 2) ;
    in_right_ratio_total = in_right / length(ground_inputs_mapping) ; 
else
    in_right_ratio_unique = 0 ;
    in_right_ratio_part = 0 ; 
    in_right_ratio_total = 0 ;
end



