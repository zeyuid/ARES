function [H, sortData] = Entropy(data)
    % count the probability distribution and calculate the entropy
    
    if isempty(data)
        H = 0;
        sortData = data;
    else
        H = 0;
        [m, n] = size(data); % n: num of array; m: num of records

        sortData = sortrows(data);  

        last = sortData(1, :);
        p = 1;
        for k = 2:m
            e = sortData(k, :);
            if sum(e == last) == n
                p = p + 1;
            else
                last = e;
                H = H - p/m * log2(p/m);
                p = 1;
            end
        end
        H = H - p/m * log2(p/m);
    end
    
end

