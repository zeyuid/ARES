function G = graph_generation(sensor_id, command_id, E_s_u, plotchose)
% % % generate the graph from E 


if ~isempty(find (command_id(:, 1) == E_s_u{1, 1} ))
    parents = sensor_id(:, 1);
    kids = command_id(:, 1);
else
    kids = sensor_id(:, 1);
    parents = command_id(:, 1);
end

Adj = zeros( max([parents; kids]) );
nodeNames = [cellstr(strcat('s', num2str(( [1:max(sensor_id(:, 1))]' )))); cellstr(strcat('c', num2str(( [max(sensor_id(:, 1))+1 :max(command_id(:, 1))]') ))) ] ; 

for j = 1 : size(E_s_u, 2)
    
    kid_node = E_s_u{1, j};
    parent_nodes = E_s_u{2, j};
    parent_weights = E_s_u{3, j};
    
    for i = 1: length(parent_nodes)
        Adj( parent_nodes(i), kid_node ) = parent_weights(i); 
    end
end

G = digraph(Adj, nodeNames);

if plotchose
    figure()
    h = plot(G,'EdgeLabel',G.Edges.Weight);
end

end


