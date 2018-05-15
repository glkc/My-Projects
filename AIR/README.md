# AIR_Spring-17_TAMU
P6 : Heterogeneous Multi-Agent Coordination : Class Project

To run the Simulator for collecting test metrics run TestScript.py from command line. For debug logs use TestScriptDebug.py.
It would run 25 simulations for all cases and 2 RANDOM_PATH test modes. 1 run for each case in NO_TILT and TILT mode.


If any file is changed, export the project and replace the jar file as "runnable jar".
Generate both info and debug jars, by changing log4j2.xml. Keep the project at info.

The Jar file takes Trail Number, Mode Number, CaseID, RunID as input, in order.

After each trial copy a FinalResults.xlxs template to the trial folder.
DataCommands contain command that extract data metrics from log files -> need to be copied manually to Excel file.

UAVPathData.py creates a file with coordinates from debug file in its specific folder.
UAVPathPlot takes the data generated above to plot and same image in respective folders. (Need to change path init before running - Update Trail ID)

To get data from the logs commands needed are in "DataCommands", copy results top excel sheet template.