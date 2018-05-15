import os

TRIAL_ID = 6
TOTAL_TEST_RUNS = 25
CASES = 6
DATA_MODES = [2, 3]  # 2, 3
RANDOM_MODES = [4, 5]  # 4, 5

for k in DATA_MODES:
    for j in range(1, CASES + 1):
        os.system("java -jar Simulator.jar " + str(TRIAL_ID) + " " + str(k) + " " + str(j) + " 0")

for k in RANDOM_MODES:
    for j in range(1, CASES + 1):
        for i in range(1, TOTAL_TEST_RUNS + 1):
            os.system("java -jar Simulator.jar " + str(TRIAL_ID) + " " + str(k) + " " + str(j) + " " + str(i))
