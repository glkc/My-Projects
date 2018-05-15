package simulation.processing.uav;

import java.util.Collection;
import java.util.HashMap;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import processing.core.PVector;
import simulation.processing.parameters.Inputs;
import simulation.processing.parameters.UAV_MODES;

@SuppressWarnings("rawtypes")
public class UAV {

	private String id;
	private UAV_MODES mode;
	private PVector loc;
	private float yaw;
	private Camera uavCam;
	private UAVMechanics mechanisms;
	private HashMap<String, EmilyData> emilyDataList;
	private int timeNotObservingEmily = 0; // Inc only when there is an EMILY
	private float distanceMoved = 0;
	private float yawChange = 0;
	private static final Logger logger = LogManager.getLogger(UAV.class.getName());

	public UAV(PVector loc, UAV_MODES mode) {
		super();
		this.id = "UAV-" + java.util.UUID.randomUUID().toString();
		this.loc = loc;
		this.yaw = 0;
		this.uavCam = new Camera(Inputs.CAM_TILT_MIN);
		this.emilyDataList = new HashMap<String, EmilyData>();
		setUAVMode(mode);
	}

	public PVector getLoc() {
		return this.loc;
	}

	public void setLoc(PVector loc) {
		distanceMoved += loc.dist(this.loc);
		this.loc = loc;
	}

	public String getId() {
		return this.id;
	}

	public Camera getUavCam() {
		return this.uavCam;
	}

	public void setUavCam(Camera uavCam) {
		this.uavCam = uavCam;
	}

	public float getYaw() {
		return this.yaw;
	}

	public void changeYaw(float angle) {
		this.yaw += angle;
		this.yawChange += Math.abs(angle);
	}

	public void incTimeNotObservingEmily() {
		this.timeNotObservingEmily++;
	}

	public UAVMechanics getMechanisms() {
		return this.mechanisms;
	}

	public HashMap<String, EmilyData> getEmilyDataList() {
		return this.emilyDataList;
	}

	public UAV_MODES getMode() {
		return this.mode;
	}

	public void setUAVMode(UAV_MODES mode) {
		if (mode == UAV_MODES.MANUAL) {
			this.mode = UAV_MODES.MANUAL;
			this.mechanisms = new Manual(this);
			logger.info("Setting " + this.id + " to manual mode");
		} else {
			if (Inputs.UAV_MODE == UAV_MODES.MANUAL)
				this.mode = UAV_MODES.AUTOMATIC_OBSERVATION;
			else
				this.mode = Inputs.UAV_MODE;
			this.mechanisms = new Observe(this);
			logger.info("Setting " + this.id + " to observe mode");
		}
	}

	public void addEmily(String id, PVector pos, PVector goal) {
		if (!this.emilyDataList.containsKey(id))
			this.emilyDataList.put(id, new EmilyData(id, pos, goal));
	}

	public void updateEmilyVisited(String id) {
		if (this.emilyDataList.containsKey(id)) {
			EmilyData emilyData = this.emilyDataList.get(id);
			emilyData.setVisited(true);
			this.emilyDataList.replace(id, emilyData);
		}
	}

	public void resetEmilyVisited() {
		Collection<String> keys = this.emilyDataList.keySet();
		for (String key : keys) {
			EmilyData emilyData = this.emilyDataList.get(key);
			emilyData.setVisited(false);
			this.emilyDataList.replace(key, emilyData);
		}
	}

	public void resetEmilyVisited(String id) {
		if (this.emilyDataList.containsKey(id)) {
			EmilyData emilyData = this.emilyDataList.get(id);
			emilyData.setVisited(false);
			this.emilyDataList.replace(id, emilyData);
		}
	}

	public boolean allEmilysAtGoal() {
		Collection<String> keys = this.emilyDataList.keySet();
		if (keys.isEmpty())
			return true;
		for (String key : keys) {
			EmilyData emilyData = this.emilyDataList.get(key);
			if (!(Math.abs(emilyData.getPos().x - emilyData.getGoal().x) < 1
					&& Math.abs(emilyData.getPos().y - emilyData.getGoal().y) < 1))
				return false;
		}
		return true;
	}

	public PVector getCentroidOfAOV() {
		return shiftToMainAxis(this.uavCam.getCentroidOfAOV());
	}

	public PVector shiftToMainAxis(PVector point) {
		float x = (float) (point.x * Math.cos(yaw * Math.PI / 180) - point.y * Math.sin(yaw * Math.PI / 180));
		float y = (float) (point.x * Math.sin(yaw * Math.PI / 180) + point.y * Math.cos(yaw * Math.PI / 180));
		return new PVector(x, y).add(getLoc());
	}

	public PVector[] getBoundingBoxOfAOV() {
		float[][] coordinates = this.uavCam.getBoxCoordinates();
		PVector[] transformedCoord = new PVector[4];
		for (int i = 0; i < coordinates.length; i++) {
			transformedCoord[i] = shiftToMainAxis(new PVector(coordinates[i][0], coordinates[i][1]));
		}
		return transformedCoord;
	}

	public void getAllMetrics() {
		logger.info("Metrics for " + this.id);
		logger.info("Total change in UAV Yaw (In Degrees)- " + Float.toString(this.yawChange));
		logger.info("Total change in UAV Camera Tilt (In Degrees)- " + Float.toString(this.uavCam.getTiltChange()));
		logger.info("Total change in UAV Movement (In Pixels) - " + Float.toString(this.distanceMoved));
		logger.info("Total frameCount of not observing any EMILY - " + Integer.toString(this.timeNotObservingEmily));
	}

	@Override
	public String toString() {
		StringBuilder builder = new StringBuilder();
		builder.append("UAV [id=").append(id).append(", mode=").append(mode).append(", loc=").append(loc)
				.append(", yaw=").append(yaw).append(", uavCam=").append(uavCam.toString()).append(", emilyDataList=")
				.append(emilyDataList.values().toString()).append(", timeNotObservingEmily=")
				.append(timeNotObservingEmily).append(", distanceMoved=").append(distanceMoved).append(", yawChange=")
				.append(yawChange).append("]");
		return builder.toString();
	}

}
