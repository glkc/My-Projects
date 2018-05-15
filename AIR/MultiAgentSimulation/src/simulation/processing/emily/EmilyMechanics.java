package simulation.processing.emily;

public class EmilyMechanics {
	private Emily emily;

	public EmilyMechanics(Emily emily) {
		this.emily = emily;
	}

	public void updateEmilyLoc() {
		emily.incVel();
		emily.updatePos();
		if (emily.atGoal())
			emily.zeroVelocity();
	}
}
