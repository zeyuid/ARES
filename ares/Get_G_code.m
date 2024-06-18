function G_code = Get_G_code(IOmap_path)
% raw 1: the output register address, i.e., Q1_1
% raw 2: the correlated input register address, i.e., {I1.1, I1.2}

text = fileread(IOmap_path) ;
IO_map = jsondecode(text) ;
Out_addr = fieldnames(IO_map) ;

G_code = cell(2, length(Out_addr));
G_code(1, :) = Out_addr;

for i = 1:length(Out_addr)
    G_code{2, i} = getfield(IO_map, Out_addr{i})';
end

if IOmap_path == "./normal_elevator_pro_IO.json" || IOmap_path =="./2_floor_elevator_IO.json"
    % if discreate, arrange the code variable in the way of Input bits
    G_code = bits_address_sym2vol(G_code) ;
else
    % if continious, arrange the code variable in the way of symbol sorting   
    G_code = byte_address_sym2vol(G_code) ;
end
% raw 3: the volumn distance of output register address, from the end of PLC output, i.e., 9
% raw 4: the volumn distance of input register address, from the end of PLC input vector, i.e., [9, 10] 

end

