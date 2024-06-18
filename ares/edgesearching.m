function [E_x_y, W_x_y] = edgesearching(data_raw, X_id, Y_id, command_delayed_set, sensor_redundant_id, transferdelay, autocorrelation, tau, info_delta_min, occupation_min, direction)

num_Y = size(Y_id, 1);

% X_id_keep = X_id;
% X_id = [Y_id ; X_id];
% num_X = size(X_id, 1);
num_X = size(X_id, 1); 

E_x_y = cell(3, num_Y);
W_x_y = zeros(num_X, num_Y );
TE_x_y = zeros(num_X, num_Y );

% search causal Xs for Y
% X' majority are equals, during the mapping.

if length(transferdelay) == 1
    transferdelay = transferdelay*ones(length(Y_id), 1 );
end
if length(autocorrelation) == 1
    autocorrelation = autocorrelation*ones(length(Y_id), 1 );
end
if length(tau) == 1
    tau = tau*ones(length(Y_id), 1 );
end



for i = 1 : num_Y
%     tic;
    
    neighbors = [];
    weights = [];
    info_delta = 1 ;
    occupation = 0 ;
    exclude_neighbors = [];
    Y_sample = Y_id(i, 1);
    
    data = data_raw;
    %%%%%%%% padding the corresponding sensors in raw data, if Y_sample is a timer related command   
    if ~isempty(find(command_delayed_set(:,1) == Y_sample))
        row = find(command_delayed_set(:,1) == Y_sample) ;
        for r = row
            delayed_sen = command_delayed_set(r, end-2) ;
            delayed_sensor = X_id(delayed_sen , 1) ; 
            
            if command_delayed_set(r, end) == 1
                [~, ~, correled_pos, ~, ~] = triggering_detection( data(:, Y_sample), 1 ) ;
            else
                [~, ~, ~, correled_pos, ~] = triggering_detection( data(:, Y_sample), 1 ) ;
            end
            [trigger_time, persistent_time, UP_Pos, DOWN_Pos, DE_X] = triggering_detection( data(:, delayed_sensor), 1 ) ;
            
            if length(intersect(correled_pos - command_delayed_set(r, end-1), UP_Pos)) > length(intersect(correled_pos - command_delayed_set(r, end-1), DOWN_Pos))
                % means the rising edges of sensor is correlated 
                for delay  = 0: command_delayed_set(r, end-1) -1
                    data(UP_Pos+delay, delayed_sensor) = data(UP_Pos-1 , delayed_sensor);
                end
            else
                % means the falling edges of sensor is correlated 
                for delay  = 0: command_delayed_set(r, end-1) -1
                    data(DOWN_Pos+delay, delayed_sensor) = data(DOWN_Pos-1 , delayed_sensor);
                end
            end
        end
        
    end
    
    
    % calculate the whole information of the command, considering the direction
%     [~, H_y] = TransferEntropy(data(:, X_id(:, 1)), data(:, Y_sample ), data(:, [] ), transferdelay(i), autocorrelation(i), tau(i), direction) ;
    
    
    % calculate weight when all sensor are used, the distribution of sensor, using TE  
    all_other_vars = setdiff(X_id(:, 1), Y_sample) ;
    [whole_corr_info,~,whole_mutual_info] = TransferEntropy(data(:, all_other_vars ), data(:, Y_sample ), data(:, [] ), transferdelay(i), autocorrelation(i), tau(i), direction) ;
    
