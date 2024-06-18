% function G = graph_plot(Adj)
% % % % plot the arrow from row number(commands) to the column number(sensors)
% 
% Adj(2: 2: end, 1) = Adj(2: 2: end, 1) * 2;
% if Adj(1, 2) > 26 
%     nodeNames = [cellstr(strcat('command', num2str(( Adj(1, 2:end) )'))) ; cellstr(strcat('sensor', num2str(( Adj(2:end, 1) ))))];
% else
%     nodeNames = [cellstr(strcat('sensor', num2str(( Adj(1, 2:end) )'))) ; cellstr(strcat('command', num2str(( Adj(2:end, 1) ))))];
% 
% nodeRow = size(Adj, 1) -1;
% nodeCol = size(Adj, 2) -1;
% 
% adj = zeros(nodeRow + nodeCol); 
% adj(end-nodeRow+1:end, 1:nodeCol) = Adj(2:end, 2:end);
% 
% G = digraph(adj, nodeNames);
% 
% plot(G) ; % plot the arrow from row number to the column number
% 
% end


function G = graph_generation(sensor_id, command_id, E_s_u, plotchose)
% % % generate the graph from E 
% parents = setdiff([E_s_u{2, 1:end}], 0) ;
% kids = [E_s_u{1, 1:end}] ;
if ~isempty(find (command_id(:, 1) == E_s_u{1, 1} ))
    parents = sensor_id(:, 1);
    kids = command_id(:, 1);
else
    kids = sensor_id(:, 1);
    parents = command_id(:, 1);
end

% nodeNames = [cellstr(strcat('sensor', num2str(( setdiff([E_s_u{2, 1:end}], 0)' )))); cellstr(strcat('command', num2str(( [E_s_u{1, 1:end}] )' ))) ] ; 

Adj = zeros( max([parents; kids]) );
nodeNames = [cellstr(strcat('s', num2str(( [1:max(sensor_id(:, 1))]' )))); cellstr(strcat('c', num2str(( [max(sensor_id(:, 1))+1 :max(command_id(:, 1))]') ))) ] ; 

% nodeNames = [cellstr( strcat ('s', num2str( 1:max(sensor_id(:, 1)) )' ) ), cellstr(strcat ('c', num2str( max(sensor_id(:, 1))+1 :max(command_id(:, 1)) )' )) ] ; 

for j = 1 : size(E_s_u, 2)
    
    kid_node = E_s_u{1, j};
    parent_nodes = E_s_u{2, j};
    parent_weights = E_s_u{3, j};
    
    for i = 1: length(parent_nodes)
        Adj( parent_nodes(i), kid_node ) = parent_weights(i);  % need change to the weight
    end
end



G = digraph(Adj, nodeNames);

if plotchose
    % % % graph plot
    figure()
    h = plot(G,'EdgeLabel',G.Edges.Weight);
%     nl = h.NodeLabel;
%     h.NodeLabel = '';
%     xd = get(h, 'XData');
%     yd = get(h, 'YData');
%     text(xd, yd, nl, 'FontSize',20, 'FontWeight','bold', 'HorizontalAlignment','left', 'VerticalAlignment','middle')
end
end

