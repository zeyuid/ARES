function [fitness] = Out2Com_Fit(output_expected, output_predict) 



try 
output_predict = double(output_predict) ; 
output_expected = double(output_expected) ;
output_predict(1, :) = [];
output_expected(1, :) = [];
% if class(output_expected) == "uint8"
%     output_predict = uint8(output_predict) ; 
% end


output_estimate = output_predict ;

%%%%% estimation: only keep the incremental output predict information, induced by sensors   
% output_estimate(2:end, :) = output_predict(2:end, :) - output_predict(1:end-1, : ) + output_expected(1:end-1, :) ; 


% %%%%% using transition as fitness comparison
% [trigger_exp, ~, ~, ~, ~] = triggering_detection( output_expected(2:end, :), 1:size(output_expected, 2) ) ;
% [trigger_est, ~, ~, ~, ~] = triggering_detection( output_estimate(2:end, :), 1:size(output_estimate, 2) ) ;
% 
% fitness = zeros(1, size(output_estimate, 2) ) ; 
% 
% for i = 1: size(trigger_est , 2)
%     
%     timed_est = trigger_est(:, i) ; 
%     timed_exp = trigger_exp(:, i) ; 
%     
%     fitness(1, i) = length(setdiff( intersect(timed_est, timed_exp ) , 0 )) / length(setdiff( union(timed_est, timed_exp ) , 0 )) ;  
%     fitness(isnan(fitness)) = 0 ;
% end


% % using static as fitness comparison
fitness = zeros(1, size(output_estimate, 2) ) ; 
for i = 1: size(output_estimate , 2)
    M = corrcoef(output_estimate, output_expected) ; 
    fitness(1, i) = M(1,2)/(sum( abs(output_expected(:, i) - output_estimate(:, i)))/ length(output_expected(:, i))) ;
%     fitness(1, i) = (sum( (output_expected(:, i) == output_estimate(:, i)))/ length(output_expected(:, i))) ;
end

fitness(isnan(fitness)) = 0;

plot(output_estimate)
hold on
plot(output_expected)
hold off

catch
   
   savepath  = strcat('dimensionNOTmatch-', datestr(now,'HH-MM-SS')) ;
   save(savepath) ; 
   
   quit 
end



end



