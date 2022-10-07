package edu.monash.ppoi.checker;

import java.time.DayOfWeek;
import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.Month;
import java.time.Year;
import java.util.ArrayList;
import java.util.List;

public class DateHandler implements IDateHandler {

	public static final int PERIODS_PER_HOUR = 4;
	public static final int PERIODS_PER_DAY = 24 * PERIODS_PER_HOUR;

	private final int year;
	private final Month month;
	private final int numDays;
	private final int firstMonday;

	public DateHandler(int year, Month month) {
		this.year = year;
		this.month = month;
		this.numDays = month.length(Year.isLeap(year));
		this.firstMonday = getFirst(year, month, DayOfWeek.MONDAY);
	}

	public LocalDateTime getStart() {
		return LocalDateTime.of(year, month, 1, 0, 0);
	}

	public Duration getDuration() {
		return Duration.ofDays(numDays);
	}

	public int getHorizon() {
		return numDays * PERIODS_PER_DAY;
	}

	public boolean isWorkingHours(int start, int duration) {
		
		// Convert period to day.
		int startDay = getDay(start);
		int startPeriod = getPeriod(start);

		int endDay = getDay(start + duration);
		int endPeriod = getPeriod(start + duration);

		// Start and end on same day in the month, within working hours, on a work day.
		return startDay == endDay &&
			   startDay <= numDays &&
			   isWorkDay(startDay) &&
			   isWorkPeriod(startPeriod) &&
			   isWorkPeriod(endPeriod);
	}

	public boolean isWorkDay(int dayOfMonth) {
		return LocalDate.of(year, month, dayOfMonth).getDayOfWeek().ordinal() < DayOfWeek.SATURDAY.ordinal();
	}

	private static boolean isWorkPeriod(int period) {
		return period >=  9 * PERIODS_PER_HOUR &&
			   period <= 17 * PERIODS_PER_HOUR;
	}

	public int getDay(int period) {
		return period / PERIODS_PER_DAY + 1;
	}

	public int getPeriod(int period) {
		return period % PERIODS_PER_DAY;
	}

	public List<Integer> getAllDays(int start) {

		// Convert period to day of the week.
		DayOfWeek weekday = LocalDate.of(year, month, getDay(start)).getDayOfWeek();

		// Find all days in the month.
		List<Integer> days = new ArrayList<>();
		for (int day = firstMonday; day <= numDays; day++)
			if (weekday.equals(LocalDate.of(year, month, day).getDayOfWeek()))
				days.add(day-1);
		
		return days;
	}

	public List<Integer> getRecurring(int start) {
		
		List<Integer> recurring = new ArrayList<>();
		int period = getPeriod(start);

		// Compute start time on this day.
		for (int day : getAllDays(start))
			recurring.add(day * DateHandler.PERIODS_PER_DAY + period);

		return recurring;
	}

	public static int getFirst(int year, Month month, DayOfWeek weekday) {
		int day = 1;
		while (!weekday.equals(LocalDate.of(year, month, day).getDayOfWeek()))
			day++;
		return day;
	}
}
