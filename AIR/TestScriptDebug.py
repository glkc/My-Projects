import os

TRIAL_ID = 7
TOTAL_TEST_RUNS = 25
CASES = 6
METRIC_MODES = [2, 3]
RANDOM_MODES = [4, 5]

for k in METRIC_MODES:
    for j in range(1, CASES + 1):
        os.system("java -jar SimulatorDebug.jar " + str(TRIAL_ID) + " " + str(k) + " " + str(j) + " 0")

for k in MODES:
    for j in range(1, CASES + 1):
        for i in range(1, TOTAL_TEST_RUNS + 1):
            os.system("java -jar SimulatorDebug.jar " + str(TRIAL_ID) + " " + str(k) + " " + str(j) + " " + str(i))