package edu.monash.ppoi.checker;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import edu.monash.io.tsf.TimeSeriesDB;
import edu.monash.ppoi.instance.Building;
import edu.monash.ppoi.instance.Instance;
import edu.monash.ppoi.instance.OnceOff;
import edu.monash.ppoi.instance.Recurring;
import edu.monash.ppoi.solution.BatterySchedule;
import edu.monash.ppoi.solution.Schedule;

public class ScheduleChecker implements IScheduleChecker {

	private static final Double peakTariff = 0.005;

	private final RoomUsage roomUsage;
	private final List<Double> baseload;
	private final List<Double> prices;
	private final List<BatteryCheck> batteryChecks;
	private final ActivityScheduleCheck<OnceOff> onceoffCheck;
	private final ActivityScheduleCheck<Recurring> recurringCheck;

	private final boolean isValid;
	private final double[] sumload;

	public ScheduleChecker(TimeSeriesDB db, Schedule schedule, List<Double> prices, DateHandler date) {

		// Get the instance to discover which loads are 'active'.
		Instance instance = schedule.getInstance();

		// Get base load.
		this.baseload = getBaseLoad(db, instance, date);
		this.prices = new ArrayList<>(prices);

		// Create room usage tracker.
		roomUsage = new RoomUsage(instance, date.getHorizon());

		// Check the battery schedules.
		batteryChecks = new ArrayList<>();
		for (BatterySchedule battSchedule : schedule.getBatterySchedule()) {
			batteryChecks.add(new BatteryCheck(battSchedule, date.getHorizon()));
		}
		
		// Check the precedences.
		onceoffCheck = new ActivityScheduleCheck<OnceOff>(date, roomUsage, instance.getAllOnceOff(), schedule.getOnceOffSchedule());
		recurringCheck = new ActivityScheduleCheck<Recurring>(date, roomUsage, instance.getAllRecurring(), schedule.getRecurringSchedule());

		// Check full schedule validity.
		isValid = checkAllValid();
		sumload = accumulateLoads();
	}


	public double getObjective() {
		return isValid() ? getScore() : Double.NaN;
	}

	public double getScore() {
		return getEnergyCost() + getPeakCost() - getOnceOffProfit();
	}

	public double getEnergyCost() {

		double sumCost = 0d;
		
		for (int t = 0; t < baseload.size(); t++) {
			
			double load = getTotalLoad(t);
			double cost = 0.001d * load * 900d / 3600d * prices.get(t);
			
			sumCost += cost;
		}
		
		return sumCost;
	}

	public double getPeakCost() {

		double maxLoad = 0d;
		for (int t = 0; t < sumload.length; t++)
			maxLoad = Math.max(maxLoad, getTotalLoad(t));

		return peakTariff * maxLoad * maxLoad;
	}

	public double getOnceOffProfit() {
		return onceoffCheck.getValue();
	}

	public boolean isValid() {
		return isValid;
	}

	public double getBaseLoad(int t) {
		return baseload.get(t);
	}

	public double getScheduleLoad(int t) {
		return getTotalLoad(t) - getBaseLoad(t);
	}

	public double getTotalLoad(int t) {
		return sumload[t];
	}

	private boolean checkAllValid() {

		boolean isValid = true;
	
		isValid = isValid && roomUsage.isValid();
		isValid = isValid && onceoffCheck.isValid();
		isValid = isValid && recurringCheck.isValid();
		
		for (BatteryCheck check : batteryChecks) {
			isValid = isValid && check.isValid();
		}

		return isValid;
	}

	private double[] accumulateLoads() {

		double[] sumload = new double[baseload.size()];

		// Base load.
		for (int i = 0; i < baseload.size(); i++) {
			sumload[i] += baseload.get(i);
		}

		// Battery load.
		for (BatteryCheck check : batteryChecks) {
			accumulate(sumload, check.getPowerKW());
		}

		// Activity load.
		accumulate(sumload, onceoffCheck.getPowerKW());
		accumulate(sumload, recurringCheck.getPowerKW());
		
		return sumload;
	}

	private static void accumulate(double[] accumulator, double[] values) {
		for (int i = 0; i < accumulator.length; i++) {
			accumulator[i] += values[i];
		}
	}

	public static List<Double> getBaseLoad(TimeSeriesDB db, Instance instance, DateHandler date) {

		// Collect all active building series.
		Map<Building, List<Double>> buildingLoad = new LinkedHashMap<>();
		for (Building building : instance.getAllBuildings())
			buildingLoad.put(building, building.getBaseLoad(db, date.getStart(), date.getDuration()));

		return combine(buildingLoad);
	}

	public static List<Double> combine(Map<Building, List<Double>> buildingLoad) {

		List<Double> baseload = new ArrayList<>();
		
		int step = 0;
		while (true) {
			
			double sumLoad = 0;
			
			for (List<Double> entry : buildingLoad.values()) {
				if (step >= entry.size())
					return baseload;
				
				sumLoad += entry.get(step);
			}

			baseload.add(sumLoad);
			step = step + 1;
		}
	}
}
