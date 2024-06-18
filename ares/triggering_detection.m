function [trigger_time, persistent_time, UP_Pos, DOWN_Pos, DE_X] = triggering_detection(X, nodes)
    % the output of "triggering_detection" is <trigger_time, persistent_time> 
    
    in = X(:, nodes); % x is column vector
    
    del = [zeros(1, size(in, 2)); in];
    del(1, :) = del(2, :);
    del(end, :) = [];
    inn = ~in;
    dell = ~del;
    
    UP = dell & in;
    UP = double(UP);
    DOWN = inn & del;
    DOWN = double(DOWN);
    COUNT = ceil(0.5 * (sum(UP)+sum(DOWN)));
    
    DOWN((DOWN == 1)) = -1;
    DE_X = UP + DOWN;
    
    UP_Pos = zeros(max(COUNT), size(in, 2));
    DOWN_Pos = zeros(max(COUNT), size(in, 2));
    
    for j = 1 : size(in, 2)
        a = find (UP(:,j) == 1);
        UP_Pos(1:length(a),j) = a;
        b = find (DOWN(:,j) == -1);
        DOWN_Pos(1:length(b),j) = b;
        trigger_time(1:length([a; b]),j) = sort([ a;b]);
    end
    
    persistent_time = trigger_time(2:end, :) - trigger_time(1:end-1, :);
    persistent_time( (persistent_time < 0) ) = 0;
    
end