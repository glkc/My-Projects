package simulation.processing.parameters;

import java.util.HashMap;
import java.util.Map;

public enum UAV_MODES {
	MANUAL(1), AUTOMATIC_OBSERVATION(2), TEST_METRICS_NO_TILT_ALGO(3), TEST_METRICS_NO_TILT_RANDOM(
			4), TEST_METRICS_WITH_TILT_RANDOM(5);
	private final int modeNumber;

	private static Map<Integer, UAV_MODES> map = new HashMap<Integer, UAV_MODES>();

	static {
		for (UAV_MODES mode : UAV_MODES.values()) {
			map.put(mode.modeNumber, mode);
		}
	}

	private UAV_MODES(int number) {
		modeNumber = number;
	}

	public static UAV_MODES valueOf(int number) {
		return map.get(number);
	}
}
