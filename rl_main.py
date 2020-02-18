import subprocess
import json
import pandas as pd
import os
import json
from shutil import copy
import numpy as np 

import plotly
import plotly.graph_objects as go

from UHC_Environment.rlutils import State, Action
s = State()
a = Action()

def start_env(simulation_days, simulation_timesteps):
    print("Running UHC Environment")
    cmd = 'java -jar /usr/local/bcvtb/bin/BCVTB.jar -console UHC_Environment/BCVTBmodel.xml -days {} -IDFTimestep {}'.format(simulation_days, simulation_timesteps)
    #retval = subprocess.call(cmd, shell=False)
    os.system(cmd)

def load_files(fname):
    print("Loading updated {} file from folder".format(fname))
    for file in os.listdir('.'):
        if file == fname:
            path = os.path.join(os.getcwd(), fname)
            if fname == "Q_table":
                df = pd.read_pickle(path, compression = 'gzip')
            if fname == "Score":
                df = pd.read_csv(path, sep = ";", header = 0, index_col = 0)        
    return df


def create_Q_table(fname="Q_table"):
    q_table = None
    # First check if there is already a Q_table
    file_exist = False
    for file in os.listdir('.'):
        if file == fname:
            print("File already exist as", file)
            file_exist = True            
    
    if not file_exist:
        print("Initializing Q_table ...")
        ix = pd.Index(s._get_state_space())
        q_table = pd.DataFrame(float(0.0), index = ix, columns = list(a._get_state_space()))
        q_table.to_pickle(fname, compression='gzip')
        print("Created new empty Q_table!")
    
    return q_table

def create_score_table(fname="Score"):
    score_list = None
    # First check if there is already a Score
    file_exist = False
    for file in os.listdir('.'):
        if file == fname:
            print("File already exist as", file)
            file_exist = True

    if not file_exist:
        print("Initializing Score_table ...")
        score_list = pd.DataFrame(columns = ['Score'], dtype=np.int64)
        score_list.to_csv(fname, header = True, sep=';')
        print("Created new empty Score!")

    return score_list


def del_files(del_file_flag):
    print(" ------------ Deleting previous run data ------------ ")
    cwd = os.getcwd()
    print("Deleteing all the previous LOGS ...")
    dirr = os.path.join(cwd, "UHC_Environment/log")
    for f in os.listdir(dirr):
            os.remove(os.path.join(dirr, f))

    print("Cleaning previous PLOTS and TABLES ...")
    dirr = os.path.join(cwd, "Q_Plots")
    for f in os.listdir(dirr):
        os.remove(os.path.join(dirr, f))
    
    print("Deleteing previous DATABASES ...")
    dirr = os.path.join(cwd, "Episode_data")
    for f in os.listdir(dirr):
        os.remove(os.path.join(dirr, f))

    if not del_file_flag:                     
        print("Deleteing previous Q_TABLE ...")
        f = os.path.join(cwd, "Q_table")
        if os.path.exists(f):
            os.remove(os.path.join(dirr, f))

        print("Deleteing previous SCORE ...")
        f = os.path.join(cwd, "Score")
        if os.path.exists(f):
            os.remove(os.path.join(dirr, f))    
    
    print("\n")
    

def rename_files(ep):

    # Current working directory
    cwd = os.getcwd()

    # Renaming Logfiles in PySocket
    fname = os.path.join(cwd, "UHC_Environment/log/PySocket.log")
    new_fname = os.path.join(cwd, "UHC_Environment/log/PySocket_{}.log".format(ep))
    os.rename(fname,new_fname)

    # Renaming Q_tables
    fname = os.path.join(cwd, "Q_table")
    new_fname = os.path.join(cwd, "Q_Plots/Q_table_{}".format(ep))
    copy(fname, new_fname)

    # Copying Databases
    fname = os.path.join(cwd, "UHC_Environment/Database.csv")
    new_fname = os.path.join(cwd, "Episode_data/Database_{}.csv".format(ep))
    copy(fname, new_fname)

    # Renaming Database Plots
    fname = os.path.join(cwd, "Episode_data/Plot.html")
    new_fname = os.path.join(cwd, "Episode_data/Plot_{}.html".format(ep))
    copy(fname, new_fname)

    print("Done renaming files!!")

def Q_plot(q_table, ep):
    q = q_table.transpose()
    q.columns = list(range(len(q.columns)))

    scale = max([abs(q.values.max()+1), abs(q.values.min()-1)])

    fig = go.Figure(data = go.Heatmap(z = q.values,
                                      y = list(q.index),
                                      x = [''.join(str(tp)) for tp in s._get_state_space()],
                                     colorscale = "RdGy", 
                                     zmax = scale,
                                     zmin = -scale))

    fig.update_layout(
    yaxis = dict(
                tickmode = 'array',
                tickvals = list(q.index),
                ticktext = list(q.index)
                )
    )

    path = os.path.join(os.getcwd(), "Q_plots") 
    fname = os.path.join(path, "Q_table_{}.html".format(ep))
    plotly.offline.plot(fig, filename = fname, auto_open=False)
    print("Done plotting Q_table!!")


def load_parameters():
    print("Loading Parameters ...")
    with open('parameters.json') as json_file:
        data = json.load(json_file)
    return data

def write_parameters(data):
    with open('parameters.json', 'w') as json_file:
        json.dump(data, json_file)
        json_file.close()


if __name__ == "__main__":
    # FLAG to not delete the previous trained Q_table and continue training
    CONTINUE_TRAINING_FLAG = False
    
    # Delete all previous
    del_files(CONTINUE_TRAINING_FLAG)

    # Load parmeters
    parameters = load_parameters()
    # Parameters
    max_episodes = parameters["simulation"]['tot_episode']
    print_episode = parameters["simulation"]['print_episode']
    simulation_days = parameters["simulation"]['simulation_days']
    simulation_timesteps = parameters["simulation"]['simulation_timestep']

    # Update the Epsilon values
    parameters = load_parameters()
    parameters['learning']['epsilon'] =  0.9
    write_parameters(parameters)
    
    # Create Q_table
    q_table = create_Q_table()   
    score_list = create_score_table()

    print("\nMaximum Episodes: ", max_episodes)
    print("Simulation Days:  ", simulation_days)
    for ep in range(max_episodes):        
        # Flag to check the operation in env
        print("\n  ------------ Episode: {} ------------ ".format(ep))
        
        # Start BCVTB and run the UHC environment
        start_env(simulation_days, simulation_timesteps)

        # Load the updated Q_table
        q_table_updated = load_files("Q_table")
        # Load the updated Score_table
        score_updated = load_files("Score")

        # Current episode (adding upon if continued from previous)
        current_ep = score_updated.index.tolist()[-1]

        # Rename the PySocket.log file for avoid re-writing
        rename_files(current_ep)



        # Save plots for the Q_table
        Q_plot(q_table_updated, current_ep)

        if ep % print_episode == 0:
            print("[x] Finished with Episode: {}    {}".format(ep, score_updated.loc[len(score_updated) -1]))
        
        # Update the Epsilon values
        parameters = load_parameters()
        parameters['learning']['epsilon'] *=  parameters['learning']['epsilon_decay']
        write_parameters(parameters)

        # This only for pausing the interation after every episode
        #input("Press Enter to continue")