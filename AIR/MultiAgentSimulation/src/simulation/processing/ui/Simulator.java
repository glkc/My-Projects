package simulation.processing.ui;

import java.util.ArrayList;
import java.util.Timer;
import java.util.TimerTask;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import processing.core.PApplet;
import processing.core.PImage;
import processing.core.PVector;
import simulation.processing.emily.Emily;
import simulation.processing.parameters.Constants;
import simulation.processing.parameters.Inputs;
import simulation.processing.parameters.UAV_MODES;
import simulation.processing.uav.UAV;

public class Simulator extends PApplet {
	private static final int[] CANVAS_BACKGROUND = new int[] { 200, 255, 255 }; // Cyan
	private static final int[] quesImgCorners = new int[] { Inputs.SIMULATOR_SIZE[0] - 25, 0, Inputs.SIMULATOR_SIZE[0],
			25 };
	private static final int STOP_TIME_MIN = 1;
	private static final int UPDATE_RATE = 15;
	private static PImage quesImg;
	private static Logger logger;
	private static Integer timeToStop = 0;
	private static UAV_MODES mode;
	private static boolean showInstructions = false;
	private static String TRIAL_RUN_ID = "0";
	private static String TEST_RUN_ID = "0";
	private static String CASE_RUN_ID = "0";
	private static String SAVE_DATA_PATH = Inputs.DATA_COLLECTION_PATH;
	private static int TIME_DELAY = 1000 * 60 * 2;

	private static final int UAV_SIZE = 10;
	private static final int EMILY_SIZE = 5;
	private static ArrayList<PVector> newEmilyLoc = new ArrayList<PVector>();
	private static ArrayList<Emily> emilys = new ArrayList<Emily>();
	private static boolean addEmily = false;
	private UAV drone;

	public static void main(String[] args) {
		if (args.length > 3) {
			TRIAL_RUN_ID = args[0];
			Inputs.UAV_MODE = UAV_MODES.valueOf(Integer.parseInt(args[1]));
			CASE_RUN_ID = args[2];
			TEST_RUN_ID = args[3];
		}
		mode = Inputs.UAV_MODE;
		SAVE_DATA_PATH += TRIAL_RUN_ID + "/" + Inputs.UAV_MODE + "/" + Constants.CASE_ID + CASE_RUN_ID + "/"
				+ Constants.TEST_ID + TEST_RUN_ID;
		System.setProperty("logFilename", SAVE_DATA_PATH + "/simulation.log");
		logger = LogManager.getLogger(Simulator.class.getName());
		PApplet.main("simulation.processing.ui.Simulator");
	}

	public void settings() {
		size(Inputs.SIMULATOR_SIZE[0], Inputs.SIMULATOR_SIZE[1]);
	}

	public void setup() {
		background(CANVAS_BACKGROUND[0], CANVAS_BACKGROUND[1], CANVAS_BACKGROUND[2]);
		noStroke();
		quesImg = loadImage("ques.jpeg");
		logger.info("Initiating simulation - " + Constants.TEST_ID + TEST_RUN_ID + " of " + Constants.CASE_ID
				+ CASE_RUN_ID + " with UAV mode - " + Inputs.UAV_MODE.name());
		drone = new UAV(new PVector(Inputs.UAV_INITIAL_POSITION[0], Inputs.UAV_INITIAL_POSITION[1]), Inputs.UAV_MODE);
		addEmilysForTest();
	}

