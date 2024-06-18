function [output] = IL_analyzer_CORE(inputs, initialization)
% columns in X represent the arrangement of Input register address
global cycle_time
cycle_time = cycle_time +1 

tic

sensor_dump_path_mat = "/Users/magnolia/tools/ARES/awlsim/Process_mimic/Sensors_mimic/sensors.mat"; 
% sensor_dump_path_pickle = "/Users/magnolia/tools/IL_analysis/awlsim/Process_mimic/Sensors_mimic/sensors.pickle" ;
command_dump_path_mat = "/Users/magnolia/tools/ARES/awlsim/Process_mimic/Command_trigger/commands.mat" ;

sensor_init_dump_path_mat = "/Users/magnolia/tools/ARES/awlsim/Process_mimic/Sensors_mimic/sensor_init.mat" ; 
command_init_dump_path_mat = "/Users/magnolia/tools/ARES/awlsim/Process_mimic/Sensors_mimic/command_init.mat" ; 

% % % sensor_dump_path_mat = "/Users/magnolia/tools/awlsim-onserver/Process_mimic/Sensors_mimic/sensors.mat"; 
% % % % sensor_dump_path_pickle = "/Users/magnolia/tools/IL_analysis/awlsim/Process_mimic/Sensors_mimic/sensors.pickle" ;
% % % command_dump_path_mat = "/Users/magnolia/tools/awlsim-onserver/Process_mimic/Command_trigger/commands.mat" ;
% % % sensor_init_dump_path_mat = "/Users/magnolia/tools/awlsim-onserver/Process_mimic/Sensors_mimic/sensor_init.mat" ; 
% % % command_init_dump_path_mat = "/Users/magnolia/tools/awlsim-onserver/Process_mimic/Sensors_mimic/command_init.mat" ; 



% % waiting for the finishing of last calculation  
while exist(command_init_dump_path_mat, 'file')|| exist(sensor_init_dump_path_mat, 'file') || exist(sensor_dump_path_mat, 'file')
    continue
end


% initiallizing the elevator Q address, as in 1 floor.    
command_init = zeros(1, 24) ; 
command_init(end - [1:7, 9:22] ) = initialization{2,1}; 
% command_init = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0]; 

% % % % % omitting when debug with online detection, @20210421 
save ('/Users/magnolia/tools/ARES/awlsim/Process_mimic/Sensors_mimic/command_init', 'command_init'); 

% should add a sensor initialization, like command_init, to set elevator run, from the 1F   
% sensor_init = [1,0,0,0,0,0,0,1,0,0,0,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0];  


sensor_init = [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] ;  
sensor_init(end-[3:27]) = initialization{1,1} ; 
save ('/Users/magnolia/tools/ARES/awlsim/Process_mimic/Sensors_mimic/sensor_init', 'sensor_init'); 
% % % save ('/Users/magnolia/tools/awlsim-onserver/Process_mimic/Sensors_mimic/sensor_init', 'sensor_init'); 


while exist(command_init_dump_path_mat, 'file')
    continue
end

pause(0.5)
% tic
save('/Users/magnolia/tools/ARES/awlsim/Process_mimic/Sensors_mimic/sensors', 'inputs');
% % % save('/Users/magnolia/tools/awlsim-onserver/Process_mimic/Sensors_mimic/sensors', 'inputs');






while ~exist(sensor_dump_path_mat, 'file')
    continue
end


if exist(command_dump_path_mat, 'file')
    file = dir(command_dump_path_mat);
    file_date = datetime(file.date,'InputFormat','dd-MMM-yyyy HH:mm:ss') ; 

    delete(command_dump_path_mat)
else
    
    file_date = datetime('01-01-0001 00:00:00', 'InputFormat','dd-MMM-yyyy HH:mm:ss') ; 
end




CommandExist = false; 
while ~CommandExist
    
    
    if exist(command_dump_path_mat, 'file')
        
        file = dir(command_dump_path_mat);
        updatefile_date = datetime(file.date,'InputFormat','dd-MMM-yyyy HH:mm:ss');  
        
        if updatefile_date > file_date
            CommandExist = true;
%             toc;
        else
            
            CommandExist = false; 
            delete(command_dump_path_mat)
        end
        
    else
        CommandExist = false ; 
    end
    
end

while ~exist(command_dump_path_mat, 'file')
    continue
end

pause(0.5)
load(command_dump_path_mat, 'command');
output = command; 

toc

end



