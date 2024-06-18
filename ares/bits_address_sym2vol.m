function G_code = bits_address_sym2vol(G_code)


% need to know: the volumn of Q_(range) of each command function, to monitor the output estimation 
% need to know: the volumns of I_(range) of each sensor, to feed the input  


% first get the length of Q_range
Q_expression = 'Q(?<byte>\d+)_(?<bit>\d+)' ; 
for i = 1:size(G_code, 2)
    output_symbols = G_code{1, i} ;  
    address = regexp(output_symbols, Q_expression, 'names', 'ignorecase') ; 
    
    vol = str2double(address.byte) * 8 + str2double(address.bit) ;  % from the bottom direction 
    G_code{3, i} = vol; % "+1" is adapted for python
end
% find the maximum vol, to fix the length of Q address: ceil(vol/8)*8 
output_length = ceil( (max([G_code{3, :}])+1) /8 ) * 8 ;


% first get the length of I_range, the largest byte and bit. 
I_expression = 'I(?<byte>\d+)[_\.](?<bit>\d+)' ; 
for i = 1:size(G_code, 2)
    input_symbols = G_code{2, i} ; 
    
    update = 1;
    for j = 1:length(input_symbols)
        address = regexp(input_symbols{j}, I_expression, 'names', 'ignorecase') ; 
        vol = str2double(address.byte) * 8 + str2double(address.bit) ;  % from the bottom direction, from the top direction = end-vol 
        
        G_code{4, i}(update) = vol ; % "+1" is adapted for python 
        update = update + 1;
    end
        
end
% find the maximum vol, to fix the length of I address: ceil(vol/8)*8 
input_length = ceil( (max([G_code{4, :}])+1) /8 ) *8 ;


end