	@SuppressWarnings("unchecked")
	public void draw() {
		background(CANVAS_BACKGROUND[0], CANVAS_BACKGROUND[1], CANVAS_BACKGROUND[2]);
		imageMode(CORNERS);
		image(quesImg, quesImgCorners[0], quesImgCorners[1], quesImgCorners[2], quesImgCorners[3]);

		drawEmily();
		drawUAV();
		sendCommunication();
		showInstructions();
		if (frameCount % Inputs.SCREEN_SHOT_RATE == 0)
			saveFrame(SAVE_DATA_PATH + "/ScreenShot-######.jpeg");
		if (mode == UAV_MODES.MANUAL) {
			if (keyPressed)
				if (keyCode == UP || keyCode == DOWN)
					drone.getMechanisms().updateUAVCameraTilt(keyCode);
				else if (keyCode == LEFT || keyCode == RIGHT)
					drone.getMechanisms().updateUAVYaw(keyCode);
				else if (key == 'Z' || key == 'z')
					// 'z' for ZoomIN and 'Z' for ZoomOUT
					drone.getMechanisms().updateUAVCameraZoom(key);
		} else {
			drone.getMechanisms().nextStep();
			if (drone.allEmilysAtGoal())
				timeToStop += 1;
			else
				timeToStop = 0;
			if (timeToStop > 60 * 60 * STOP_TIME_MIN) { // @60fps
				logger.info("All EMILYs are at goal. Simulation Done. Ending Simulation.");
				drone.getAllMetrics();
				exit();
			}
		}
	}

	public void keyPressed() {
		if (keyCode == 'a' || keyCode == 'A') {
			drone.setUAVMode(UAV_MODES.AUTOMATIC_OBSERVATION);
			mode = UAV_MODES.AUTOMATIC_OBSERVATION;
		} else if (keyCode == 'm' || keyCode == 'M') {
			drone.setUAVMode(UAV_MODES.MANUAL);
			mode = UAV_MODES.MANUAL;
		} else if ((keyCode == 'e' || keyCode == 'E') && Simulator.mode == UAV_MODES.MANUAL) {
			addEmily = true;
		}
	}

	public void mouseClicked() {
		if (addEmily) {
			newEmilyLoc.add(new PVector(mouseX, mouseY));
			if (newEmilyLoc.size() == 2) {
				String emilyId = "EMILY" + emilys.size();
				emilys.add(new Emily(emilyId, newEmilyLoc.get(0), newEmilyLoc.get(1)));
				logger.info("Adding " + emilyId + " at " + newEmilyLoc.get(0).toString() + " heading towards "
						+ newEmilyLoc.get(1).toString());
				addEmily = false;
				newEmilyLoc.clear();
			}
		} else if (mouseX > quesImgCorners[0] && mouseX < quesImgCorners[2] && mouseY > quesImgCorners[1]
				&& mouseY < quesImgCorners[3]) {
			showInstructions = !showInstructions;
		}
	}

	public void mouseDragged() {
		if (mode == UAV_MODES.MANUAL)
			drone.getMechanisms().updateUAVPosition(pmouseX, pmouseY, mouseX, mouseY);
	}

	private void drawUAV() {
		pushMatrix();
		translate(drone.getLoc().x, drone.getLoc().y);
		rotate(radians(drone.getYaw()));

		fill(255, 255, 0, 100); // YELLOW @opacity - 100/255
		beginShape();
		float[][] box = drone.getUavCam().getBoxCoordinates();
		for (int i = 0; i < box.length; i++)
			vertex(box[i]);
		endShape(CLOSE);

		stroke(255, 255, 0);
		for (int i = 0; i < box.length; i++)
			line(0, 0, box[i][0], box[i][1]);
		noStroke();

		popMatrix();
		fill(0, 0, 255); // DARK BLUE
		ellipseMode(CENTER);
		ellipse(drone.getLoc().x, drone.getLoc().y, UAV_SIZE, UAV_SIZE);
	}

	private void drawEmily() {
		for (Emily emily : emilys) {
			stroke(emily.getColor()[0], emily.getColor()[1], emily.getColor()[2]);
			line(emily.getInitPos().x, emily.getInitPos().y, emily.getPos().x, emily.getPos().y);
			noStroke();
			PVector direction = emily.getVel().copy();
			float theta = direction.heading() + radians(90);
			pushMatrix();
			translate(emily.getPos().x, emily.getPos().y);
			rotate(theta);
			fill(255, 0, 0);
			beginShape(TRIANGLES);
			vertex(0, -EMILY_SIZE * 2);
			vertex(-EMILY_SIZE, EMILY_SIZE * 2);
			vertex(EMILY_SIZE, EMILY_SIZE * 2);
			endShape();
			popMatrix();
			emily.getMechanisms().updateEmilyLoc();
			if (logger.isDebugEnabled())
				logger.debug(emily.toString());
		}
	}

