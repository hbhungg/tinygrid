package edu.monash.io.tsf;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

public class Frequency {

	private static final Map<String, Duration> lookup = new HashMap<>();
	
	static {
		lookup.put("15_minutes", Duration.ofMinutes(15));
		lookup.put("daily", Duration.ofDays(1));
	}

	private Frequency() {}

	public static Duration of(String label) {
		return lookup.get(label.toLowerCase());
	}
}
