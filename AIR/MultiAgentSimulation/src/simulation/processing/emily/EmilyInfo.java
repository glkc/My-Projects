package simulation.processing.emily;

import processing.core.PVector;

public class EmilyInfo {
	private String emilyId;
	private PVector pos;
	private PVector goal;

	public EmilyInfo(String ID, PVector pos, PVector goal) {
		this.emilyId = ID;
		this.pos = pos;
		this.goal = goal;
	}

	public PVector getPos() {
		return this.pos;
	}

	public String getID() {
		return this.emilyId;
	}

	public PVector getGoal() {
		return this.goal;
	}

	public void setPos(PVector pos) {
		this.pos = pos;
	}

	@Override
	public String toString() {
		StringBuilder builder = new StringBuilder();
		builder.append("EmilyInfo [emilyId=").append(emilyId).append(", pos=").append(pos).append(", goal=")
				.append(goal).append("]");
		return builder.toString();
	}
}
