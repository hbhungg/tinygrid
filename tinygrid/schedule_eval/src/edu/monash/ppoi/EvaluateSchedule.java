package edu.monash.ppoi;

public class EvaluateSchedule {

	public static void main(String[] args) {
    if (args[2].equals("1")) {
      Phase.P1.checkSchedule(args);
    } else {
      Phase.P2.checkSchedule(args);
    }
	}
}
