function G_code = byte_address_sym2vol(G_code)


% need to know: the volumn of Q_(range) of each command function, to monitor the output estimation 
% need to know: the volumns of I_(range) of each sensor, to feed the input  

% first sort the Q output
G_code = sortrows(G_code', 1)' ; 

for i = 1:size(G_code, 2)
    G_code{3, i} = i; 
end

% then sort the list the position of I in all input variables  
all_input_addrsymbo = sort(unique([G_code{2, :}])) ; 

for i = 1:size(G_code, 2)
    input_symbols = G_code{2, i} ; 
    for j = 1:length(input_symbols)
        vol = find(strcmp(all_input_addrsymbo, input_symbols(j) )) ; 
        
        G_code{4, i}(j) = vol ; 
    end
end

end



