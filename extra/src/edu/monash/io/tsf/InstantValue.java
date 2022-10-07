package edu.monash.io.tsf;

import java.time.ZonedDateTime;

public class InstantValue {

	private final ZonedDateTime instant;
	private final double value;

	public InstantValue(ZonedDateTime instant, double value) {
		this.instant = instant;
		this.value = value;
	}

	public ZonedDateTime getInstant() {
		return instant;
	}

	public double getValue() {
		return value;
	}

	@Override
	public String toString() {
		return String.format("%s %s",
				instant.toString(),
				Double.toString(value));
	}
}
