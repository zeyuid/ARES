function [E_s_u, G_control] = EdgeSetConstruction(data_raw, sensor_id, command_id, command_delayed_set_cell, redundant_id,info_delta_min,occupation_min, transferdelay, autocorrelation, tau )  



command_timer = reshape([command_delayed_set_cell{:, 1}], size(command_delayed_set_cell{1,1})) ; 
sensor_timer = reshape([command_delayed_set_cell{1, 2}{:,:}], size(command_delayed_set_cell{1,2})) ; 
delays = reshape([command_delayed_set_cell{:, 3}], size(command_delayed_set_cell{1,3})) ; 
directions = reshape([command_delayed_set_cell{:, 4}], size(command_delayed_set_cell{1,4})) ; 

% command_delayed_set = [];
% command_delayed_set(1, 1) = 34; command_delayed_set(1, 2) = 13; command_delayed_set(1, 3) = 6; command_delayed_set(1, 4) = 1;

command_delayed_set(:, 1) = command_timer(:, 1) ; 
command_delayed_set(:, 2) = sensor_timer(:, 1);
command_delayed_set(:, 3) = delays(:, 1);
command_delayed_set(:, 4) = directions(:, 1);
% % construct edges in controller, i.e., from sensor to command
% transferdelay = 0; autocorrelation = 1; tau = 1; 

% search command responsed for rising edges
% [E_s_u_rising, W_s_u_rising] = edgesearching(data_raw, sensor_id, command_id, command_delayed_set, redundant_id, transferdelay, autocorrelation, tau, info_delta_min, occupation_min, []);
% % search command responsed for falling edges
% [E_s_u_falling, W_s_u_falling] = edgesearching(data_raw, sensor_id, command_id, command_delayed_set, redundant_id, transferdelay, autocorrelation, tau, info_delta_min, occupation_min, []);

% weighted directed graph
[E_s_u, W_s_u] = edgesearching(data_raw, sensor_id, command_id, command_delayed_set, redundant_id, transferdelay, autocorrelation, tau, info_delta_min, occupation_min, []);

% E_s_u = {};
% for j = 1:size(E_s_u_rising, 2)
%     E_s_u{1, j} = E_s_u_rising{1, j};
%     E_s_u{2, j} = union( E_s_u_rising{2, j},  E_s_u_falling{2, j} ) ;
%     ave_weights = [];
%     for m = 1:length(E_s_u{2, j})
%         factor = E_s_u{2, j}(m) ;
%         posit_rising = find(E_s_u_rising{2, j} == factor) ;
%         posit_falling = find(E_s_u_falling{2, j} == factor) ;
%         
%         weight = 0 ;
%         if posit_rising
%             weight = weight + E_s_u_rising{3, j}(posit_rising);
%             if posit_falling
%                 weight = weight + E_s_u_falling{3, j}(posit_falling) ; 
%                 ave_weights(m) = weight/2; 
%             end
%         end
%         if posit_falling
%             weight = weight + E_s_u_falling{3, j}(posit_falling) ; 
%         end
%         ave_weights(m) = weight;
%     end
%     
%     E_s_u{3, j} = ave_weights ; 
%     % E_s_u{3, j} = ones(length(E_s_u{2, j}), 1) ; set weights as one
% end

% tranlate to graph
G_control = graph_generation(sensor_id, command_id, E_s_u, 1);




end
% % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % 
% % % 
% % % % construct edges for physical invariants, i.e., from command to sensor
% % % % two challenges: 1. Uniformization of trigger delay; 
% % % 
% % % % search for sensors, purely decided by control command 
% % % [dependent_sensors, delays_falling_edge, delays_rising_edge] = dependent_sensors_search(command_id, sensor_id, trigger_time, UP_Pos, DOWN_Pos);
% % % 
% % % % data prepare: 1. Uniformization of trigger delay
% % % [Data_prime, UP_Pos_prime, DOWN_Pos_prime] = data_delay_uniformization( UP_Pos, DOWN_Pos, data_raw, dependent_sensors, sensor_id, delays_rising_edge, delays_falling_edge);
% % % 
% % % % % % % edges match: 2. different delays k for matching : add direction of edges for searching
% % % 
% % % 
% % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % 
% % % 
% % % % search command responsed for rising edges
% % % transferdelay = [ delays_rising_edge{3, dependent_sensors } ]; autocorrelation = 1;  tau = 1;
% % % [E_u_s_rising, W_u_s_rising] = edgesearching(Data_prime, command_id(1:end,:), sensor_id(dependent_sensors, :), redundant_id, transferdelay, autocorrelation, tau, info_delta_min, occupation_min, [1, 0]);
% % % 
% % % 
% % % % search command responsed for falling edges
% % % transferdelay = [ delays_falling_edge{3, dependent_sensors } ]; autocorrelation = 1; tau = 1;
% % % [E_u_s_falling, W_u_s_falling] = edgesearching(Data_prime, command_id, sensor_id(dependent_sensors, :), redundant_id, transferdelay, autocorrelation, tau, info_delta_min, occupation_min, [0, 1]);
% % % 
% % % 
% % % 
% % % % weighted directed graph
% % % E_u_s = {};
% % % for j = 1:size(E_u_s_rising, 2)
% % %     E_u_s{1, j} = E_u_s_rising{1, j};
% % %     E_u_s{2, j} = union( E_u_s_rising{2, j},  E_u_s_falling{2, j} ) ;
% % %     
% % %     ave_weights = [];
% % %     for m = 1:length(E_u_s{2, j})
% % %         factor = E_u_s{2, j}(m) ;
% % %         posit_rising = find(E_u_s_rising{2, j} == factor) ;
% % %         posit_falling = find(E_u_s_falling{2, j} == factor) ;
% % %         
% % %         weight = 0 ;
% % %         if posit_rising
% % %             weight = weight + E_u_s_rising{3, j}(posit_rising);
% % %         elseif posit_falling
% % %             weight = weight + E_u_s_falling{3, j}(posit_falling) ; 
% % %         end
% % %         ave_weights(m) = weight/2;
% % %     end
% % %     
% % %     E_u_s{3, j} = ave_weights ;     
% % %     % E_u_s{3, j} = ones(length(E_u_s{2, j}), 1) ; % set weights as one
% % % end
% % % 
% % % % tranlate to graph
% % % G_physics = graph_generation(sensor_id, command_id, E_u_s, 0);


