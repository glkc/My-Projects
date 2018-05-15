package simulation.processing.ui;

import processing.core.PApplet;

public class ProcessingTryout extends PApplet {

	public static void main(String[] args) {
		PApplet.main("simulation.processing.ui.ProcessingTryout");
	}

	float x = 0;
	float y = 100;
	float speed = 3;
	float prevMouseX = 0;
	float prevMouseY = 0;
	float MouseX = 0;
	float MouseY = 0;
	float inc = 0;

	public void settings() {
		size(1280, 800);
	}

	public void setup() {
		background(224, 255, 255);
		noStroke();
	}

	public void draw() {
		if (keyPressed) {
			float temp = 0;
			if (keyCode == UP) {
				temp = MouseY;
				MouseY = prevMouseY - speed;
				prevMouseY = temp;
			} else if (keyCode == DOWN) {
				temp = MouseY;
				MouseY = prevMouseY + speed;
				prevMouseY = temp;
			} else if (keyCode == LEFT) {
				temp = MouseX;
				MouseX = prevMouseX - speed;
				prevMouseX = temp;
			} else if (keyCode == RIGHT) {
				temp = MouseX;
				MouseX = prevMouseX + speed;
				prevMouseX = temp;
				noLoop();
			} else
				inc += 1;
		}
		display(prevMouseX, prevMouseY, MouseX, MouseY);
	}

	private void display(float xp, float yp, float mouseX, float mouseY) {
		background(224, 255, 255);
		fill(255);
		ellipse(100, 100, 30, 30);
		translate(100, 100);
		rotate(radians(inc));
		rect(mouseX, mouseY, 30, 10);
	}
}
