
# RL with UHC on Energyplus

  

The folder contains only the parts to run the Q_table with epsilon greedy algorithm RL agent on UHC Environment for Svinnge House Energyplus model.

  

## Docker image

The docker image in the folder creates the simulation environment with Energyplus_v8.9.0, BCVTB_v1.6.0, Python_v3.6.1 and Java on Debian 10.
Energyplus and bcvtb are installed at location `/usr/local/EnergyPlus-8-9-0` and `/usr/local/bcvtb`. 

The simulation files should be run in a shared folder in image at `/var/uhc`

Example command for running interactive session sharing a windows desktop folder with docker image  **energyplus:8.9.0**, 

    docker run --rm -it -v C:\Users\Desktop\RL_UHC:/var/uhc/ energyplus:8.9.0

## Starting the RL Algorithm
To start the algorithm, you need to setup the parameters in the *parameters.json* file. 
Then just run the following command from the same location where rl_main is present.

    python rl_main.py

The script will delete all the previous run files from the folder *UHC_Environment/log*, *Episode_data* and *Q_plots*. It also will delete all the preious q_tables and score.
Then it will read the json file to determine the number of days, simulation time step and number of episodes to run the UHC environment. 

At the end of each episode, the script also saves the previous log in *UHC_Environment/log*, new plots and state .csv in *Episode_data* and q_plots _&_ q_table in *Q_plots*

To continue updating the same Q_table, you can write **True** to flag in **rl_main.py**, 

    CONTINUE_TRAINING_FLAG=False

## Folder Structure

In the folder, following files and folders are there.

**DO NOT DELETE ANY OF THE BELOW MENTIONED FILES OR FOLDER. THEY ARE IMPORTANT FOR RUNNING THE UHC**
 

-  **FILE - rl_main.py**
	- This is the main file from which runs the connects to the BCVTB environememt running Energyplus model.

-  **FILE - parameters.json**
	- All the hyper-parameters and parameters to run environment are written in JSON.

-  **FOLDER - UHC_Environment**
	- All the files and folders that are required to run the UHC environment are in this folder.
	- The file *PClient.py* is the main file that runs 1 iteration of the UHC environment.

-  **FOLDER - Q_Plots**
	- All the q_tables after each episodes are saved in this folder. Also, subsequent plots for q_tables are also there.

-  **FOLDER - Episode_data**
	- All the values for state varaibles are saved in a excel sheet and are also plotted for each episode.


# rl_main.py

File that starts episode iterations for updating Q_tables.

## Methods

-  **del_file():** Delete all previous IDF Log in *UHC_Environment\\log*, *Q_table*, *Score*, plots and saved tables in folder *Q_plots* and all episode data in folder *Episode_data*

-  **load_parameters():** Load the JSON parameters for printing purposes. We also edit the epsilon value after each episode and then write back to the JSON.

-  **write_parameters():** Write updated epsilon value back to the JSON.

-  **create_Q_table():** Create an Panda Q_table with ZERO before the environment run.

-  **create_score_table():** Create an empty Panda Score before the environment run.

-  **start_env(simulation_days, simulation_timesteps):** Starts the BCVTB environment running it on the command line.
	- simulation_days: Number of days for each episode runs (max 6 months)
	- simulation_timesteps: Energyplus simulation timestep

-  **rename_files():** Appends the Q_table, plots and logs with episode data just to avoid re-writing on the same file.

-  **Q_plot(q_table, ep):** Plots the updated Q_table after each run and saves them in folder *Q_plots*

  

# parameters.json

JSON with all the RL hyper parmeters and parameters to run the simulation.

## Parameters

-  **learning:** Hyper-parameters for rl algorithm
	- epsilon
	- epsilon_decay
	- learning_rate
	- discount

-  **simulation:** Parameters for setting up the UHC environment
-  **user_setpoint_temp:** This is the temperature RL will try to achieve. This value directly affects the terminal state in the environment as well as reward function in rl.

