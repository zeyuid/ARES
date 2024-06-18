function [ifactor, Delta_TTE, occupation] = TransferEntropy(X, Y, Xprime, t, w, tau, direction)
% return the impact of x on y, Info_x2y; the transfer entropy, TE_x_y
%   X: the source time series in D-1 vector
%   t: time lag in X from present, smaller than length(X), t=0: realtime compare
%   Y: target time series in D-1 vector
%   w: time lag in Y from present, smaller than length(Y)
%   Xprime: annother condition, besides w time lagged y
%   Xprime have a same lag with X, i.e. t
%   direction: transfer direction: rising -- [1,0], falling -- [0, 1]





% go through the time series X and Y, and populate Xpat, Ypat, and Yt
Xpat=[]; Ypat=[]; Xprimepat=[]; Yt=[];

starttime = max(t + tau, w) + 1 ; % max(t + tau, w + tau) + 1 ;  % 
endtime = min(size(X,1), size(Y,1));
len = endtime - starttime +1 ;

for i = 1 %: tau+1
    period = [starttime-i+1 : starttime-i+1+len-1]' ;
    M = Y(period, :);
    Yt = [M, Yt];
end

if isempty(Xprime)
    for i = t+1: t+1+tau  % t+1: t+1+tau
        period = [starttime-i+1 : starttime-i+1+len-1]' ;
        M = X(period, :);
        Xpat = [M, Xpat];
    end
else
    for i = t+1: t+1+tau  % t+1: t+1+tau
        period = [starttime-i+1 : starttime-i+1+len-1]' ;
        M = X(period, :);
        Xpat = [M, Xpat];
        N = Xprime(period, :);
        Xprimepat = [N, Xprimepat];
    end
end


for j =  2:w+1  % max(2, w+1) : w+1+tau 
    period = [starttime-j+1 : starttime-j+1+len-1]' ;
    M = Y(period, :);
    Ypat = [M, Ypat];
end


% % calculate the temporal transfer entropy 
% % i.e. incremental mutual information given an auto-regression series
% % Fucntion "Entropy" is self-made 

H_ypr_xpr_xprime = Entropy([Ypat, Xpat, Xprimepat]);
H_ypr_xprime = Entropy([Ypat, Xprimepat]);
H_y_ypr_xprime = Entropy([Yt, Ypat, Xprimepat]);
H_y_ypr_xpr_xprime = Entropy([Yt, Ypat, Xpat, Xprimepat]);

H_y = Entropy(Yt);


Delta_TTE = H_ypr_xpr_xprime - H_ypr_xprime + H_y_ypr_xprime - H_y_ypr_xpr_xprime;

ifactor = Delta_TTE /H_y ;
occupation = (H_ypr_xpr_xprime + H_y - H_y_ypr_xpr_xprime) /H_y ;


% calculate the probability that X impact Y 
% Info_x2y = Delta_TTE / H_y_condition ;












% % go through the time series X and Y, and populate Xpat, Ypat, and Yt
% Xpat=[]; Ypat=[]; Yprimepat=[]; Yt=[];
% 
% 
% starttime = max(t, w) + 1 + tau ;
% endtime = min(size(X,1), size(Y,1));
% l = endtime - starttime +1 ;
% 
% 
% for i = 1 : tau+1
%     period = [starttime-i+1 : starttime-i+1+l-1]' ;
%     M = Y(period, :);
%     Yt = [Yt, M];
% end
% 
% 
% 
% if isempty(Xprime)
%     for i = 1: t+1+tau
%         period = [starttime-i+1 : starttime-i+1+l-1]' ;
%         M = X(period, :);
%         Xpat = [Xpat, M];
%     end
% else
%     for i = 1: t+1+tau
%         period = [starttime-i+1 : starttime-i+1+l-1]' ;
%         M = X(period, :);
%         Xpat = [Xpat, M];
%         N = Xprime(period, :);
%         Yprimepat = [Yprimepat, N];
%     end
% end
% 
% 
% for j = 2:w+1
%     period = [starttime-j+1 : starttime-j+1+l-1]' ;
%     M = Y(period, :);
%     Ypat = [Ypat, M];
% end
% 
% 
% 
% % calculate the entropy of Y not decided by auto-regression
% nonauto_H = Entropy([Yt, Ypat]) - Entropy(Ypat);  % H(Yt|Ypat)
% 
% Ypat = [Ypat, Yprimepat];
% % calculate the transfer entropy
% % Function "entropy" is system involeved, Fucntion "Entropy" is self-made
% H_y_ypr = Entropy([Yt, Ypat]);  
% H_ypr_xpr = Entropy([Ypat, Xpat]);
% H_ypr = Entropy([Ypat]);
% H_y_ypr_xpr = Entropy([Yt, Ypat, Xpat]);
% % H_y = Entropy(Yt) ;
% % H_xpr = Entropy(Xpat) ;
% 
% TE_x_y = H_y_ypr - H_ypr + H_ypr_xpr - H_y_ypr_xpr ;
% Info_x2y = TE_x_y / nonauto_H ;
% 








