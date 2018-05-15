package simulation.processing.uav;

import processing.core.PVector;
import simulation.processing.parameters.Inputs;

public class Camera {

	private static final float ZOOM_MAX = 1;
	private static final float ZOOM_MIN = (float) 0.3;
	static final float HORIZINTAL_FOV = (float) 40.5;
	static final float VERTICAL_FOV = (float) 33;
	static final int ANGLE_FIX = 90;
	private float[][] boxCoordinates;
	private float tiltChange = 0;
	private float zoomFactor = 1;
	private float angle;

	public Camera(float angle) {
		super();
		this.angle = angle;
		getBoxCorners();
	}

	public float getAngle() {
		return this.angle;
	}

	public void changeAngle(float delta) {
		if (this.angle - delta <= Inputs.CAM_TILT_MAX && this.angle - delta >= Inputs.CAM_TILT_MIN) {
			this.angle -= delta;
			this.tiltChange += Math.abs(delta);
			getBoxCorners();
		}
	}

	public float getTiltChange() {
		return this.tiltChange;
	}

	private void getBoxCorners() {
		// 4:3 -> 81 degrees horizontal and 66 degrees vertical
		float w = (float) (Inputs.UAV_HEIHT * Math.tan(Math.toRadians(HORIZINTAL_FOV)));
		float s = (float) (Inputs.UAV_HEIHT * Math.tan(Math.toRadians(this.angle + ANGLE_FIX)));
		float h1 = (float) (Inputs.UAV_HEIHT * Math.tan(Math.toRadians(VERTICAL_FOV - this.angle + ANGLE_FIX)));
		float h2 = (float) (Inputs.UAV_HEIHT * Math.tan(Math.toRadians(-VERTICAL_FOV - this.angle + ANGLE_FIX)));
		this.boxCoordinates = new float[][] { { w, h1 }, { w + s, h2 }, { -w - s, h2 }, { -w, h1 } };
		// top right, bottom right, bottom left, top left - order of vertices
		changeBoundingBox(zoomFactor);
	}

	public float[][] getBoxCoordinates() {
		return this.boxCoordinates;
	}

	public void factorZoom(float delta) {
		if ((this.zoomFactor * delta < ZOOM_MAX && delta > 1) || (this.zoomFactor * delta > ZOOM_MIN && delta < 1)) {
			this.zoomFactor *= delta;
			changeBoundingBox(delta);
		}
	}

	private void changeBoundingBox(double delta) {
		float[][] oldCoordinates = this.boxCoordinates;
		this.boxCoordinates[0] = updateCorner(oldCoordinates[0], oldCoordinates[2], delta);
		this.boxCoordinates[1] = updateCorner(oldCoordinates[1], oldCoordinates[3], delta);
		this.boxCoordinates[2] = updateCorner(oldCoordinates[2], oldCoordinates[0], delta);
		this.boxCoordinates[3] = updateCorner(oldCoordinates[3], oldCoordinates[1], delta);
	}

	private float[] updateCorner(float[] p1, float[] p2, double change) {
		float[] point = { 0, 0 };
		point[0] = (float) (change * p1[0]);
		point[1] = p1[1] + ((p1[1] - p2[1]) / (p1[0] - p2[0])) * (point[0] - p1[0]);
		return point;
	}

	public PVector getCentroidOfAOV() {
		float x = 0;
		float y = 0;
		for (int i = 0; i < boxCoordinates.length; i++) {
			for (int j = 0; j < boxCoordinates[i].length; j++) {
				if (j == 0) {
					x += boxCoordinates[i][j];
				} else {
					y += boxCoordinates[i][j];
				}
			}
		}
		return new PVector(x / (float) boxCoordinates.length, y / (float) boxCoordinates.length);
	}

	@Override
	public String toString() {
		StringBuilder builder = new StringBuilder();
		builder.append("Camera [tiltChange=").append(tiltChange).append(", zoomFactor=").append(zoomFactor)
				.append(", angle=").append(angle).append("]");
		return builder.toString();
	}

	public float[] maxDimensionsofAOV() {
		// returns width, height dimension at max view of AOV
		float w = (float) (Inputs.UAV_HEIHT * Math.tan(Math.toRadians(HORIZINTAL_FOV)));
		float s = (float) (Inputs.UAV_HEIHT * Math.tan(Math.toRadians(Inputs.CAM_TILT_MAX + ANGLE_FIX)));
		float h1 = (float) (Inputs.UAV_HEIHT
				* Math.tan(Math.toRadians(VERTICAL_FOV - Inputs.CAM_TILT_MAX + ANGLE_FIX)));
		float h2 = (float) (Inputs.UAV_HEIHT
				* Math.tan(Math.toRadians(-VERTICAL_FOV - Inputs.CAM_TILT_MAX + ANGLE_FIX)));
		PVector p1 = new PVector(w, h1);
		PVector p2 = new PVector(w + s, h2);
		PVector p3 = new PVector(-w - s, h2);
		float dis1 = p2.dist(p3);
		float dis2 = p1.dist(p2);
		return new float[] { dis1, dis2 };
	}
}
