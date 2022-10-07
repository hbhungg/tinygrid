package edu.monash.io.tsf;

import java.io.File;
import java.time.Duration;
import java.time.Month;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import edu.monash.io.FileUtils;

public class TimeSeriesDB {

	private static final ZoneId UTC = ZoneId.of("UTC");

	private static final String EMPTY_OR_COMMENT = "^[ \t]*(#.*)?$";
	private static final String ATTRIBUTE = "^[ \t]*@.*";
	private static final String ATTR_DELIM = "[ \t]+";

	private final Duration frequency;
	private final List<Attribute> attributes;
	private final Map<String, TimeSeries> database;

	private TimeSeriesDB(Duration frequency, List<Attribute> attributes, Map<String, TimeSeries> database) {
		this.frequency = frequency;
		this.attributes = attributes;
		this.database = database;
	}

	public Duration getDelta() {
		return frequency;
	}

	public Set<String> getSeriesNames() {
		return database.keySet();
	}

	public TimeSeries getSeries(String name) {
		return database.get(name);
	}

	public Map<String, PlainTimeSeries> forMonth(int year, Month month) {

		Map<String, PlainTimeSeries> subdb = new LinkedHashMap<>();

		for (Map.Entry<String, TimeSeries> entry : database.entrySet())
			subdb.put(entry.getKey(), entry.getValue().forMonth(year, month));

		return subdb;
	}

	@Override
	public String toString() {
		return String.format("<TSF: %s | %s | %s>",
				frequency.toString(),
				attributes.toString(),
				database.keySet().toString());
	}

	public static TimeSeriesDB parse(File file) {
		return parse(file, UTC, null);
	}

	public static TimeSeriesDB parse(File file, ZoneId root, ZoneId target) {
		return parseData(FileUtils.readFileAsString(file), root, target);
	}

	private static TimeSeriesDB parseData(String data, ZoneId root, ZoneId target) {
		
		String[] lines = data.split("[\r\n]+");

		// Store attributes.
		Duration frequency = null;
		List<Attribute> attributes = new ArrayList<>();
		Map<String, TimeSeries> database = new LinkedHashMap<>();

		// Assume headers come first. Switch to parsing series after seeing @data.
		boolean expectData = false;
		
		for (String line : lines) {

			// Skip empty lines and comments.
			if (line.matches(EMPTY_OR_COMMENT)) continue;

			// Parse data or else metadata.
			if (expectData) {

				// Parse line as a series.
				TimeSeries series = TimeSeries.parse(line, attributes, frequency, root, target);
				
				// Store series.
				database.put(series.getName(), series);
				
			} else {
				if (line.matches(ATTRIBUTE)) {
					
					// Break up the line into parts using spaces as delimiter.
					String[] parts = line.split(ATTR_DELIM);

					// Assumption: metadata are at most three parts
					if (parts.length > 3)
						throw new RuntimeException("TSF parse error. Expected no more than three parts for meta data. Received " + Arrays.toString(parts));

					// Tokenizer, decide what to do based on the @property.
					if ("@data".equals(parts[0])) {
						attributes.add(Attribute.DATA);
						expectData = true;
					} else if ("@attribute".equals(parts[0])) {
						attributes.add(new Attribute(parts[1], DataType.of(parts[2])));
					} else if ("@frequency".equals(parts[0])) {
						frequency = Frequency.of(parts[1]);
					}
				} else throw new RuntimeException("TSF parse error. Expected a metadata line starting with @.");
			}
		}

		return new TimeSeriesDB(frequency, attributes, database);
	}
}
