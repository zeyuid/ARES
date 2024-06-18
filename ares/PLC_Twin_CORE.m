function [output] = PLC_Twin_CORE(inputs, initialization)
% columns in X represent the arrangement of Input register address
global cycle_time
cycle_time = cycle_time +1 

tic

%%%%%% %%%%%% %%%%%% %%%%%% %%%%%% %%%%%% %%%%%% %%%%%% %%%%%% %%%%%% %%%%%% %%%%%% 
%%%%%% Note: the following four paths should be consistent with the PLC-Twin %%%%%% 
%%%%%% %%%%%% %%%%%% %%%%%% %%%%%% %%%%%% %%%%%% %%%%%% %%%%%% %%%%%% %%%%%% %%%%%% 

% the interface of PLC-Twin, for validating the proposed mapping 
sensor_dump_path_mat = "../awlsim/Process_mimic/Sensors_mimic/sensors.mat"; 
command_dump_path_mat = "../awlsim/Process_mimic/Command_trigger/commands.mat" ;
% the interface of PLC-Twin, for initializing the memeory of PLC-Twin 
sensor_init_dump_path_mat = "../awlsim/Process_mimic/Sensors_mimic/sensor_init.mat" ; 
command_init_dump_path_mat = "../awlsim/Process_mimic/Sensors_mimic/command_init.mat" ; 


% % waiting for the finishing of last calculation  
while exist(command_init_dump_path_mat, 'file')|| exist(sensor_init_dump_path_mat, 'file') || exist(sensor_dump_path_mat, 'file')
    continue
end

% initiallizing the elevator Q address, pretending to be at the 1st floor 
command_init = zeros(1, 24) ; 
command_init(end - [1:7, 9:22] ) = initialization{2,1}; 
save ('../awlsim/Process_mimic/Sensors_mimic/command_init', 'command_init'); 

% should add a sensor initialization, like command_init, to set elevator run, from the 1F 
sensor_init = [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] ; 
sensor_init(end-[3:27]) = initialization{1,1} ; 
save ('../awlsim/Process_mimic/Sensors_mimic/sensor_init', 'sensor_init'); 


while exist(command_init_dump_path_mat, 'file')
    continue
end

% send validating sensor readings to PLC-Twin
pause(0.5)
save('../awlsim/Process_mimic/Sensors_mimic/sensors', 'inputs');

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


% wait for the generation of command from PLC-Twin 
CommandExist = false; 
while ~CommandExist
    if exist(command_dump_path_mat, 'file')
        
        file = dir(command_dump_path_mat);
        updatefile_date = datetime(file.date,'InputFormat','dd-MMM-yyyy HH:mm:ss');  
        
        if updatefile_date > file_date
            CommandExist = true;
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

% return the commands generated by PLC-Twin 
output = command; 

toc
end




