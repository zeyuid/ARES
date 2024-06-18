function [sensor_set, command_set, command_delayed_set, trigger_time, UP_Pos, DOWN_Pos, redundant_id, constant_id, laggings, laggings_UEntropy] = node_classification(data_raw, timer_command_threshold)

% % % % % node classification for constants, variants, and reduntants % % % % %
% if variable is constant, remove them from the analysising list.
% if variables are closely correlated, union them and removing the left
% from the analysising list.

fprintf("start node classification {sensors, commands}. \n")
tic ;

variable_id = [];
constant_id = [];
redundant_id = [];


data = data_raw;
corr=[];

redundant_threshold = 0.9;
for i = 1:size(data,2)
    if Entropy( data_raw(:, i) ) == 0
        constant_id = [constant_id; i];
    else
        variable_id = [variable_id; i];
        
        for j = 1:size(data,2)
            MM = corrcoef(im2double(data_raw(:, i)), im2double(data_raw(:, j))) ;
            corr(j, i) = MM(1, 2) ;
        end
        
        
        if sum( corr(:, i) > redundant_threshold) > 1  % find redundant sensor variables
            index = find( corr(:, i) > redundant_threshold);
            redundant = setdiff(index, i);
            
            for m = 1:length(redundant)
                if isempty(find(redundant_id == redundant(m)))
                    redundant_id = [redundant_id ; [redundant(m), i]];
                end
            end
        end
        
        
    end
end


% % % % node classification for sensors and commands % % % % %
% commands' all triggers happends in sensors set, however, sensors don't.
% For node s, given all trigger times of other nodes, calculate the unique trigger time of s.
% The unique trigger time of command nodes should be none.
% If the unique triggering time of node s is not none, then node s belongs to sensor nodes set.


alltraces_id = [];

[trigger_time, ~, UP_Pos, DOWN_Pos, ~] = triggering_detection( data, variable_id ) ;

nodes = variable_id;
unique_time = {};

sensors_number = 22 ;


for i = 1: length(nodes)
    if ~isempty(find( redundant_id == nodes(i)))
        [row, col] = find( redundant_id == nodes(i));
        redundant_index=[];
        for redu_node = redundant_id ( row, : )
            redundant_index = [redundant_index; find(nodes==redu_node) ];
        end
        unique_time{i} = setdiff( setdiff(trigger_time(:, [setdiff(1:length(nodes), redundant_index ), i] ), []), setdiff( trigger_time(:, setdiff(1:length(nodes), redundant_index ) ), []) );
    else
        unique_time{i} = setdiff( setdiff(trigger_time(:, 1 : length( nodes )), []), setdiff(trigger_time(:, setdiff(1:length(nodes), i) ), []) );
    end
    
    ratio = length(unique_time{i})/sum(trigger_time(:,i) ~= 0);
    
    alltraces_id = [alltraces_id; nodes(i), ratio, i, length(unique_time{i}), sum(trigger_time(:,i) ~= 0)];
    
end

alltraces_id = sortrows(alltraces_id, 2, 'descend') ;

sensorincluding_id = alltraces_id(1: sensors_number, :);
commandincluding_id = alltraces_id(sensors_number+1:end, : ) ;


command_delayed_set = cell(0, 4);

[commandincluding_id, sensorincluding_id, Timer_related_exist, command_delayed_set_update, laggings_update, laggings_UEntropy_update] = timer_command_updating(sensorincluding_id, commandincluding_id, trigger_time,  redundant_id, unique_time, timer_command_threshold) ;
if Timer_related_exist
    command_delayed_set = [command_delayed_set; command_delayed_set_update(1, :)] ;
    laggings = laggings_update ; 
    laggings_UEntropy = laggings_UEntropy_update ; 
end

while Timer_related_exist
    [commandincluding_id, sensorincluding_id, Timer_related_exist, command_delayed_set_update, laggings_update, laggings_UEntropy_update] = timer_command_updating(sensorincluding_id, commandincluding_id, trigger_time,  redundant_id, unique_time, timer_command_threshold) ;
    if Timer_related_exist
        command_delayed_set = [command_delayed_set; command_delayed_set_update(1, :)] ;
        laggings = laggings_update ; 
        laggings_UEntropy = laggings_UEntropy_update ; 
    end
end


sensor_set = sensorincluding_id ;
command_set = commandincluding_id ;

toc;
fprintf("end node classification {sensors, commands}. \n")

end




function [command_set, sensor_set, Timer_related_exist, command_delayed_set, laggings, laggings_UEntropy] = timer_command_updating(sensorincluding_id, commandincluding_id, trigger_time,  redundant_id, unique_time, timer_command_threshold)


sensor_set  = [];
command_set = [];
command_delayed_set = cell(0, 4);
update = 1;
command_update_threshold = max(commandincluding_id(:,2)) ;
Timer_related_exist = 0 ;

