package simulation.processing.parameters;

import java.util.HashMap;

//"/OneDrive/Documents/TAMU_Spring'17/AIR/P6 - H MA C/MultiAgentSimulation/src/simulation/data/"
public class Inputs {

	public static final int[] SIMULATOR_SIZE = new int[] { 3200, 1600 };
	public static final int[] UAV_INITIAL_POSITION = new int[] { 1600, 1500 };
	public static final int SCREEN_SHOT_RATE = 30;
	public static final int OBSERVE_TIME = 60 * 2;
	// 2 sec with 60 frames per second(default) - 300 frames

	public static final int CAM_TILT_MIN = -90;
	public static final int CAM_TILT_MAX = -40;
	public static final int UAV_HEIHT = 50;
	public static UAV_MODES UAV_MODE = UAV_MODES.MANUAL;

	public static String DATA_COLLECTION_PATH = System.getProperty("user.home")
			+ "/git/AIR_Spring-17_TAMU/RunsData/Trial-";

	public static final HashMap<String, float[][]> START_POSITIONS = new HashMap<String, float[][]>();
	public static final HashMap<String, float[][]> GOAL_POSITIONS = new HashMap<String, float[][]>();

	private static final float[][] START_CASE_1 = { { 1537, 1449 }, { 1566, 1443 }, { 1598, 1433 }, { 1639, 1444 },
			{ 1681, 1451 }, { 1672, 1491 } };
	private static final float[][] START_CASE_2 = { { 28, 163 }, { 3116, 342 }, { 66, 610 }, { 3084, 849 },
			{ 110, 1127 }, { 103, 1384 } };
	private static final float[][] START_CASE_3 = { { 973, 691 }, { 1353, 540 }, { 1304, 1012 }, { 1156, 1187 } };
	private static final float[][] START_CASE_4 = { { 1838, 1393 }, { 1531, 1384 }, { 1390, 1523 } };
	private static final float[][] START_CASE_5 = { { 1515, 64 }, { 1730, 1493 }, { 3098, 764 }, { 21, 932 },
			{ 3070, 104 }, { 48, 63 } };
	private static final float[][] START_CASE_6 = { { 670, 898 }, { 1340, 456 }, { 1360, 1022 }, { 1824, 460 },
			{ 1677, 851 }, { 1317, 238 } };

	private static final float[][] GOAL_CASE_1 = { { 50, 1395 }, { 76, 141 }, { 834, 74 }, { 1804, 86 }, { 2978, 242 },
			{ 3142, 1324 } };
	private static final float[][] GOAL_CASE_2 = { { 3139, 216 }, { 66, 413 }, { 3089, 629 }, { 124, 935 },
			{ 3079, 1127 }, { 1568, 1412 } };
	private static final float[][] GOAL_CASE_3 = { { 1032, 684 }, { 1409, 586 }, { 1332, 1011 }, { 1071, 297 } };
	private static final float[][] GOAL_CASE_4 = { { 348, 43 }, { 258, 116 }, { 58, 178 } };
	private static final float[][] GOAL_CASE_5 = { { 1407, 1459 }, { 1702, 70 }, { 90, 751 }, { 3058, 876 },
			{ 96, 1457 }, { 3084, 1435 } };
	private static final float[][] GOAL_CASE_6 = { { 1463, 708 }, { 749, 531 }, { 826, 516 }, { 1340, 1062 },
			{ 1177, 917 }, { 910, 1064 } };

	static {
		START_POSITIONS.put(Constants.CASE_ID + "1", START_CASE_1);
		GOAL_POSITIONS.put(Constants.CASE_ID + "1", GOAL_CASE_1);

		START_POSITIONS.put(Constants.CASE_ID + "2", START_CASE_2);
		GOAL_POSITIONS.put(Constants.CASE_ID + "2", GOAL_CASE_2);

		START_POSITIONS.put(Constants.CASE_ID + "3", START_CASE_3);
		GOAL_POSITIONS.put(Constants.CASE_ID + "3", GOAL_CASE_3);

		START_POSITIONS.put(Constants.CASE_ID + "4", START_CASE_4);
		GOAL_POSITIONS.put(Constants.CASE_ID + "4", GOAL_CASE_4);

		START_POSITIONS.put(Constants.CASE_ID + "5", START_CASE_5);
		GOAL_POSITIONS.put(Constants.CASE_ID + "5", GOAL_CASE_5);

		START_POSITIONS.put(Constants.CASE_ID + "6", START_CASE_6);
		GOAL_POSITIONS.put(Constants.CASE_ID + "6", GOAL_CASE_6);
	}

}
