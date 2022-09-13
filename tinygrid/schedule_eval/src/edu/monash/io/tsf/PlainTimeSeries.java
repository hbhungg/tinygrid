package edu.monash.io.tsf;

import java.time.LocalDateTime;
import java.time.Month;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.temporal.TemporalAmount;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

public class PlainTimeSeries {

	private final List<ZonedDateTime> instant;
	private final List<Double> data;

	public PlainTimeSeries(ZonedDateTime[] instant, double[] data) {
		this.instant = Arrays.asList(instant.clone());
		this.data = Arrays.stream(data.clone()).mapToObj(Double::valueOf).collect(Collectors.toList());
	}

	public PlainTimeSeries(List<ZonedDateTime> instant, List<Double> data) {
		
		this.instant = new ArrayList<>(instant);
		this.data = new ArrayList<>(data);

		if (this.instant.size() != this.data.size())
			throw new IllegalArgumentException("Unequal length timestamps and data.");
	}

	public int size() {
		return instant.size();
	}

	public List<Double> getData() {
		return data;
	}

	public List<ZonedDateTime> getTimestamps() {
		return instant;
	}

	public PlainTimeSeries forMonth(int year, Month month) {

		List<ZonedDateTime> instant = new ArrayList<>();
		List<Double> data = new ArrayList<>();

		for (int i = 0; i < this.instant.size(); i++) {

			ZonedDateTime original = this.instant.get(i);
			double datum = this.data.get(i);

			if (original.getYear() == year && original.getMonth().equals(month)) {
				instant.add(original);
				data.add(datum);
			}
		}

		return new PlainTimeSeries(instant, data);
	}

	public PlainTimeSeries withZoneSameInstant(ZoneId newTZ) {

		List<ZonedDateTime> instant = new ArrayList<>();
		
		for (ZonedDateTime original : this.instant)
			instant.add(original.withZoneSameInstant(newTZ));

		return new PlainTimeSeries(instant, data);
	}

	public PlainTimeSeries minus(TemporalAmount delta) {

		List<ZonedDateTime> instant = new ArrayList<>();
		
		for (ZonedDateTime original : this.instant)
			instant.add(original.minus(delta));

		return new PlainTimeSeries(instant, data);
	}

	public PlainTimeSeries fillForward(TemporalAmount delta) {

		List<ZonedDateTime> instant = new ArrayList<>();
		List<Double> data = new ArrayList<>();

		for (int i = 0; i < this.instant.size(); i++) {

			ZonedDateTime original = this.instant.get(i);
			double datum = this.data.get(i);

			instant.add(original);
			data.add(datum);
			instant.add(original.plus(delta));
			data.add(datum);
		}

		return new PlainTimeSeries(instant, data);
	}

	public static PlainTimeSeries fromRows(List<String[]> rows, int timeColumn, int dataColumn, DateTimeFormatter format, ZoneId tz) {

		List<ZonedDateTime> instant = new ArrayList<>();
		List<Double> data = new ArrayList<>();

		for (String[] row : rows) {
			instant.add(LocalDateTime.parse(row[timeColumn], format).atZone(tz));
			data.add(Double.parseDouble(row[dataColumn]));
		}

		return new PlainTimeSeries(instant, data);
	}
}
