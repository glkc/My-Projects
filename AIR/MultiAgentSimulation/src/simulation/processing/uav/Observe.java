package simulation.processing.uav;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Random;
import java.util.Timer;
import java.util.TimerTask;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import processing.core.PVector;
import simulation.processing.parameters.Constants;
import simulation.processing.parameters.Inputs;
import simulation.processing.parameters.UAV_MODES;

/*
 * Find one closest EMILY and move accordingly. This is called in draw() continuously.
 * @see simulation.processing.uav.UAVMechanics#nextStep()
 */
public class Observe implements UAVMechanics<Float> {

	private static final int EMILY_BOUNDARY = 50;
	private static final int EMILY_INSIDE_UAV_VIEW_ANGLE_BUFFER = 1;
	private static final Logger logger = LogManager.getLogger(Observe.class.getName());
	private HashMap<String, EmilyData> emilyDataList;
	private Timer timer = new Timer();
	private String closestId = null;
	private PVector droneLoc = null;
	private PVector centroid = null;
	private int toggle = 0;
	private int numVisited;
	private UAV drone;
	private boolean canFit = false;
	private boolean move = false;

	public Observe(UAV uav) {
		this.drone = uav;
		this.numVisited = getNumVisited();
		this.emilyDataList = drone.getEmilyDataList();
	}

	private int getNumVisited() {
		HashMap<String, EmilyData> emilyDataList = this.drone.getEmilyDataList();
		int numVisited = 0;
		for (String key : emilyDataList.keySet()) {
			if (emilyDataList.get(key).getVisited() == true) {
				numVisited++;
			}
		}
		return numVisited;
	}

	@Override
	public void updateUAVPosition(int notUsing1, int notUsing2, int notUsing3, int notUsing4) {
		PVector pos = new PVector(), vel = new PVector();
		if (this.canFit) {
			for (String key : this.emilyDataList.keySet())
				pos.add(this.emilyDataList.get(key).getPos());
			pos.div((float) this.emilyDataList.size());
		} else {
			pos = this.emilyDataList.get(this.closestId).getPos().copy();
		}
		if (pos.dist(this.centroid) > 10)
			vel = pos.copy().sub(this.centroid)
					.setMag((float) Constants.UAV_RELATIVE_VELOCITY_FACTOR * Constants.EMILY_VELOCITY);
		else
			move = false;
		this.droneLoc.add(vel);
		this.drone.setLoc(this.droneLoc);
		if (logger.isDebugEnabled())
			logger.debug(
					"Moving UAV " + this.drone.getId() + " to " + pos.toString() + " at " + Float.toString(vel.mag()));
	}

	@Override
	public void updateUAVCameraTilt(Float notUsing) {
		if (this.drone.getMode() == UAV_MODES.TEST_METRICS_NO_TILT_ALGO
				|| this.drone.getMode() == UAV_MODES.TEST_METRICS_NO_TILT_RANDOM) {
			updateUAVPosition(0, 0, 0, 0);
			return;
		}
		PVector emilyPos = new PVector();
		if (this.canFit) {
			for (String key : this.emilyDataList.keySet())
				emilyPos.add(this.emilyDataList.get(key).getPos());
			emilyPos.div((float) this.emilyDataList.size());
		} else {
			emilyPos = this.emilyDataList.get(this.closestId).getPos().copy();
		}
		emilyPos.add(emilyPos.copy().sub(this.droneLoc).limit(EMILY_BOUNDARY));
		float minDist = this.droneLoc.dist(emilyPos);
		float tilt = (float) Math.atan(minDist / Inputs.UAV_HEIHT);
		float oTilt = (float) (Math.toDegrees(tilt) - Camera.ANGLE_FIX - Camera.VERTICAL_FOV);
		if (oTilt > Inputs.CAM_TILT_MAX && !move)
			move = true;
		if (move)
			oTilt = Inputs.CAM_TILT_MAX + 1;

		tilt = Math.min(Inputs.CAM_TILT_MAX, oTilt);
		if (logger.isDebugEnabled())
			logger.debug("Tilt Camera of " + this.drone.getId() + " to " + tilt);

		Camera cam = this.drone.getUavCam();
		if (this.drone.getUavCam().getAngle() <= tilt)
			cam.changeAngle(-CAMERA_TILT_SPEED);
		else
			cam.changeAngle(CAMERA_TILT_SPEED);
		this.drone.setUavCam(cam);

		if (move || this.canFit)
			updateUAVPosition(0, 0, 0, 0);
	}

