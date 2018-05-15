package simulation.processing.uav;

import processing.core.PVector;
import simulation.processing.parameters.Constants;

public class EmilyData {
	private String emilyId;
	private PVector pos;
	private PVector goal;
	private boolean visited;

	public EmilyData(String ID, PVector pos, PVector goal) {
		this.emilyId = ID;
		this.pos = pos;
		this.goal = goal;
		this.visited = false;
	}

	public Float getVelocityMag() {
		return this.goal.copy().sub(this.pos).setMag(Constants.EMILY_VELOCITY).mag();
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

	public boolean getVisited() {
		return this.visited;
	}

	public void setVisited(boolean visited) {
		this.visited = visited;
	}

	@Override
	public String toString() {
		StringBuilder builder = new StringBuilder();
		builder.append("EmilyData [emilyId=").append(emilyId).append(", pos=").append(pos).append(", goal=")
				.append(goal).append(", visited=").append(visited).append("]");
		return builder.toString();
	}
}
