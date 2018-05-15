package simulation.processing.uav;

import processing.core.PVector;

public class Manual implements UAVMechanics<Integer> {

	private UAV drone;

	public Manual(UAV uav) {
		this.drone = uav;
	}

	@Override
	public void updateUAVPosition(int pmouseX, int pmouseY, int mouseX, int mouseY) {
		drone.setLoc(drone.getLoc().copy().add(new PVector(mouseX - pmouseX, mouseY - pmouseY)));
	}

	@Override
	public void updateUAVCameraTilt(Integer keyCode) {
		Camera cam = drone.getUavCam();
		if (keyCode.intValue() == processing.core.PConstants.UP) {
			cam.changeAngle(-CAMERA_TILT_SPEED);
		} else if (keyCode.intValue() == processing.core.PConstants.DOWN) {
			cam.changeAngle(CAMERA_TILT_SPEED);
		}
		drone.setUavCam(cam);
	}

	@Override
	public void updateUAVYaw(Integer keyCode) {
		if (keyCode.intValue() == processing.core.PConstants.LEFT) {
			drone.changeYaw(-CAMERA_YAW_SPEED);
		} else if (keyCode.intValue() == processing.core.PConstants.RIGHT) {
			drone.changeYaw(CAMERA_YAW_SPEED);
		}
	}

	@Override
	public void updateUAVCameraZoom(char key) {
		if (key == 'Z')
			drone.getUavCam().factorZoom(ZOOM_IN_FACTOR);
		else if (key == 'z')
			drone.getUavCam().factorZoom(ZOOM_OUT_FACTOR);
	}

	@Override
	public void getEMILYLocUpdate(String id, PVector pos, PVector goal) {
		drone.addEmily(id, pos, goal);
	}

	@Override
	public void nextStep() {
	}
}
