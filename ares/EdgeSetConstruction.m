function [E_s_u, G_control] = EdgeSetConstruction(data_raw, sensor_id, command_id, command_delayed_set_cell, redundant_id,info_delta_min,occupation_min, transferdelay, autocorrelation, tau )  

% reshape the node sets 
command_timer = reshape([command_delayed_set_cell{:, 1}], size(command_delayed_set_cell{1,1})) ; 
sensor_timer = reshape([command_delayed_set_cell{1, 2}{:,:}], size(command_delayed_set_cell{1,2})) ; 
delays = reshape([command_delayed_set_cell{:, 3}], size(command_delayed_set_cell{1,3})) ; 
directions = reshape([command_delayed_set_cell{:, 4}], size(command_delayed_set_cell{1,4})) ; 


command_delayed_set(:, 1) = command_timer(:, 1) ; 
command_delayed_set(:, 2) = sensor_timer(:, 1);
command_delayed_set(:, 3) = delays(:, 1);
command_delayed_set(:, 4) = directions(:, 1);

%%%%% construct edges from sensor node to command node, and build the weighted directed graph
[E_s_u, ~] = edgesearching(data_raw, sensor_id, command_id, command_delayed_set, redundant_id, transferdelay, autocorrelation, tau, info_delta_min, occupation_min );

% transfer to graph and show
G_control = graph_generation(sensor_id, command_id, E_s_u, 1);
end


