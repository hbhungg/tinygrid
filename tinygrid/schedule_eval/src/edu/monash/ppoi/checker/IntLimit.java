package edu.monash.ppoi.checker;

import java.util.Arrays;

public class IntLimit {

	private int limit;
	private final int[] usage;

	public IntLimit(int limit, int horizon) {
		this.limit = limit;
		this.usage = new int[horizon];
	}

	public int getHorizon() {
		return usage.length;
	}

	public boolean positive() {
		return limit > 0;
	}

	public void increment() {
		limit++;
	}

	public boolean isValid() {
		
		boolean check = true;

		for (int time = 0; check && time < usage.length; time++) {
			check = check && check(time);
		}

		return check;
	}

	public int getLimit() {
		return limit;
	}

	public int getMaxUse() {
		return Arrays.stream(usage).max().orElse(0);
	}
	
	public boolean accumulate(int start, int duration, int amount) {

		boolean check = true;

		for (int time = start; time < start + duration; time++) {
			usage[time] += amount;
			check = check && check(time);
		}

		return check;
	}

	public boolean retract(int start, int duration, int amount) {

		boolean check = true;

		for (int time = start; time < start + duration; time++) {
			usage[time] -= amount;
			check = check && check(time);
		}

		return check;
	}

	private boolean check(int time) {
		return getUse(time) >= 0 && getUse(time) <= limit;
	}

	public int getUse(int time) {
		return usage[time];
	}

	public int getAvailable(int start, int duration) {

		int available = limit;
		
		for (int time = start; time < start + duration; time++)
			available = Math.min(available, limit - getUse(time));

		return available;
	}

	@Override
	public String toString() {
		return Arrays.toString(usage) + " <= " + limit;
	}
}