	private void sendCommunication() {
		for (Emily emily : emilys) {
			drone.getMechanisms().getEMILYLocUpdate(emily.getInfo().getID(), emily.getPos(), emily.getGoal());
			if (frameCount % UPDATE_RATE == 0)
				arrow(emily.getPos().x, emily.getPos().y, drone.getLoc().x, drone.getLoc().y);
		}
	}

	private void addEmilysForTest() {
		for (int i = 0; i < Inputs.START_POSITIONS.get(Constants.CASE_ID + CASE_RUN_ID).length; i++) {
			if (Integer.parseInt(CASE_RUN_ID) == 6 && i > 2)
				break;
			String id = "EMILY-" + java.util.UUID.randomUUID().toString();
			PVector startPoint = new PVector(Inputs.START_POSITIONS.get(Constants.CASE_ID + CASE_RUN_ID)[i][0],
					Inputs.START_POSITIONS.get(Constants.CASE_ID + CASE_RUN_ID)[i][1]);
			PVector goalPoint = new PVector(Inputs.GOAL_POSITIONS.get(Constants.CASE_ID + CASE_RUN_ID)[i][0],
					Inputs.GOAL_POSITIONS.get(Constants.CASE_ID + CASE_RUN_ID)[i][1]);
			emilys.add(new Emily(id, startPoint, goalPoint));
			logger.info("Adding " + id + " at " + startPoint + " heading towards " + goalPoint);
		}
		if (Integer.parseInt(CASE_RUN_ID) == 6) {
			Timer timer = new Timer();
			timer.schedule(new TimerTask() {
				@Override
				public void run() {
					for (int i = 3; i < Inputs.START_POSITIONS.get(Constants.CASE_ID + CASE_RUN_ID).length; i++) {
						String id = "EMILY-" + java.util.UUID.randomUUID().toString();
						PVector startPoint = new PVector(
								Inputs.START_POSITIONS.get(Constants.CASE_ID + CASE_RUN_ID)[i][0],
								Inputs.START_POSITIONS.get(Constants.CASE_ID + CASE_RUN_ID)[i][1]);
						PVector goalPoint = new PVector(
								Inputs.GOAL_POSITIONS.get(Constants.CASE_ID + CASE_RUN_ID)[i][0],
								Inputs.GOAL_POSITIONS.get(Constants.CASE_ID + CASE_RUN_ID)[i][1]);
						emilys.add(new Emily(id, startPoint, goalPoint));
						logger.info("Adding " + id + " at " + startPoint + " heading towards " + goalPoint);
					}
				}
			}, TIME_DELAY);
		}
	}

	private void showInstructions() {
		if (mode == UAV_MODES.MANUAL || mode == UAV_MODES.AUTOMATIC_OBSERVATION) {
			String display = Constants.GENERAL_QUERY_TEXT;
			fill(255);
			if (mode == UAV_MODES.MANUAL)
				display += " " + Constants.MANUAL_QUERY_TEXT;
			if (showInstructions)
				text(display, Inputs.SIMULATOR_SIZE[0] - 300, 25, 300, 100);
		}
	}

	private void arrow(float x1, float y1, float x2, float y2) {
		stroke(0, 255, 0);
		strokeWeight(2);
		line(x1, y1, x2, y2);
		pushMatrix();
		translate(x2, y2);
		float a = atan2(x1 - x2, y2 - y1);
		rotate(a);
		line(0, 0, -10, -10);
		line(0, 0, 10, -10);
		popMatrix();
		noStroke();
	}
}
