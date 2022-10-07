package edu.monash.ppoi.solution;

import java.util.ArrayList;
import java.util.List;

import edu.monash.ppoi.instance.Instance;
import edu.monash.ppoi.instance.Recurring;

public class RecurringSchedule extends ActivitySchedule<Recurring> {

	public RecurringSchedule(Recurring activity, int start, List<Integer> rooms) {
		super(activity, start, rooms);
	}

	public static RecurringSchedule parse(Instance instance, String line) {
		
		String[] parts = line.split(" ");
		if (parts.length < 5 || !Recurring.LABEL.equals(parts[0])) {
			throw new RuntimeException("Unexpected format for recurring activity.");
		}

		int id = Integer.parseInt(parts[1]);
		int start = Integer.parseInt(parts[2]);

		Recurring activity = instance.getRecurring(id);
		
		int numRooms = Integer.parseInt(parts[3]);
		if (numRooms != activity.getNumRooms())
			throw new RuntimeException("Number of rooms scheduled does not match the number in activity");

		List<Integer> rooms = new ArrayList<>();
		for (int i = 0; i < numRooms; i++) {
			rooms.add(Integer.parseInt(parts[4+i]));
		}

		return new RecurringSchedule(activity, start, rooms);
	}
}
