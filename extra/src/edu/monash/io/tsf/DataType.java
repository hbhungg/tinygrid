package edu.monash.io.tsf;

import java.util.HashMap;
import java.util.Map;

public enum DataType {

	STRING, DATE, DATA;

	private static final Map<String, DataType> lookup = new HashMap<>();
	
	static {
		lookup.put("string", STRING);
		lookup.put("date", DATE);
	}

	public static DataType of(String label) {
		return lookup.get(label.toLowerCase());
	}
}
