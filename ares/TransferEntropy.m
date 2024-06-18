function [ifactor, Delta_TTE, occupation] = TransferEntropy(X, Y, Xprime, t, w, tau)
% return the impact of x on y, Info_x2y; the transfer entropy, TE_x_y
%   X: the source time series in D-1 vector
%   t: time lag in X from present, smaller than length(X), t=0: realtime compare
%   Y: target time series in D-1 vector
%   w: time lag in Y from present, smaller than length(Y)
%   Xprime: annother condition, besides w time lagged y
%   Xprime have a same lag with X, i.e. t
%   tau: sample length of correlation


% go through the time series X and Y, and generate Xpat, Ypat, and Yt 
Xpat=[]; Ypat=[]; Xprimepat=[]; Yt=[];
starttime = max(t + tau, w) + 1 ; 
endtime = min(size(X,1), size(Y,1));
len = endtime - starttime +1 ;

for i = 1 
    period = [starttime-i+1 : starttime-i+1+len-1]' ;
    M = Y(period, :);
    Yt = [M, Yt];
end

if isempty(Xprime)
    for i = t+1: t+1+tau  
        period = [starttime-i+1 : starttime-i+1+len-1]' ;
        M = X(period, :);
        Xpat = [M, Xpat];
    end
else
    for i = t+1: t+1+tau  
        period = [starttime-i+1 : starttime-i+1+len-1]' ;
        M = X(period, :);
        Xpat = [M, Xpat];
        N = Xprime(period, :);
        Xprimepat = [N, Xprimepat];
    end
end


for j =  2:w+1  
    period = [starttime-j+1 : starttime-j+1+len-1]' ;
    M = Y(period, :);
    Ypat = [M, Ypat];
end

% % calculate the conditional mutual information 
% % the function of "Entropy" is self-made 

H_ypr_xpr_xprime = Entropy([Ypat, Xpat, Xprimepat]);
H_ypr_xprime = Entropy([Ypat, Xprimepat]);
H_y_ypr_xprime = Entropy([Yt, Ypat, Xprimepat]);
H_y_ypr_xpr_xprime = Entropy([Yt, Ypat, Xpat, Xprimepat]);

H_y = Entropy(Yt);

Delta_TTE = H_ypr_xpr_xprime - H_ypr_xprime + H_y_ypr_xprime - H_y_ypr_xpr_xprime;

ifactor = Delta_TTE /H_y ;
occupation = (H_ypr_xpr_xprime + H_y - H_y_ypr_xpr_xprime) /H_y ;

end


