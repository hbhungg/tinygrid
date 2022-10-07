package edu.monash.ppoi.checker;

import java.util.List;

import edu.monash.ppoi.instance.Activity;
import edu.monash.ppoi.instance.OnceOff;
import edu.monash.ppoi.instance.Recurring;
import edu.monash.ppoi.solution.ActivitySchedule;

@SuppressWarnings("rawtypes")
public class ActivityScheduleCheck<A extends Activity> {

	private final boolean isRecurring;

	private final double[] powerKW;
	private final boolean valid;
	private final int value;

	private final boolean[] scheduled;
	private final boolean[] workHours;
	private final int[] startDay;

	public ActivityScheduleCheck(IDateHandler date, RoomUsage usage, List<A> activities, List<? extends ActivitySchedule> schedule) {

		this.isRecurring = isRecurring(activities);
		this.scheduled = new boolean[activities.size()];
		this.workHours = new boolean[activities.size()];
		this.startDay = new int[activities.size()];

		this.valid = evaluateSchedule(date, activities, schedule);
		this.powerKW = accumulateScheduleLoad(date, usage, schedule);
		this.value = accumulateValue(activities);
	}

	private boolean isRecurring(List<A> activities) {
		return (activities.get(0) instanceof Recurring);
	}

	public double[] getPowerKW() {
		return powerKW;
	}

	public boolean isValid() {
		return valid;
	}

	public int getValue() {
		return value;
	}

	private boolean evaluateSchedule(IDateHandler date, List<A> activities, List<? extends ActivitySchedule> schedule) {

		// Determine the full set of activity precedences.
		List<List<Integer>> fullPrecedences = Activity.getPrecedenceClosure(activities);

		// Track which activities are scheduled when.
		for (ActivitySchedule<?> item : schedule) {
			
			int id = item.getActivityID();

			scheduled[id] = true;
			startDay[id] = date.getDay(item.getStartTime());
			workHours[id] = date.isWorkingHours(item.getStartTime(), activities.get(id).getDuration()-1);
		}

		// Check that all precedences j <- i are respected for every scheduled activity.
		boolean valid = true;
		for (int i = 0; i < activities.size(); i++)
			if (scheduled[i])
				for (int j : fullPrecedences.get(i))
					valid = valid && scheduled[j] && (startDay[j] < startDay[i]);

		// Make sure that all recurring activities are scheduled in work hours.
		if (isRecurring)
			valid = valid && allTrue(scheduled) && allTrue(workHours);

		return valid;
	}

	private double[] accumulateScheduleLoad(IDateHandler date, RoomUsage usage, List<? extends ActivitySchedule> activities) {
		return isRecurring ?
			   accumulateRecurring(date, usage, activities) :
			   accumulateOnceOff(date, usage, activities);
	}

	private double[] accumulateRecurring(IDateHandler date, RoomUsage usage, List<? extends ActivitySchedule> schedule) {

		double[] powerKW = new double[date.getHorizon()];

		for (ActivitySchedule<?> scheduled : schedule) {

			Recurring activity = (Recurring) scheduled.getActivity();
			// Determine period during the day.
			for (int start : date.getRecurring(scheduled.getStartTime())) {
				
				// Accumulate room usage.
				usage.scheduleActivity(activity, start, scheduled.getBuildings());

				for (int time = 0; time < activity.getDuration(); time++) {
					powerKW[start + time] += activity.getNumRooms() * activity.getLoadkW();
				}
			}
		}

		return powerKW;
	}

	private double[] accumulateOnceOff(IDateHandler date, RoomUsage usage, List<? extends ActivitySchedule> schedule) {
		
		double[] powerKW = new double[date.getHorizon()];

		for (ActivitySchedule<?> scheduled : schedule) {

			// Accumulate room usage.
			usage.scheduleActivity(scheduled);

			// Accumulate power usage.
			OnceOff activity = (OnceOff) scheduled.getActivity();
			for (int time = scheduled.getStartTime(); time < scheduled.getEndTime(); time++) {
				powerKW[time] += activity.getNumRooms() * activity.getLoadkW();
			}
		}

		return powerKW;
	}

	@SuppressWarnings("unchecked")
	private int accumulateValue(List<A> activities) {
		return !isRecurring ? accumulateOnceOff((List<OnceOff>) activities) : 0;
	}

	private int accumulateOnceOff(List<OnceOff> activities) {

		int value = 0;

		for (OnceOff activity : activities) {
			int i = activity.getID();
			if (scheduled[i]) {
				value += activity.getValue() - (!workHours[i] ? activity.getOutOfOfficePenalty() : 0);
			}
		}

		return value;
	}

	private static boolean allTrue(boolean[] values) {
		
		boolean all = true;
		
		for (int i = 0; all && i < values.length; i++)
			all &= values[i];
		
		return all;
	}
}
