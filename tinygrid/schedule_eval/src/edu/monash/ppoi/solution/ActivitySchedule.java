package edu.monash.ppoi.solution;

import java.util.ArrayList;
import java.util.List;

import edu.monash.ppoi.instance.Activity;

public abstract class ActivitySchedule<T extends Activity> implements Comparable<ActivitySchedule<T>> {

	private final T activity;
	private final int startTime;
	private final int endTime;
	private final List<Integer> buildingRooms;

	public ActivitySchedule(T activity, int start, List<Integer> rooms) {
		
		if (activity == null || rooms == null)
			throw new NullPointerException("Null argument provided " + activity + ", " + rooms);
		if (start < 0)
			throw new IllegalArgumentException("Start cannot be < 0.");
		if (rooms.size() != activity.getNumRooms())
			throw new IllegalArgumentException("Schedule rooms != num rooms");

		this.activity = activity;
		this.startTime = start;
		this.endTime = start + this.activity.getDuration();
		this.buildingRooms = new ArrayList<>(rooms);
	}

	public T getActivity() {
		return activity;
	}
	
	public int getActivityID() {
		return activity.getID();
	}

	public int getStartTime() {
		return startTime;
	}

	public int getEndTime() {
		return endTime;
	}

	public List<Integer> getBuildings() {
		return buildingRooms;
	}

	public int compareTo(ActivitySchedule<T> that) {
		
		int startDiff = this.getStartTime() - that.getStartTime();
		int idDiff = this.getActivityID() - that.getActivityID();
		
		return startDiff != 0 ? startDiff : idDiff;
	}

	@Override
	public String toString() {

		StringBuilder builder = new StringBuilder();

		builder.append(getActivity().getActivityLabel());
		builder.append(" ");
		builder.append(getActivityID());
		builder.append(" ");
		builder.append(getStartTime());
		builder.append(" ");
		builder.append(getBuildings().size());
		for (int building : getBuildings()) {
			builder.append(" ");
			builder.append(building);
		}
		
		builder.append('\n');

		return builder.toString();
	}

	@Override
	public int hashCode() {
		return this.getActivityID();
	}

	@Override
	public boolean equals(Object obj) {
		return (obj instanceof ActivitySchedule)
				? (this.internalEquals((ActivitySchedule<?>) obj))
				: false;
	}

	private boolean internalEquals(ActivitySchedule<?> that) {
		return this.getActivity().equals(that.getActivity())
			&& this.getStartTime() == that.getStartTime();
	}
}