%     [test] = TransferEntropy(data(:, X_id(:, 1)), data(:, Y_sample ), data(:, [] ), 0, 1, 0,[]) ;
    
    % 
    % any unsatisfied condition will exit the loop
    while occupation < occupation_min  % && info_delta > info_delta_min 
        
        for j = 1:num_X
            if isempty(find(exclude_neighbors == X_id(j, 1)))
                TE_x_y(j , i) = TransferEntropy(data(:, X_id(j, 1)), data(:, Y_sample ), data(:, neighbors ), transferdelay(i), autocorrelation(i), tau(i), direction) ;
                W_x_y(j , i) = TE_x_y(j , i)/whole_corr_info;
            else
                TE_x_y(j , i) = 0;
                W_x_y(j , i) = 0;
            end
            
        end
        % map node with maximum weight to target command node command_id(i, 1)
        info_delta = max(W_x_y(: , i));
        
        if info_delta > info_delta_min
            neighbor = X_id (find(W_x_y(:, i) ==  info_delta ), 1 );
            
            % if the neighbor has redundant node, add them together to neighbors set
            neighborprimes = [];
            for k = 1:length(neighbor)
                
                neighborprime = neighbor(k);
                if isempty(find([neighbors, neighborprimes] == neighborprime )) 
                    if ~isempty(find( sensor_redundant_id == neighborprime ))
                        
                        [row, col] = find( sensor_redundant_id == neighborprime ) ;
                        neighborprime = setdiff(sensor_redundant_id ( row, : ), 0 );  % all redundant nodes with neighbor
                        
                    end
                    neighborprimes = [neighborprimes, neighborprime];
                end
            end
            neighbors = [neighbors, neighborprimes];
            
            % update the weight when given other neighbors
            while length(neighbors) ~= length(weights)
                [neighbors, weights, exclude_neighbor] = weights_update(data, neighbors, sensor_redundant_id, Y_sample, whole_corr_info,info_delta_min, transferdelay(i), autocorrelation(i), tau(i), direction );
                if ~isempty(find(neighbors==0))
                
                    if isempty(find(neighbors~=0))
                        neighbors = neighborprimes;
                    else
                        exclude_neighbors = [exclude_neighbors, exclude_neighbor];
                        weights = weights(neighbors~=0);
                        neighbors = neighbors(neighbors~=0);
                    end
                end
            end
            
            
            [~,~,occupation_raw] = TransferEntropy(data(:, neighbors ), data(:, Y_sample ), data(:, [] ), transferdelay(i), autocorrelation(i), tau(i), direction) ;
            occupation = occupation_raw/whole_mutual_info;
            
        else
            break
        end
    end
    
    
    E_x_y{1, i} = Y_sample;
    E_x_y{2, i} = neighbors;
    E_x_y{3, i} = weights;
    E_x_y{4, i} = occupation * whole_mutual_info ; % the proportion of info. the chosen sensors have, comparing with the all sensors have. under the autocorrelation(i) condition  
    E_x_y{5, i} = length(neighbors);
    
    % % information that all sensors and one-delayed commands can provide 
    % E_x_y{5, i} = whole_mutual_info ; % the proportion that, info. theory has, 1 autocorrelation    
    
end
% sort E_x_y as the node degree increase 
E_x_y = sortrows(E_x_y',5)' ;

end


function [neighbors, weights, exclude_neighbors] = weights_update(data, neighbors, sensor_redundant_id, Y_sample, whole_info, info_delta_min, transferdelay, autocorrelation, tau, direction )
% update the weight when given other neighbors
for jj = 1:length(neighbors)
    noncoorelated_neighbots = [];
    
    if ~isempty(find( sensor_redundant_id == neighbors(jj) ))
        [row, col] = find( sensor_redundant_id == neighbors(jj) ) ;
        noncoorelated_neighbots = setdiff( neighbors , sensor_redundant_id (row,:) );  % all neighbors without neighbors(jj) and its redundant nodes
        redundant_neighbors = sensor_redundant_id (row,:);
        TE_s_u_prime = [];
        for jjj = 1: length(redundant_neighbors)
            TE_s_u_prime(jjj) = TransferEntropy(data(:, redundant_neighbors(jjj) ), data(:, Y_sample ), data(:, noncoorelated_neighbots ),  transferdelay, autocorrelation, tau, direction) ;
        end
        TE_x_y = max(TE_s_u_prime) ;
    else
        noncoorelated_neighbots = setdiff( neighbors , neighbors(jj) );
        TE_x_y = TransferEntropy(data(:, neighbors(jj) ), data(:, Y_sample ), data(:, noncoorelated_neighbots ),  transferdelay, autocorrelation, tau, direction) ;
    end
    weights(jj) = TE_x_y / whole_info;
end

% info_delta_min = 0.02;
exclude_neighbors = neighbors( weights < info_delta_min );
neighbors(weights < info_delta_min) = 0;

end
