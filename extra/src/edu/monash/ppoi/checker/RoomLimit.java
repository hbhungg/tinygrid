package edu.monash.ppoi.checker;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.stream.Collectors;

import edu.monash.ppoi.instance.Building;
import edu.monash.ppoi.instance.Room;

public class RoomLimit {

	private final Map<Integer, IntLimit> limits = new LinkedHashMap<>();

	public RoomLimit(List<Building> buildings, Room size, int horizon) {
		for (Building building : buildings) {
			this.limits.put(building.getID(), new IntLimit(building.getNumRooms(size), horizon));
		}
	}

	public RoomLimit(List<Integer> limits, int horizon) {
		for (int i = 0; i < limits.size(); i++) {
			this.limits.put(i, new IntLimit(limits.get(i), horizon));
		}
	}

	public List<Integer> getBuildings() {
		return new ArrayList<>(limits.keySet());
	}

	public int getHorizon() {
		return limits.values().iterator().next().getHorizon();
	}

	public int getLimit(int building) {
		return limits.get(building).getLimit();
	}

	public boolean isValid() {
		boolean valid = true;
		for (IntLimit limit : limits.values())
			valid = valid && limit.isValid();

		return valid;
	}

	public boolean accumulate(List<Integer> ids, int start, int duration) {

		boolean valid = true;
		
		for (int id : ids) {
			valid = limits.get(id).accumulate(start, duration, 1) && valid;
		}

		return valid;
	}

	public boolean retract(List<Integer> ids, int start, int duration) {

		boolean valid = true;
		
		for (int id : ids) {
			valid = limits.get(id).retract(start, duration, 1) && valid;
		}

		return valid;
	}

	public void increaseRandomLimit(Random rng) {

		// Identify indices of non-zero entries.
		List<IntLimit> nonzero = limits.values().stream()
												.filter(IntLimit::positive)
												.collect(Collectors.toList());

		// Choose one of the non-zeroes to increase.
		nonzero.get(rng.nextInt(nonzero.size())).increment();
	}

	public List<Integer> getLimits() {
		return limits.values().stream()
							  .map(IntLimit::getLimit)
							  .collect(Collectors.toList());
	}

	public List<Integer> getMaxUse() {
		return limits.values().stream()
							  .map(IntLimit::getMaxUse)
							  .collect(Collectors.toList());
	}

	public int getUsage(int bID, int time) {
		return limits.get(bID).getUse(time);
	}

	public int[] getAvailable(int start, int duration) {
		return limits.values().stream()
							  .mapToInt(limit -> limit.getAvailable(start, duration))
							  .toArray();
	}
}