% % % 
% % % % go through the time series X and Y, and populate Xpat, Ypat, and Yt
% % % Xpat=[]; Ypat=[]; Yprimepat=[];
% % % starttime = max(t, w) + 1;
% % % endtime = min(size(X,1), size(Y,1));
% % % 
% % % Yt = Y(starttime:endtime, :);
% % % l = length(Yt);
% % % 
% % % if isempty(Yprime)
% % %     for i = 1: t+1
% % %         period = [starttime-i+1 : starttime-i+1+l-1]' ;
% % %         M = X(period, :);
% % %         Xpat = [Xpat, M];
% % %     end
% % % else
% % %     for i = 1: t+1
% % %         period = [starttime-i+1 : starttime-i+1+l-1]' ;
% % %         M = X(period, :);
% % %         Xpat = [Xpat, M];
% % %         N = Yprime(period, :);
% % %         Yprimepat = [Yprimepat, N];
% % %     end
% % % end
% % % 
% % % 
% % % for j = 2:w+1
% % %     period = [starttime-j+1 : starttime-j+1+l-1]' ;
% % %     M = Y(period, :);
% % %     Ypat = [Ypat, M];
% % % end
% % % 
% % % % calculate the entropy of Y not decided by auto-regression
% % % nonauto_H = Entropy([Yt, Ypat]) - Entropy(Ypat);  % H(Yt|Ypat)
% % % 
% % % Ypat = [Ypat, Yprimepat];
% % % % calculate the transfer entropy
% % % % Function "entropy" is system involeved, Fucntion "Entropy" is self-made
% % % H_y_ypr = Entropy([Yt, Ypat]);  
% % % H_ypr_xpr = Entropy([Ypat, Xpat]);
% % % H_ypr = Entropy([Ypat]);
% % % H_y_ypr_xpr = Entropy([Yt, Ypat, Xpat]);
% % % % H_y = Entropy(Yt) ;
% % % H_xpr = Entropy(Xpat) ;
% % % 
% % % 
% % % if transfer
% % %     TE_x_y = H_y_ypr - H_ypr + H_ypr_xpr - H_y_ypr_xpr ;
% % %     Info_x2y = TE_x_y / nonauto_H ;
% % % else
% % %     TMI = H_y_ypr + H_xpr - H_y_ypr_xpr ;
% % %     TE_x_y = TMI ;
% % %     Info_x2y = TMI / H_y_ypr ;
% % % end





% return the impact of x on y, Info_x2y; the transfer entropy, TE_x_y
%   X: the source time series in D-1 vector
%   t: time lag in X from present, smaller than length(X), t=0: realtime compare
%   Y: target time series in D-1 vector
%   w: time lag in Y from present, smaller than length(Y)
%   Yprime: annother condition, besides w time lagged y
%   Yprime have a same lag with X, i.e. t


%   t=0, w=0: TransferEntropy(X, Y, t, w) = MI(X,Y)
%   w=0: TransferEntropy(X, Y, t, w) = TMI(X, Y, t)


% check input arguments
% if nargin < 1
%     error('Please provide time series in format [source; target]');
% elseif nargin < 2
%     if size(X,2) == 2
%         Y = X(:, 2);
%         X = X(:, 1);
%     else
%         error('Please provide time series in format [source; target]');
%     end
% end



% transfer to the column format
% X=X(:);
% Y=Y(:);
% Yprime=Yprime(:);



