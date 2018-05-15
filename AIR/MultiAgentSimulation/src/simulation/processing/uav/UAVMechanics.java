package simulation.processing.uav;

import processing.core.PVector;

public interface UAVMechanics<T> {

	static final float CAMERA_TILT_SPEED = (float) 1;
	static final float CAMERA_YAW_SPEED = (float) 2;
	static final float ZOOM_IN_FACTOR = (float) 1.1;
	static final float ZOOM_OUT_FACTOR = (float) 0.9;
	static final int TIMER_COUNT = 1;

	public void updateUAVPosition(int curLocX, int curLocY, int toLocX, int toLocY);

	public void updateUAVCameraTilt(T deltaAngle);

	public void updateUAVYaw(T deltaAngle);

	public void updateUAVCameraZoom(char zoomFactor);

	public void getEMILYLocUpdate(String id, PVector pos, PVector goal);

	public void nextStep();

}
