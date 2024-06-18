function [fitness] = Out2Com_Fit(output_expected, output_predict) 

try 
output_predict = double(output_predict) ; 
output_expected = double(output_expected) ;
output_predict(1, :) = [];
output_expected(1, :) = [];


output_estimate = output_predict ;


fitness = zeros(1, size(output_estimate, 2) ) ; 
for i = 1: size(output_estimate , 2)
    fitness(1, i) = (sum( (output_expected(:, i) == output_estimate(:, i)))/ length(output_expected(:, i))) ;
end

fitness(isnan(fitness)) = 0;

catch
   savepath  = strcat('dimensionNOTmatch-', datestr(now,'HH-MM-SS')) ;
   save(savepath) ; 
   
   quit 
end


end