% % % % go through the time series X and Y, and populate Xpat, Ypat, and Yt
% % % Xpat=[]; Ypat=[]; Xprimepat=[]; Yt=[];
% % % 
% % % starttime = max(t, w) + 1 + tau ;
% % % endtime = min(size(X,1), size(Y,1));
% % % l = endtime - starttime +1 ;
% % % 
% % % for i = 1 : tau+1
% % %     period = [starttime-i+1 : starttime-i+1+l-1]' ;
% % %     M = Y(period, :);
% % %     Yt = [Yt, M];
% % % end
% % % 
% % % if isempty(Xprime)
% % %     for i = 1: t+1+tau
% % %         period = [starttime-i+1 : starttime-i+1+l-1]' ;
% % %         M = X(period, :);
% % %         Xpat = [Xpat, M];
% % %     end
% % % else
% % %     for i = 1: t+1+tau
% % %         period = [starttime-i+1 : starttime-i+1+l-1]' ;
% % %         M = X(period, :);
% % %         Xpat = [Xpat, M];
% % %         N = Xprime(period, :);
% % %         Xprimepat = [Xprimepat, N];
% % %     end
% % % end
% % % 
% % % for j = 2:w+1
% % %     period = [starttime-j+1 : starttime-j+1+l-1]' ;
% % %     M = Y(period, :);
% % %     Ypat = [Ypat, M];
% % % end
% % % 
% % % % calculate the entropy of Y not decided by auto-regression
% % % H_y_condition = Entropy([Yt, Ypat]) - Entropy(Ypat);  % H(Yt|Ypat)
% % % 
% % % % calculate the transfer temporal mutual information, 
% % % % i.e. incremental mutual information given an auto-regression series
% % % % Fucntion "Entropy" is self-made 
% % % 
% % % H_x_xpr = Entropy([Xpat, Xprimepat]);
% % % H_xpr = Entropy(Xprimepat);
% % % H_xpr_y = Entropy([Yt, Xprimepat]);
% % % H_y_x_xpr = Entropy([Yt, Xpat, Xprimepat]);
% % % 
% % % TTMI = H_x_xpr - H_xpr + H_xpr_y - H_y_x_xpr; % transfer temporal mutual information
% % % 
% % % % calculate the probability that X impact Y 
% % % Info_x2y = TTMI / H_y_condition ;








% % % % go through the time series X and Y, and populate Xpat, Ypat, and Yt
% % % Xpat=[]; Ypat=[]; Yprimepat=[];
% % % starttime = max(t, w) + 1;
% % % endtime = min(size(X,1), size(Y,1));
% % % 
% % % Yt = Y(starttime:endtime, :);
% % % l = length(Yt);
% % % 
% % % if isempty(Yprime)
% % %     for i = 1: t+1
% % %         period = [starttime-i+1 : starttime-i+1+l-1]' ;
% % %         M = X(period, :);
% % %         Xpat = [Xpat, M];
% % %     end
% % % else
% % %     for i = 1: t+1
% % %         period = [starttime-i+1 : starttime-i+1+l-1]' ;
% % %         M = X(period, :);
% % %         Xpat = [Xpat, M];
% % %         N = Yprime(period, :);
% % %         Yprimepat = [Yprimepat, N];
% % %     end
% % % end
% % % 
% % % 
% % % for j = 2:w+1
% % %     period = [starttime-j+1 : starttime-j+1+l-1]' ;
% % %     M = Y(period, :);
% % %     Ypat = [Ypat, M];
% % % end
% % % 
% % % % calculate the entropy of Y not decided by auto-regression
% % % nonauto_H = Entropy([Yt, Ypat]) - Entropy(Ypat);  % H(Yt|Ypat)
% % % 
% % % Ypat = [Ypat, Yprimepat];
% % % % calculate the transfer entropy
% % % % Function "entropy" is system involeved, Fucntion "Entropy" is self-made
% % % H_y_ypr = Entropy([Yt, Ypat]);  
% % % H_ypr_xpr = Entropy([Ypat, Xpat]);
% % % H_ypr = Entropy([Ypat]);
% % % H_y_ypr_xpr = Entropy([Yt, Ypat, Xpat]);
% % % % H_y = Entropy(Yt) ;
% % % H_xpr = Entropy(Xpat) ;
% % % 
% % % 
% % % if transfer
% % %     TE_x_y = H_y_ypr - H_ypr + H_ypr_xpr - H_y_ypr_xpr ;
% % %     Info_x2y = TE_x_y / nonauto_H ;
% % % else
% % %     TMI = H_y_ypr + H_xpr - H_y_ypr_xpr ;
% % %     TE_x_y = TMI ;
% % %     Info_x2y = TMI / H_y_ypr ;
% % % end



end


