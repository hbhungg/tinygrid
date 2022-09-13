package edu.monash.ppoi.checker;

import java.time.DayOfWeek;
import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.Month;
import java.time.Year;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import edu.monash.io.tsf.PlainTimeSeries;
import edu.monash.io.tsf.TimeSeriesDB;

public class ChronicsHandler implements IDateHandler {

	public static final ZoneId UTC = ZoneId.of("UTC");
	public static final ZoneId TZ = ZoneId.of("Australia/Melbourne");

	public static final Duration DELTA = Duration.ofMinutes(15);
	public static final int PERIODS_PER_HOUR = 4;
	public static final int PERIODS_PER_DAY = 24 * PERIODS_PER_HOUR;
	public static final int PERIODS_PER_WEEK = 7 * PERIODS_PER_DAY;

	private final int year;
	private final Month month;
	private final ZonedDateTime start;

	private final int numDays;
	private final int numSteps;
	private final int offset;
	private final int firstFullDay;
	private final int firstMonday;

	private final List<List<Integer>> recurring;

	private final Map<String, PlainTimeSeries> loads;
	private final PlainTimeSeries prices;

	public ChronicsHandler(int year, Month month, TimeSeriesDB loadSeries, PlainTimeSeries priceSeries) {

		this.year = year;
		this.month = month;
		this.start = ZonedDateTime.of(LocalDateTime.of(year, month, 1, 0, 0), UTC);

		this.loads = loadSeries.forMonth(year, month);
		this.prices = priceSeries.forMonth(year, month);

		this.numDays = month.length(Year.isLeap(year));
		this.numSteps = numDays * PERIODS_PER_DAY;
		this.offset = computeOffset();
		this.firstFullDay = computeFullDayStart();
		this.firstMonday = DateHandler.getFirst(year, month, DayOfWeek.MONDAY);
		this.recurring = computeRecurring();

		validate();
	}

	private int computeOffset() {
		int offset = 0;
		while (!this.getAEDT(offset).getDayOfWeek().equals(DayOfWeek.MONDAY))
			offset++;
		return offset;
	}

	private int computeFullDayStart() {
		int offset = 0;
		while (this.getAEDT(offset).getHour() != 0)
			offset++;
		return offset;
	}

	private List<List<Integer>> computeRecurring() {

		/*
		 * Compute list of recurring periods.
		 */
		int offset = getOffset();
		List<List<Integer>> recurring = new ArrayList<>();
		
		for (int time = offset; time < offset + PERIODS_PER_WEEK; time++) {
			
			// Identify which periods are recurring,
			List<Integer> periods = new ArrayList<>();
			for (int i = 0; i < 4; i++)
				periods.add(time + i * PERIODS_PER_WEEK);

			// Add recurring periods to the collection.
			recurring.add(periods);
		}

		/*
		 * Replicate list of recurring items for the active weeks.
		 */
		List<List<Integer>> allRecurring = new ArrayList<>();
		
		// Padding the time before the first Monday.
		for (int time = 0; time < offset; time++)
			allRecurring.add(null);
		
		// Four weeks of recurring schedule.
		for (int i = 0; i < 4; i++)
			for (int time = 0; time < PERIODS_PER_WEEK; time++)
				allRecurring.add(recurring.get(time));

		return allRecurring;
	}

	private void validate() {

		if (this.numSteps != this.prices.size())
			throw new IllegalArgumentException(String.format("Unequal length timestamps %d and price data %d.", this.numSteps, this.prices.size()));
		
		for (Map.Entry<String, PlainTimeSeries> entry : loads.entrySet())
			if (this.numSteps != entry.getValue().size())
				throw new IllegalArgumentException(String.format("Unequal length timestamps %d and load '%s' data %d.", this.numSteps, entry.getKey(), entry.getValue().size()));

		for (int t = 0; t < this.numSteps; t++) {
			ZonedDateTime time = getUTC(t);
			for (PlainTimeSeries value : this.loads.values()) {
				if (!value.getTimestamps().get(t).equals(time)) {
					throw new IllegalArgumentException(String.format("Timestamp mismatch at t=%d.", t));
				}
			}
		}
	}

