package edu.monash.ppoi.solution;

import java.util.ArrayList;
import java.util.List;

import edu.monash.ppoi.instance.Instance;
import edu.monash.ppoi.instance.OnceOff;

public class OnceOffSchedule extends ActivitySchedule<OnceOff> {

	public OnceOffSchedule(OnceOff activity, int start, List<Integer> rooms) {
		super(activity, start, rooms);
	}

	public static OnceOffSchedule parse(Instance instance, String line) {
		
		String[] parts = line.split(" ");
		if (parts.length < 5 || !OnceOff.LABEL.equals(parts[0])) {
			throw new RuntimeException("Unexpected format for once-off activity.");
		}

		int id = Integer.parseInt(parts[1]);
		int start = Integer.parseInt(parts[2]);

		OnceOff activity = instance.getOnceOff(id);
		
		int numRooms = Integer.parseInt(parts[3]);
		if (numRooms != activity.getNumRooms())
			throw new RuntimeException("Number of rooms scheduled does not match the number in activity");

		List<Integer> rooms = new ArrayList<>();
		for (int i = 0; i < numRooms; i++) {
			rooms.add(Integer.parseInt(parts[4+i]));
		}

		return new OnceOffSchedule(activity, start, rooms);
	}
}
