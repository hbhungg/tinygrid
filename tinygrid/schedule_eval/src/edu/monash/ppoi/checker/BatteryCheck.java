package edu.monash.ppoi.checker;

import edu.monash.ppoi.instance.Battery;
import edu.monash.ppoi.solution.BatterySchedule;

public class BatteryCheck {

	private final double[] powerKW;
	private final boolean valid;

	public BatteryCheck(BatterySchedule schedule, int horizon) {

		this.powerKW = new double[horizon];
		this.valid = evaluateSchedule(schedule, horizon);
	}

	public double[] getPowerKW() {
		return powerKW;
	}

	public boolean isValid() {
		return valid;
	}

	private boolean evaluateSchedule(BatterySchedule schedule, int horizon) {

		Battery battery = schedule.getBattery();

		// Track schedule validity.
		boolean valid = true;
		
		// Battery starts full.
		double state = battery.getCapacityKWh();

		for (int time = 0; time < horizon; time++) {

			// Determine action.
			Battery.Act action = schedule.getAction(time);

			// Determine load on grid.
			this.powerKW[time] = battery.getLoadKW(action);

			// Determine change in power.
			state += battery.getEnergyKWh(action, 15d/60d);
			if (state < 0 || state > battery.getCapacityKWh())
				valid = false;
		}

		return valid;
	}
}
