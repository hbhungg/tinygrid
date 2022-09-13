package edu.monash.ppoi;

import java.io.File;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.Month;
import java.time.Year;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

import edu.monash.io.FileUtils;
import edu.monash.io.tsf.PlainTimeSeries;
import edu.monash.io.tsf.TimeSeriesDB;
import edu.monash.ppoi.checker.ChronicsHandler;
import edu.monash.ppoi.checker.ChronicsScheduleChecker;
import edu.monash.ppoi.checker.DateHandler;
import edu.monash.ppoi.checker.IScheduleChecker;
import edu.monash.ppoi.checker.ScheduleChecker;
import edu.monash.ppoi.instance.Instance;
import edu.monash.ppoi.solution.Schedule;

public enum Phase {

	/*
	 * Connect phase with month of the year and input testing data file.
	 * Note that phase_2_data.tsf will be released once phase 1 is complete.
	 */
	P0(2020, Month.SEPTEMBER, "energy/phase_1_data.tsf"),
	P1(2020, Month.OCTOBER,   "energy/phase_2_data.tsf"),
  // P2T is broken
	P2T(2020, Month.OCTOBER,  "energy/nov_data.tsf"),
	P2(2020, Month.NOVEMBER,  "energy/nov_data.tsf");

	/*
	 * Root folder where data files are stored; adjust according to local paths.
	 */
	private static final String ROOT = "../../dataset/";

	private static final String PRICE_FORMAT = "price/PRICE_AND_DEMAND_%4d%02d_VIC1.csv";
	private static final DateTimeFormatter DATE_FORMAT = DateTimeFormatter.ofPattern("yyyy/MM/dd HH:mm:ss");
	private static final ZoneId SOURCE_TZ = ZoneId.of("UTC");
	private static final ZoneId TARGET_TZ = ZoneId.of("Australia/Queensland");

	private final int year;
	private final Month month;
	private final String tsfFile;

	private Phase(int year, Month month, String tsfFile) {
		this.year = year;
		this.month = month;
		this.tsfFile = tsfFile;
	}

	public int getYear() {
		return year;
	}

	public Month getMonth() {
		return month;
	}

	public TimeSeriesDB getLoadSeries() {
		return TimeSeriesDB.parse(new File(getTSFFile()));
	}

	public List<Double> getPrices() {
		return FileUtils.readPriceCSV(getPriceFile());
	}

	public DateHandler getDateHandler() {
		return new DateHandler(year, month);
	}

	public String getPriceFile() {
		return String.format(ROOT + PRICE_FORMAT, year, month.getValue());
	}

	public String getTSFFile() {
		return ROOT + tsfFile;
	}

	public LocalDateTime getStart() {
		return LocalDateTime.of(year, month, 1, 0, 0);
	}

	public Duration getDuration() {
		return Duration.ofDays(month.length(Year.isLeap(year)));
	}

	public void checkSchedule(String[] args) {
		try {
			System.out.println(getObjective(args[0], args[1]));
		} catch (Exception ex) {
			System.out.println(Double.NaN);
			System.out.flush();

			if (args.length < 2) {
				System.err.println("Expected two input arguments, instance file and schedule file.");
			} else {
				System.err.println("Error while evaluating schedule.");
				ex.printStackTrace();
			}
		}
	}

	public double getObjective(String instanceFilename, String scheduleFilename) {
		return getEvaluator().getScheduleChecker(instanceFilename, scheduleFilename).getObjective();
	}

	public IEvaluator getEvaluator() {
		if (this.equals(Phase.P2) || this.equals(Phase.P2T)) {
			return new ChronicsEvaluator(new ChronicsHandler(year, month, getLoadSeries(), readPriceSeries()));
		} else {
			return new Evaluator(getLoadSeries(), getPrices(), getDateHandler());
		}
	}

	public static PlainTimeSeries readPriceSeries() {

		// Read data from disk.
		List<String[]> rows = concatenatePriceFiles();

		// Concatenate the three price files as AEST time series.
		PlainTimeSeries catSeries = PlainTimeSeries.fromRows(rows, 1, 3, DATE_FORMAT, TARGET_TZ);

		// Convert to UTC time, shift down 30 mins to start of the period, upsample so the delta is 15 mins.
		PlainTimeSeries fullSeries = catSeries.withZoneSameInstant(SOURCE_TZ)
											  .minus(Duration.ofMinutes(30))
											  .fillForward(Duration.ofMinutes(15));

		return fullSeries;
	}

	public static List<String[]> concatenatePriceFiles() {

		List<String> files = new ArrayList<>();
		
		for (int month = 9; month <= 12; month++) 
			files.add(ROOT + String.format(PRICE_FORMAT, 2020, month));

		return FileUtils.readCSVs(files);
	}

	public interface IEvaluator {
		public IScheduleChecker getScheduleChecker(String instanceFilename, String scheduleFilename);
	}

	public static class Evaluator implements IEvaluator {

		private final TimeSeriesDB db;
		private final List<Double> prices;
		private final DateHandler dates;

		public Evaluator(TimeSeriesDB db, List<Double> prices, DateHandler dates) {
			this.db = db;
			this.prices = prices;
			this.dates = dates;
		}

		public IScheduleChecker getScheduleChecker(String instanceFilename, String scheduleFilename) {

			// Read in the instance
			Instance instance = Instance.parseInstance(new File(instanceFilename));
			Schedule schedule = Schedule.parseSchedule(new File(scheduleFilename), instance);

			return new ScheduleChecker(db, schedule, prices, dates);
		}
	}

	public static class ChronicsEvaluator implements IEvaluator {

		private final ChronicsHandler db;

		public ChronicsEvaluator(ChronicsHandler db) {
			this.db = db;
		}

		public IScheduleChecker getScheduleChecker(String instanceFilename, String scheduleFilename) {

			// Read in the instance
			Instance instance = Instance.parseInstance(new File(instanceFilename));
			Schedule schedule = Schedule.parseSchedule(new File(scheduleFilename), instance);

			return new ChronicsScheduleChecker(db, schedule);
		}
	}
}
