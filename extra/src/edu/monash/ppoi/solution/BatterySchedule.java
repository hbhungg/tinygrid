package edu.monash.ppoi.solution;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import edu.monash.ppoi.instance.Battery;
import edu.monash.ppoi.instance.Instance;

public class BatterySchedule {

	private final Battery battery;
	private final Map<Integer, Battery.Act> schedule;

	public BatterySchedule(Battery battery, Map<Integer, Battery.Act> schedule) {
		if (battery == null || schedule == null)
			throw new NullPointerException();

		this.battery = battery;
		this.schedule = new LinkedHashMap<>(schedule);
	}

	public Battery getBattery() {
		return battery;
	}

	public Battery.Act getAction(int time) {
		return schedule.getOrDefault(time, Battery.Act.HOLD);
	}

	@Override
	public String toString() {

		StringBuilder builder = new StringBuilder();

		for (Map.Entry<Integer, Battery.Act> step : schedule.entrySet()) {
			builder.append(Battery.LABEL);
			builder.append(" ");
			builder.append(battery.getBatteryID());
			builder.append(" ");
			builder.append(step.getKey());
			builder.append(" ");
			builder.append(step.getValue().ordinal());
			builder.append('\n');
		}
		
		return builder.toString();
	}

	public static List<BatterySchedule> parse(Instance instance, String[] lines, int lineNum) {

		// How many batteries to schedule?
		final int numBattery = instance.getAllBatteries().size();

		// Create battery schedules container.
		List<BatterySchedule> schedules = new ArrayList<>();

		// Create default schedules.
		List<Map<Integer, Battery.Act>> battSchedules = new ArrayList<>();
		for (int i = 0; i < numBattery; i++) {
			battSchedules.add(new LinkedHashMap<>());
		}

		for (int i = 0; lineNum < lines.length && i < numBattery; i++) {

			String[] parts = lines[lineNum].split(" ");
			int id = Integer.parseInt(parts[1]);
			
			do {
				if (parts.length != 4 || !Battery.LABEL.equals(parts[0])) {
					throw new RuntimeException("Unexpected format for battery.");
				}
				
				parts = lines[lineNum].split(" ");
				int batteryIDcheck = Integer.parseInt(parts[1]);
				int time = Integer.parseInt(parts[2]);
				Battery.Act action = Battery.Act.values()[Integer.parseInt(parts[3])];
	
				if (id != batteryIDcheck)
					break;
	
				battSchedules.get(id).put(time, action);
				lineNum++;
	
			} while (lineNum < lines.length);
		}

		// Instantiate schedule per battery.
		for (int id = 0; id < numBattery; id++) {
			schedules.add(new BatterySchedule(instance.getBattery(id), battSchedules.get(id)));
		}

		return schedules;
	}
}
