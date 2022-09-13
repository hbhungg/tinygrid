 package edu.monash.io.tsf;

import java.time.Duration;
import java.time.LocalDateTime;
import java.time.Month;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class TimeSeries {
	
	private static final String ATTR_DELIMITER = ":";
	private static final String DATA_DELIMITER = ",";
	private static final String MISSING_FORMAT = "\\?";
	private static final DateTimeFormatter DATE_FORMAT = DateTimeFormatter.ofPattern("y-M-d H-m-s");

	private final Map<String, Attribute> attributeSet;
	private final Map<Attribute, String> attributes;
	private final ZonedDateTime start;
	private final Duration delta;

	private ZonedDateTime[] instant;
	private double[] data;
	
	private TimeSeries(Map<Attribute, String> series, Duration frequency, ZoneId start, ZoneId target) {

		this.attributes = series;
		this.attributeSet = getAttributeSet(attributes.keySet());
		this.start = getStartTime(start, target);
		this.delta = frequency;

		this.instant = null;
		this.data = null;
	}

	private Map<String, Attribute> getAttributeSet(Collection<Attribute> attributes) {

		Map<String, Attribute> attributeSet = new LinkedHashMap<>();
		
		for (Attribute a : attributes) {
			attributeSet.put(a.getName(), a);
		}

		return attributeSet;
	}

	private ZonedDateTime getStartTime(ZoneId startTZ, ZoneId realTZ) {

		String date = attributes.get(Attribute.START_TIMESTAMP);
		LocalDateTime local = LocalDateTime.parse(date, DATE_FORMAT);
		ZonedDateTime zonal = local.atZone(startTZ);

		if (realTZ != null) {
			zonal = zonal.withZoneSameInstant(realTZ);
		}

		return zonal;
	}

	public String getName() {
		return attributes.get(Attribute.SERIES_NAME);
	}

	public String getAttribute(String name) {
		return attributes.get(attributeSet.get(name));
	}

	protected InstantValue getInstantValue(int index) {
		return new InstantValue(instant[index], data[index]);
	}

	public double[] getData() {
		ensureCached(); return data;
	}

	public ZonedDateTime[] getTimestamps() {
		ensureCached(); return instant;
	}

	public RecurringTimeSeriesView getView(LocalDateTime viewStart, Duration duration) {

		ZonedDateTime zonedStart = viewStart.atZone(start.getZone());
		Duration sinceStart = Duration.between(start, zonedStart);
		
		long start = sinceStart.toMillis() / delta.toMillis();
		long count = duration.toMillis() / delta.toMillis();

		return new RecurringTimeSeriesView(this, (int) start, (int) count);
	}

	public String head(int count) {

		ensureCached();
		
		StringBuilder builder = new StringBuilder();

		for (int t = 0; t < count; t++) {
			if (t > 0)
				builder.append("\n");
			
			builder.append(instant[t].toString());
			builder.append(" ");
			builder.append(Double.toString(data[t]));
		}

		return builder.toString();
	}

	protected void ensureCached() {
		if (data == null)
			parseData();
	}

	private void parseData() {
		
		data = parseData(attributes.get(Attribute.DATA));
		instant = new ZonedDateTime[data.length];

		instant[0] = start;
		for (int t = 1; t < data.length; t++) {
			instant[t] = instant[t-1].plus(delta);
		}
	}

	private static double[] parseData(String string) {
		return parseData(string, Double.NaN);
	}

	private static double[] parseData(String data, double missing) {
		return Arrays.stream(data.split(DATA_DELIMITER))
					 .mapToDouble(s -> parseElement(s, missing))
					 .toArray();
	}

	private static double parseElement(String elem, double missing) {
		return elem.matches(MISSING_FORMAT) ? missing : Double.valueOf(elem);
	}

	protected static TimeSeries parse(String line, List<Attribute> attributes, Duration frequency, ZoneId root, ZoneId target) {
		
		// Break up the line into parts.
		String[] parts = line.split(ATTR_DELIMITER);

		// Check that the line matches the expected input format.
		if (parts.length != attributes.size())
			throw new RuntimeException(String.format("Unexpected number of fields in attribute (got %d, expected %d)", parts.length, attributes.size()));

		// Compile the parts into 
		Map<Attribute, String> series = new LinkedHashMap<>();
		for (int i = 0; i < parts.length; i++) {
			series.put(attributes.get(i), parts[i]);
		}

		return new TimeSeries(series, frequency, root, target);
	}

	public PlainTimeSeries forMonth(int year, Month month) {

		ZonedDateTime[] origTimes = this.getTimestamps();
		double[] origData = this.getData();

		List<ZonedDateTime> instant = new ArrayList<>();
		List<Double> data = new ArrayList<>();

		for (int i = 0; i < origTimes.length; i++) {

			ZonedDateTime original = origTimes[i];
			double datum = origData[i];

			if (original.getYear() == year && original.getMonth().equals(month)) {
				instant.add(original);
				data.add(datum);
			}
		}

		return new PlainTimeSeries(instant, data);
	}
}
