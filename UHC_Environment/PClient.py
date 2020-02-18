# Python Imports
import math
import sys
import pandas as pd
import os
import numpy as np 
import json

# Local imports
from rlutils import State, Action
from pySocket import BCVTBPySocket
ut = BCVTBPySocket()
from pyDatabase import PyDatabase
db = PyDatabase()

def load_files(fname):
    df = None
    print("Loading {} file from folder".format(fname))
    path = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.abspath(os.path.join(path, os.pardir))
    for file in os.listdir(parent_dir):
        if file == fname:
            path = os.path.join(parent_dir, fname)

            if fname == "Q_table":
                df = pd.read_pickle(path, compression = 'gzip')
            if fname == "Score":
                df = pd.read_csv(path, sep = ";", header = 0, index_col = 0)

            print("Loaded table")
            print(df.head(5))
    
    return df

def save_files(fname, table, ep=None):
    print("Saving {} to folder".format(fname))
    cwd = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.abspath(os.path.join(cwd, os.pardir))
    
    # Saving back the updated Q_table
    path = os.path.join(parent_dir, fname)
    if fname == "Q_table":
        table.to_pickle(path, compression='gzip')
    if fname == "Score":
        table.to_csv(path, header = True, sep=';')
        

def parameters_file(operation, data = None):
    print("Loading simulation paremeters ...")
    cwd = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.abspath(os.path.join(cwd, os.pardir))

    prm_file = os.path.join(parent_dir, "parameters.json")

    if operation == "load":
        with open(prm_file, 'r') as json_file:
            data = json.load(json_file)
        json_file.close()
        return data

    if operation == "save":
         with open(prm_file, 'r') as json_file:
             json.dump(data, prm_file)


