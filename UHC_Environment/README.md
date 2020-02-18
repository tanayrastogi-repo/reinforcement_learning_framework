# UHC_Environment

The folder contains all the files and folder that are required to run the UHC environement for doing the RL learning. 
Here only the states, actions and rewards functions are defined for the enviroenment. 
Also, the updatation of Q_table in also implemented here. 

## Folder Structure
In the folder, following files and folders are there.

 **DO NOT DELETE ANY OF THE BELOW MENTIONED FILES OR FOLDER. THEY ARE IMPORTANT FOR RUNNING THE UHC**

 - **FILE - PClient.py**
	 - This is the *MAIN FILE* that connects to BCVTB, collects state data, perform actions in the environment and update the Q_table.
 -  **FILE - pyDatabase.py**
	 - Implements the pandas dataframe to collect all the state observations at each episode run. Here only we save them in a cav file, *Database.csv* and plot the state values in *Plot.html*
 - **FILE - pySocket.py**
	 - Implements the socket communication methods with BCVTB. All the functions are read from the utilSocket.so C-Library and just acts as an interface for the C functions. 
 - **FILE - rlutils.py**
	 - Implements the State and Action definition for the Learning agent for UHC environment. 
 - **FILE - utilSocket.so**
	 - This is the complied C library for socket communication with BCVTB.
 - **FILE - BCVTBmodel.xml**
	 - Implements the bcvtb model that connects the Python and EP+ models via sockets for data exchange.
 - **FOLDER - IDFRuntime**
	 - Folder contains the Svinnge House Model (.IDF), Stockholm weather file (.EPW) and the socket configuration file (.CGF). All other runtime files that are generated during the EP+ as also saved here. 
 - **FOLDER - log**
	 - Folder contains the log files at each iteration from BCVTB. Log *IDFSimulation.txt* is the log from the EP+ side and PySocket.txt is from the Python side. The folder also contains remaned log with episode number after each episode finishes. 