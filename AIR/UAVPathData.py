import os
import easygui

RUN_ID = 0
TOTAL_TEST_RUNS = 25
CASES = 6

easygui.msgbox('Select a file in the main mode folder for path.'
                   'Click OK', title="Follow Instructions")
path = easygui.fileopenbox()
if "Run-0" not in path:
	RUN_ID = TOTAL_TEST_RUNS
path = path.split('Case', 1)[0]
for i in range(1, CASES + 1):
	runPath = path + "Case-" + str(i) + "\\Run-"
	
	if RUN_ID == 0:
		runPath = runPath + "0\\"
		os.system('grep "Drone data" ' + runPath + 'Simulation.log' + ' |  cut -d "[" -f6 | cut -d "]" -f1 > ' + runPath + 'UAV_Path')
	else:
		for j in range(1, RUN_ID + 1):
			pth = runPath + str(j) + "\\"
			print "Case-" + str(i) + "\\Run-" + str(j)
			os.system('grep "Drone data" ' + pth + 'Simulation.log' + ' |  cut -d "[" -f6 | cut -d "]" -f1 > ' + pth + 'UAV_Path')