	@Override
	public void updateUAVYaw(Float notUsing) {
		if (this.droneLoc.dist(centroid) > 1) {
			float uex = 0;
			float uey = 0;
			float uax = this.droneLoc.copy().sub(this.centroid).x;
			float uay = this.droneLoc.copy().sub(this.centroid).y;
			if (!canFit) {
				uex = this.emilyDataList.get(this.closestId).getPos().copy().sub(this.droneLoc).x;
				uey = this.emilyDataList.get(this.closestId).getPos().copy().sub(this.droneLoc).y;
			} else {
				for (String key : this.emilyDataList.keySet()) {
					uex += this.emilyDataList.get(key).getPos().x;
					uey += this.emilyDataList.get(key).getPos().y;
				}
				uex = uex / this.emilyDataList.size() - this.droneLoc.x;
				uey = uey / this.emilyDataList.size() - this.droneLoc.y;
			}

			float dot = uex * uax + uey * uay;
			float det = uex * uay - uey * uax;
			float angle = (float) (Math.atan2(det, dot) - Math.PI);
			if (angle > Math.PI)
				angle -= 2 * Math.PI;
			else if (angle < -Math.PI)
				angle += 2 * Math.PI;
			if (logger.isDebugEnabled())
				logger.debug("Rotate UAV(yaw) " + this.drone.getId() + " by " + Math.toDegrees(angle));
			if (Math.abs(Math.toDegrees(angle)) > 1)
				this.drone.changeYaw((float) (angle > 0 ? -CAMERA_YAW_SPEED : CAMERA_YAW_SPEED));
		}
	}

	@Override
	public void updateUAVCameraZoom(char key) {
		if (key == 'Z')
			this.drone.getUavCam().factorZoom(ZOOM_IN_FACTOR);
		else if (key == 'z')
			this.drone.getUavCam().factorZoom(ZOOM_OUT_FACTOR);
	}

	@Override
	public void getEMILYLocUpdate(String id, PVector pos, PVector goal) {
		this.drone.addEmily(id, pos, goal);
	}

	@Override
	public void nextStep() {
		// TODO add Case-1 - coverall(), Case-2 Check
		this.emilyDataList = this.drone.getEmilyDataList();
		if (!emilyDataList.isEmpty()) {
			this.droneLoc = this.drone.getLoc().copy();
			this.emilyDataList = this.drone.getEmilyDataList();
			this.droneLoc = this.drone.getLoc().copy();
			this.centroid = this.drone.getCentroidOfAOV().copy();
			this.canFit = coverall();
			if (!this.canFit) {
				findClosest();
				if (isEmilyInUavView()) {
					this.toggle++;
					if (!this.emilyDataList.get(this.closestId).getVisited()) {
						this.drone.updateEmilyVisited(this.closestId);
						this.numVisited++;
						logger.info(this.closestId + " is in the Area Of View of " + this.drone.getId());
					}
				} else
					this.drone.incTimeNotObservingEmily();
			}
			updateUAVYaw(null);
			updateUAVCameraTilt(null);
		}
		if (logger.isDebugEnabled())
			logger.debug("Drone data - " + this.drone.toString());
	}

