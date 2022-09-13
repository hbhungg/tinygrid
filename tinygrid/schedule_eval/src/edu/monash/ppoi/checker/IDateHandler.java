package edu.monash.ppoi.checker;

import java.util.List;

public interface IDateHandler {

	public int getHorizon();

	public boolean isWorkingHours(int start, int duration);

	public List<Integer> getAllDays(int start);

	public List<Integer> getRecurring(int start);

	public int getDay(int timestep);

	public int getPeriod(int timestep);
}
