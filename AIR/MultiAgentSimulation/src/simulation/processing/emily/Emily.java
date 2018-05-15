package simulation.processing.emily;

import java.util.Arrays;

import processing.core.PApplet;
import processing.core.PVector;
import simulation.processing.parameters.Constants;

public class Emily extends PApplet {

	private int[] color;
	private PVector vel;
	private PVector acce;
	private PVector initPos;
	private EmilyMechanics mechanisms;
	private EmilyInfo info;

	public Emily(String id, PVector pos, PVector goal) {
		this.initPos = pos.copy();
		this.info = new EmilyInfo(id, pos, goal);
		this.vel = goal.copy().sub(pos).setMag(Constants.EMILY_VELOCITY);
		this.acce = new PVector(0, 0, 0);
		this.mechanisms = new EmilyMechanics(this);
		this.color = new int[] { (int) random(255), (int) random(255), (int) random(255) };
	}

	public PVector getInitPos() {
		return initPos;
	}

	public PVector getPos() {
		return info.getPos();
	}

	public void updatePos() {
		PVector pos = this.info.getPos();
		pos.add(this.vel);
		this.info.setPos(pos);
	}

	public EmilyMechanics getMechanisms() {
		return mechanisms;
	}

	public PVector getGoal() {
		return info.getGoal();
	}

	public PVector getVel() {
		return vel;
	}

	public void incVel() {
		this.vel.add(this.acce);
	}

	public EmilyInfo getInfo() {
		return info;
	}

	public int[] getColor() {
		return color;
	}

	public boolean atGoal() {
		if (Math.abs(this.info.getPos().x - this.info.getGoal().x) < 1
				&& Math.abs(this.info.getPos().y - this.info.getGoal().y) < 1)
			return true;
		return false;
	}

	public void zeroVelocity() {
		this.vel = new PVector(0, 0, 0);
	}

	@Override
	public String toString() {
		StringBuilder builder = new StringBuilder();
		builder.append("Emily [color=").append(Arrays.toString(color)).append(", info=").append(info).append(", vel=")
				.append(vel).append(", vel Magnitude=").append(Float.toString(vel.mag())).append(", acce=").append(acce)
				.append(", initPos=").append(initPos).append("]");
		return builder.toString();
	}
}
