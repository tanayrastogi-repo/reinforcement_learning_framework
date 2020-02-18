import pandas as pd
import datetime
import os

import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class PyDatabase:
    def __init__(self, startDate = datetime.datetime(2002, 1, 1, 0, 0, 0)):
        # Defining the statdate in the pandas
        self.stDate = startDate

        # Initializing the Pandas Dataframe
        self.columns = ['TimeStamp', 'OutTemp', 'GlbSolRad', 'HVACHeating', 'ZoneAirTemp', 'ZonePplCnt', 'HVACMFR', 'SetPointTemp', 'Reward']  
        self.df = pd.DataFrame(columns=self.columns)

        # Close the excel sheets it open
        self.closeFile('Database.csv')    


    def closeFile(self, filename):
        try:
            f = open(filename)
            f.close()
            print("Closing File ", filename)
        except Exception as e:
            print(e)
        

    def addData(self, itr, data, setpoint, sim_time_step, reward):
        # Simulation Timestamp
        sim_time_step = sim_time_step / 60
        currDate = self.stDate + datetime.timedelta(minutes=itr*sim_time_step)
        dtTime = currDate.strftime("%a, %d, %B, %y, %H:%M:%S")  

        # Adding to the database
        self.df.loc[itr, 'TimeStamp'] = dtTime
        self.df.loc[itr,  'OutTemp':'HVACMFR'] = data 
        self.df.loc[itr,  'SetPointTemp'] = setpoint 
        self.df.loc[itr,  'Reward'] = reward 

    def saveDataFile(self,):
        self.df.to_csv('Database.csv', sep=';', decimal=',')

    def plot_data(self, ):
        print("Plotting Database ...")
        # Sort Index
        self.df.sort_index(inplace=True)
        dates = pd.to_datetime(self.df['TimeStamp'], format='%a, %d, %B, %y, %H:%M:%S')

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        for col in ['OutTemp', 'ZoneAirTemp', 'SetPointTemp']:
            fig.add_trace(go.Scatter(x=dates, y=self.df[col], name=col),secondary_y=False)
        for col in ['HVACMFR', 'GlbSolRad','HVACHeating', 'ZonePplCnt']:
            fig.add_trace(go.Scatter(x=dates, y=self.df[col], name=col, fill="tozeroy", line=dict(width=1)), secondary_y=True)
        for col in ['Reward']:
            fig.add_trace(go.Scatter(x=dates, y=self.df[col], name=col),secondary_y=True)

        # fig = make_subplots(specs=[[{"secondary_y": True}]])
        # for col in ['OutTemp', 'ZoneAirTemp', 'SetPointTemp']:
        #     fig.add_trace(go.Scatter(x=dates, y=self.df[col], name=col),secondary_y=False)
        # for col in ['GlbSolRad']:
        #     fig.add_trace(go.Scatter(x=dates, y=self.df[col], name=col, fill="tozeroy", line=dict(width=1)), secondary_y=True)
        # for col in ['Reward']:
        #     fig.add_trace(go.Scatter(x=dates, y=self.df[col], name=col),secondary_y=True)
        
        # Save Files
        path = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.abspath(os.path.join(path, os.pardir))
        fname = os.path.join(parent_dir, "Episode_data/Plot.html")
        plotly.offline.plot(fig, filename = fname, auto_open=False)