for i = 1: length(sensorincluding_id)
    
    % identify falling/rising transition in the unique transitions of var. in sensorincluding_id
    sensor_ca = sensorincluding_id(i, 3);
    sensor_ca_unique = unique_time{sensor_ca} ;
    
    for j = 1: length(sensorincluding_id)
        % compare the time lagging with other variables in Sensor_including set
        if ~(j == i)
            sensor_ca_comapred = sensorincluding_id(j, 3) ;
            % for the rising edges:
            lag = (repmat(sensor_ca_unique, 1, length( setdiff(trigger_time(:, sensor_ca_comapred ), 0 ) ))  - repmat(setdiff(trigger_time(:, sensor_ca_comapred ), 0 )', length( sensor_ca_unique ), 1)) ;
            lags = [];
            
            for m = 1:size( lag , 1 )
                a = min( lag(m, lag(m, :)>2)) ;
                if ~isempty(a)
                    lags(1, m) =  setdiff(a, []);
                end
            end
            
            laggings{i, j} = lags ;
            if isempty(laggings{i, j})
                laggings_UEntropy(i, j) = log2(0)  / log2(length(laggings{i, j})) ;
            else
                laggings_UEntropy(i, j) = Entropy(laggings{i, j}' ) / log2(length(laggings{i, j})) ;
            end
        end
    end
    
    
    for j = length(sensorincluding_id)+1: length(sensorincluding_id)+length(commandincluding_id)
        % compare the time lagging with other variables in Sensor_including set
        sensor_ca_comapred = commandincluding_id(j- length(sensorincluding_id) , 3) ; % the classified command is also to compare
        % for the rising edges:
        lag = (repmat(sensor_ca_unique, 1, length( setdiff(trigger_time(:, sensor_ca_comapred ), 0 ) ))  - repmat(setdiff(trigger_time(:, sensor_ca_comapred ), 0 )', length( sensor_ca_unique ), 1)) ;
        lags = [];
        
        for m = 1:size( lag , 1 )
            a = min( lag(m, lag(m, :)>2)) ;
            if ~isempty(a)
                lags(1, m) =  setdiff(a, []);
            end
        end
        
        laggings{i, j} = lags ;
        if isempty(laggings{i, j})
            laggings_UEntropy(i, j) = log2(0)  / log2(length(laggings{i, j})) ;
        else
            laggings_UEntropy(i, j) = Entropy(laggings{i, j}' ) / log2(length(laggings{i, j})) ;
        end
        
    end
    
    
    % remove the correlated redundant variabbles
    if ~isempty(find(redundant_id == sensorincluding_id(i, 1)) )
        
        [row, ~] = find( redundant_id == sensorincluding_id(i, 1) ) ;
        redundant_index=[];
        
        for redu_node = redundant_id ( row, : )
            redundant_index = [redundant_index; find(sensorincluding_id(:, 1)==redu_node) ];
        end
        for redu_node = 1:length(redundant_index)
            mm = find(sensorincluding_id(:, 3) == redundant_index(redu_node));
            laggings_UEntropy(i, mm) = 1 ;
        end
        
    end
    
    
    
    if isempty(sensor_ca_unique)
        laggings_UEntropy(i, : ) = 0 ;
    elseif length(sensor_ca_unique) == 1
        laggings_UEntropy(i, : ) = 1 ; %  only one unique ST, considered not possibile to be a timer command
    end
    
    
    
    laggings_UEntropy(i, i) = 1 ;
    
    timer_command_exist = min(laggings_UEntropy(i, setdiff(1:length(sensorincluding_id), i) ) ) < timer_command_threshold && sum(laggings_UEntropy(i, setdiff(1:length(sensorincluding_id), i) )) ~= 0 ;
    
    
    if timer_command_exist
        M = trigger_time ;
        if length(sensor_ca_unique)>2
            sen_rise_delay = find(laggings_UEntropy(i,:) == min(laggings_UEntropy(i, setdiff(1:length(sensorincluding_id), i) ) )) ;
            sen_rise_delay = setdiff(sen_rise_delay, commandincluding_id); 
            sen_rise_delay_time = mode( [laggings{ i, sen_rise_delay }] ) ;
            update_unique = sensor_ca_unique ; % setdiff ( timer_trigger_command , M(:, setdiff(1:size(M,2), sensorincluding_id(i,3) ) ))  ;
            
            if ~isempty(update_unique)
                update_unique = update_unique - sen_rise_delay_time ;
                update_unique = setdiff ( update_unique , M(:, setdiff(1:size(M,2), sensorincluding_id(i,3) ) ))  ;
            end
            
            command_delayed_set(update, :) = {sensorincluding_id(i , :), {sen_rise_delay}, sen_rise_delay_time, 1} ; 
            update = update+1;
            
        else
            update_unique = zeros(0,1);
        end
        
        
        command_delayed_set{update-1, 1}(1, 4) = length(update_unique);
        command_delayed_set{update-1, 1}(1, 2) = length(update_unique)/length(setdiff(M(:, sensorincluding_id(i, 3)), []) ) ;
        
        
        
        if command_delayed_set{update-1, 1}(1, 2) > command_update_threshold
            sensor_set = [sensor_set; sensorincluding_id(i , :)] ;
            command_delayed_set(update-1, :) = [];
            update = update-1;
        else
            Timer_related_exist = 1;
            
            command_update_threshold = command_delayed_set{update-1, 1}(1, 2) ;
            
            if min(update-2, 1) == 1
                sensor_set = [sensor_set; sensorincluding_id(sensorincluding_id(:, 1) == command_delayed_set{1:min(update-2, 1), 1}(1,1) , :) ] ;
                command_delayed_set(1:update-2, :) = [];
            end
            
        end
        
    else
        sensor_set = [sensor_set; sensorincluding_id(i , :)] ;
    end
    
    command_set = command_delayed_set(:, 1) ;
    
end

if Timer_related_exist == 1
    
    sensor_set = [sensor_set; commandincluding_id(1, :)] ;
    command_set = [command_set{:, 1}; commandincluding_id(2:end, :)] ;
    
    sensor_set = sortrows(sensor_set, 2, 'descend') ;
    command_set = sortrows(command_set, 2, 'descend' ) ;
else
    
    sensor_set = sensorincluding_id ;
    command_set = commandincluding_id ;
    
end


end