class UHCEnv:
    def __init__(self,  q_table, score_table, parameters, sim_start_time = 0, sim_time_step = 600):
      
        # Parameters
        days = int(parameters["simulation"]["simulation_days"])
        print("Running simulation for {} days".format(days))
        sim_time_step = int(parameters["simulation"]["simulation_timestep"])
        sim_time_step = (60/sim_time_step)*60
        print("Simulation Time Step: ", sim_time_step)

        # Hyper parameters
        self.epsilon = parameters["learning"]["epsilon"]
        self.learning_rate = parameters["learning"]["learning_rate"]
        self.discount = parameters["learning"]["discount"]
        print("Epsilon value: ", self.epsilon)


        # Default set temperature
        self.controller_set_temp = parameters["simulation"]["user_setpoint_temp"]

        # RL Variables
        self.q_table = q_table
        self.score_table = score_table
        self.episode_score = 0 
        

        # Create state and action objects
        self.state = State()
        self.action = Action()
        self.reward = 0


        # Calculating number of simulation Iterations to be done in 1 Episode
        sim_end_time = days*24*3600
        self.num_iterations = int(math.floor((sim_end_time-sim_start_time)/sim_time_step+1))
        print("Total number of iterations: ", self.num_iterations)
                
        # Timesteps 
        self.sim_time_step = sim_time_step

        # Set terminal state
        self.set_terminal(parameters["simulation"]["user_setpoint_temp"])

        # Socket variables
        ut.nDblWri = len(self.action)            # number of variables to write to socket  = Number of Actions
        ut.nDblRea = len(self.state)             # number of variables to read from socket = Number of States       
        
        # Establish Client Communication
        ut.establishClientSocket()
        if(ut.sockfd < 0):
            print("Error: Failed to obtain socket file descriptor. sockfd=", ut.sockfd)
            sys.exit((ut.sockfd)+100)

        # Initialize socket communication
        print("Initializing communication with BCVTB")
        dataWrite = [0 for _ in range(ut.nDblWri)]
        print("Data to write: ", dataWrite)
        ut.simTimWri = (1)*self.sim_time_step
        ut.exchangedoubleswithsocket(dataWrite)
        # Read state data from socket
        data =  ut.dblValRea
        nData = ut.nDblRea
        data = [data[i] for i in range(nData)]
        # Update the state
        self.update_states(data)


    def set_terminal(self, user_setpoint_temp):
        temp = State()
        self.terminal = temp.zone_air_temp_state_space.digitize(user_setpoint_temp)
        print("Terminal State: ", self.terminal)


    def max_action(self, state):
        # Fetch the column name that gives max Q value
        q_values = self.q_table.loc[state]
        action = q_values.idxmax()
        return action

    def update_setpoint_temp(self, action, use_rl_method=True):
        # Flag just to try of controller with and without RL Learning
        if(use_rl_method):
            print("Choosen action: ", action)
            self.controller_set_temp = self.controller_set_temp + action
            print("Setpoint: ", self.controller_set_temp)
            if self.controller_set_temp < self.action.min:
                return self.action.min
            elif self.controller_set_temp > self.action.max:
                return self.action.max
            else:
                return self.controller_set_temp

        # This will run just simple PID controller, it will still update Q_table and score,
        # but they have no effect on the action
        else:
            return self.controller_set_temp


    def ifTerminal(self, state):
        if (state.zone_air_temp == self.terminal) or (self.itr == self.num_iterations):
            return True
        else:
            return False
    
    def update_states(self, data):
        print("Data from Socket")
        print(data)

        self.state.update_states(data)
        print("Digitized values")
        print(self.state.get_states())


    def calculate_reward(self, ):
        # Reward function - Peak Function
        # fucntion of terminal temperature and current zone temperature
        moving_up_down = 100
        width = 9
        curvature = 2
        reward = max([moving_up_down-math.pow(width*abs(self.terminal - self.state.zone_air_temp), curvature), -200])

        return reward


    def step(self, action, use_rl_method = True):
        
        # Get perform the chossen action on the setpoint temperatures
        self.controller_set_temp = self.update_setpoint_temp(action, use_rl_method)
        # Convert action to a list of dimention ut.nDblWri
        dataWrite = [self.controller_set_temp]
        print("Data to write: ", dataWrite)
        ut.exchangedoubleswithsocket(dataWrite)
        # Read state data from socket
        data =  ut.dblValRea
        nData = ut.nDblRea
        data = [data[i] for i in range(nData)]
        
        # Updated states
        self.update_states(data)
 
        new_state = self.state.get_states()

        # TODO: Define better reward function
        reward = self.calculate_reward()

        # Check if the state is terminal or not
        done = self.ifTerminal(self.state)
        print("Terminal? ", done)

        # Add data to the database for storage and plotting
        db.addData(self.itr, data, self.controller_set_temp, self.sim_time_step, reward)

        return new_state, reward, done



    def exit(self, ):
        print("Exiting the environment .....")

        # Save the updted Q_table and Score
        save_files("Q_table", self.q_table)
        
        # Update the Score Table
        self.score_table = self.score_table.append(pd.DataFrame([self.episode_score], columns = ['Score']))
        self.score_table.reset_index(drop=True, inplace=True)
        print(self.score_table)
        save_files("Score", self.score_table)

        # Save the database file
        db.plot_data()
        db.saveDataFile()

        ut.sendclientmessage(1)
        ut.closeipc()
        sys.exit(1)


    def start_simulation_loop(self, ):
        
        # Current state
        print("Getting Current state")
        curr_state = self.state.get_states()
        # Keeping track of number of random actions
        rand_action = 0

        for self.itr in range(-1, self.num_iterations): 
            # Update Simulation time
            ut.simTimWri = (self.itr+1)*self.sim_time_step
            print("\n ------------- [{}/{}] Simulation Time: {} ------------- ".format(self.itr, self.num_iterations, ut.simTimRea/self.sim_time_step))
            
            # Chose a random action
            print("Choosing action..")
            rand_number = np.random.random_sample()
            if self.epsilon > rand_number or self.itr == 0:
                print("Random Action")
                rand_action += 1
                action = self.action.sample()
            else:
                print("Max Action")
                action = self.max_action(curr_state)
                

            # Step into environment
            print("Stepping into environment")
            use_rl_method = True
            new_state, reward, done = self.step(action, use_rl_method)

            # Update score
            self.episode_score +=reward

            # Update the Q_table
            print("Updating Q_table")
            max_action = self.max_action(new_state)
            print("\n")
            print("Action:                ", action)
            print("Max Action (newstate): ", max_action)
            print("Current State: ", curr_state)
            print("New State:     ", new_state)
            print("Q_values (curstate, action):    ", self.q_table.loc[curr_state, action])
            print("Q_values (curstate, maxaction): ", self.q_table.loc[curr_state, max_action])
            print("Q_values (newstate, action):    ", self.q_table.loc[new_state, action])
            print("Q_values (newstate, maxaction): ", self.q_table.loc[new_state, max_action])
            print("Reward: ", reward)
            
            self.q_table.loc[curr_state, action] += self.learning_rate*( reward + self.discount*(self.q_table.loc[new_state, max_action]) -  self.q_table.loc[curr_state, action] )
            print("Q_values (curstate, action):    ", self.q_table.loc[curr_state, action])
            print("\n")

            # Update states
            curr_state = new_state

            # if done:
            #     # If reached terminal state, then exit loop and close program
            #     self.exit()

        # Close of program after loop ends     
        print("Number of Random Actions: ", rand_action)   
        self.exit()


        
if __name__ == "__main__":     

    # Load parmeters
    parameters = parameters_file("load")

    # Load Q_table, Score and Hyper Parameters
    q_table = load_files("Q_table")
    score_table = load_files("Score")

    # Initialize Environment
    env = UHCEnv(q_table, score_table, parameters)

    # Start Loop
    env.start_simulation_loop()