	private void findClosest() {
		if (this.toggle == 0) {
			// if all Emilys are visited, then reset all Emilys visited
			if (this.numVisited == this.emilyDataList.keySet().size()) {
				this.drone.resetEmilyVisited();
				this.numVisited = 1;
				this.drone.updateEmilyVisited(this.closestId);
				logger.info("Resetting EMILYs all except " + this.closestId + " visited status");
				timer.schedule(new TimerTask() {
					String id = closestId;

					@Override
					public void run() {
						numVisited--;
						drone.resetEmilyVisited(this.id);
						logger.info("Resetting " + this.id + " visited status");
					}
				}, 50 * TIMER_COUNT * Inputs.OBSERVE_TIME);
				// Multiplication to sec
			}
			// get closest Emily
			float minDist = Float.MAX_VALUE;
			this.toggle = 1; // so that the loop is not entered multiple times
			PVector centroid = this.drone.getCentroidOfAOV();
			for (String emilyID : this.emilyDataList.keySet()) {
				PVector pos = this.emilyDataList.get(emilyID).getPos();
				boolean visited = this.emilyDataList.get(emilyID).getVisited();
				float dist = centroid.dist(pos);
				if (dist < minDist && !visited) {
					minDist = dist;
					this.closestId = emilyID;
				}
			}
			if (logger.isDebugEnabled())
				logger.debug(this.closestId + " is the closest target to " + this.drone.getId() + " "
						+ this.drone.getMode());
			if (this.drone.getMode() == UAV_MODES.TEST_METRICS_NO_TILT_RANDOM
					|| this.drone.getMode() == UAV_MODES.TEST_METRICS_WITH_TILT_RANDOM) {
				this.closestId = getRandomEmilyId();
				if (logger.isDebugEnabled())
					logger.debug(this.closestId + " is the next target to " + this.drone.getId() + " "
							+ this.drone.getMode() + ". Going towards it.");
			}
		} else if (this.toggle >= Inputs.OBSERVE_TIME) {
			logger.info("Observe Time of " + this.closestId + " is up. Observe next target " + this.drone.getId());
			this.toggle = -1;
		}
		if (logger.isDebugEnabled()) {
			logger.debug("Toggle count - " + Integer.toString(this.toggle));
			logger.debug("EMILYs Visited Count - " + Integer.toString(this.numVisited));
		}
	}

	private String getRandomEmilyId() {
		ArrayList<String> emilyIds = new ArrayList<String>();
		for (String emilyID : this.emilyDataList.keySet())
			if (!emilyDataList.get(emilyID).getVisited())
				emilyIds.add(emilyID);
		int rnd = new Random().nextInt(emilyIds.size());
		return emilyIds.get(rnd);
	}

	private boolean coverall() {
		// Create a temporary pseudo node, such that when viewing that all
		// EMILYs should be in view. It can be used for Case-3.
		// TODO: Optimize it further. compare dimensions in UAV view direction
		this.emilyDataList = this.drone.getEmilyDataList();
		float minX = Float.MAX_VALUE;
		float maxX = Float.MIN_VALUE;
		float minY = Float.MAX_VALUE;
		float maxY = Float.MIN_VALUE;
		for (String key : this.emilyDataList.keySet()) {
			PVector currPos = emilyDataList.get(key).getPos();
			if (currPos.x <= minX)
				minX = currPos.x;
			if (currPos.x >= maxX)
				maxX = currPos.x;
			if (currPos.y <= minY)
				minY = currPos.y;
			if (currPos.y >= maxY)
				maxY = currPos.y;
		}
		float dist1 = (float) Math.sqrt(Math.pow(maxX - minX, 2));
		float dist2 = (float) Math.sqrt(Math.pow(maxY - minY, 2));

		float[] dimensions = this.drone.getUavCam().maxDimensionsofAOV();
		boolean canFit = false;
		if (dist1 <= dimensions[0] && dist2 <= dimensions[1])
			canFit = true;
		return false; // return canFit;
	}

	private boolean isEmilyInUavView() {
		PVector[] boundingBoxVertices = this.drone.getBoundingBoxOfAOV();
		PVector pos = this.emilyDataList.get(this.closestId).getPos().copy();
		pos.add(pos.copy().sub(this.droneLoc).limit(EMILY_BOUNDARY));
		float angle = 0;
		for (int i = 0; i < boundingBoxVertices.length; i++) {
			angle += PVector.angleBetween(boundingBoxVertices[i].copy().sub(pos),
					boundingBoxVertices[(i + 1) % boundingBoxVertices.length].copy().sub(pos));
		}
		return (Math.abs(Math.toDegrees(angle - 2 * Math.PI)) <= EMILY_INSIDE_UAV_VIEW_ANGLE_BUFFER);
	}
}