-  **simulation_timestep:** Energyplus (EP+) timesteps. This needs to be same as in the IDF file. If different, the BCVTB socket will not run properly and no simulation step will happen.

-  **tot_episode:** Maximum number of episodes for RL agent

-  **print_episode:** Flag to determine after how many episodes info will be printed on terminal

-  **simulation_days:** Number of days to run the UHC environment in EP+

  
  

# PClient.py

This is the main file that runs the UHC environment.

It starts and maintains the socket communication with BCVTB, updates the state, action, rewards and q tables for environment for each run.

  

## Methods

-  **load_file(fname):** Load either the Q table or the Score from the previous run.

-  **fname:** Name of the file being loaded

-  **load_file(fname, table):** Save the panda dataframe table to a file

-  **fname:** Name of the file to which table is saved

-  **table:** Table to be saved

-  **parameters_file(operation):** It either loads or saves the JSON parameter file, based on the option.

-  **operation:** Either *load* to load file, or *save* to save file

  

## Class - UHCEnv

Class implements the RL environment for UHC. The class runs 1 Episode of RL learning for defined number of iterations calculated by number of simulation days JSON parameter.

  

### Class Variables

-  **self.epsilon**
	- Hyper parameter controlling exploration and exploitation of state space

-  **self.learning_rate**
	- Hyper parameter affecting the Q_table value update

-  **self.discount**
	- Hyper parameter affecting the Q_table value update

-  **self.controller_set_temp**
	- This is the variable that is wirtten to the EP+ which determines the setpoint temperature for HVAC controller. This is initialized as the user_setpoint_temperature at start of simulation and is changed every iteration based on choose action by RL agent.

-  **self.q_table**
	- Variable for q_table

-  **self.score_table**
	- Variable for score at each episode

-  **self.episode_score**
	- Variable to update score at each iteration

-  **self.state**
	- Variable of type class State

-  **self.action**
	- Variable of type class Action

-  **self.reward**
	- Variable to save reward at each iteraton

-  **self.num_iterations**
	- Variable to determine how many step will be taken with BCVTB simulation

-  **self.sim_time_step**
	- Variable for time jump in the simulation in real-time. This needs to be same as the timestep in IDF file.

-  **self.terminal**
	- Variable that determines the terminal value for the RL simulation platform

### Class Methods

-  **self.__init__(q_table, score_table, parameters)**
	- Initializes the hyperparameters and variables. Here we also intizalize the socket communication with BCVTB and do a dummy exchange on the socket to get the initial states of the UHC environment.

-  **q_table** is the updated table from previous iteration

- **score** is the updated score table from previous iteration

- **parameters** are the JSON file parameters

-  **self.set_terminal(user_setpoint_temp)**
	- Define the terminal state. It is equal to the user defined temperature for the zone.

-  **user_setpoint_temp** is the user defined temperature from JSON file

-  **self.start_simulation_loop()**
	- It starts the socket communciation with BCVTB for defined self.num_iterations

-  **self.step(action, use_rl_method)**
	- This function performs the 1 step in the environment. It performs the action defined by the algorithm, then update the state, rewards and check if it is terminal state or not.

-  **self.max_action(state)**
	- The function looks into the q_table and determines the action for the given state.

-  **state** is the current state of the environment

-  **self.update_setpoint_temp(action, use_rl_method)**'
	- The function upadates the temperature setpoint based on the action.

-  **action** is the choosen action

-  **use_rl_method** is a flag just to determine if to update the setpoint according to RL or not

-  **self.ifTerminal(state)**
	- Function just checks if the current state is terminal or not

-  **self.update_states(data)**
	- Update the state based on the data from the environment and then digitized them

-  **self.calculate_reward()**
	- Calculate the reward for the given state according to a function defined here

-  **self.exit()**
	- Function to safely exit the simulation. It terminates the socket communication with BCVTB and also then saves the q_table, score, plot and save episode data.