	public LocalDateTime getStart() {
		return start.toLocalDateTime();
	}

	public Duration getDuration() {
		return Duration.ofDays(numDays);
	}

	public int getHorizon() {
		return numSteps;
	}

	public int getOffset() {
		return offset;
	}

	public ZonedDateTime getUTC(int timestep) {
		return this.start.plus(DELTA.multipliedBy(timestep));
	}

	public ZonedDateTime getAEDT(int timestep) {
		return getUTC(timestep).withZoneSameInstant(TZ);
	}

	public int getDay(int timestep) {
		
		ZonedDateTime startDay = getAEDT(firstFullDay).minus(Duration.ofDays(2));
		ZonedDateTime nowDay = getAEDT(timestep);
		
		return (int) Duration.between(startDay.toLocalDateTime(), nowDay.toLocalDateTime()).toDays();
	}

	public int getPeriod(int timestep) {
		
		ZonedDateTime time = getAEDT(timestep);
		
		int hour = time.getHour();
		int minute = time.getMinute();
		int period = hour * 4 + minute / 15;
		
		return period;
	}

	@Override
	public boolean isWorkingHours(int start, int duration) {

		// Last period.
		int end = start + duration - 1;

		// Convert period to day.
		ZonedDateTime startTime = getAEDT(start);
		ZonedDateTime endTime = getAEDT(end);

		// Checks.
		boolean inHorizon = start >= 0 && end < getHorizon();
		boolean sameDay = startTime.toLocalDate().equals(endTime.toLocalDate());
		boolean workPeriods = isWorkPeriod(start) && isWorkPeriod(end);

		// Start and end in the scheduling horizon, on same day, all within working hours.
		return inHorizon && sameDay && workPeriods;
	}

	public boolean isWorkPeriod(int timestep) {

		// Time step to AEDT.
		ZonedDateTime instant = getAEDT(timestep);

		// Checks.
		boolean workDay = instant.getDayOfWeek().ordinal() < DayOfWeek.SATURDAY.ordinal();
		boolean after9am = instant.toLocalTime().isAfter(LocalTime.of(8, 59));
		boolean before5pm = instant.toLocalTime().isBefore(LocalTime.of(17, 0));

		// Is work day and work hours?
		return workDay && after9am && before5pm;
	}

	public double getPrice(int timestep) {
		return this.prices.getData().get(timestep);
	}

	public List<Double> getPrices() {
		return this.prices.getData();
	}

	public List<Integer> getAllDays(int start) {

		// Convert period to day of the week.
		DayOfWeek weekday = getAEDT(start).getDayOfWeek();

		// Find all days in the month.
		List<Integer> days = new ArrayList<>();
		for (int day = firstMonday; day <= numDays; day++) {

			// Which day is this?
			DayOfWeek dayOfWeek = LocalDate.of(year, month, day).getDayOfWeek();

			// If this entire week is still part of this month,
			if (day + (DayOfWeek.FRIDAY.ordinal() - dayOfWeek.ordinal()) <= numDays)
				if (weekday.equals(LocalDate.of(year, month, day).getDayOfWeek()))
					days.add(day-1);
		}
		
		return days;
	}

	public List<Integer> getRecurring(int period) {
		return this.recurring.get(period);
	}

	public double getLoad(int timestep, String label) {

		double sum = 0d;

		for (Map.Entry<String, PlainTimeSeries> entry : this.loads.entrySet()) {

			String name = entry.getKey();
			double value = entry.getValue().getData().get(timestep);

			value = Double.isNaN(value) ? 0d : value;

			if (name.contains(label))
				sum += value;
		}

		return sum;
	}

	public double getMaxLoad() {

		double maxLoad = 0;

		for (int t = 0; t < getHorizon(); t++) {
			double load = getLoad(t, "Building");
			maxLoad = (maxLoad < load) ? load : maxLoad;
		}

		return maxLoad;
	}
}
