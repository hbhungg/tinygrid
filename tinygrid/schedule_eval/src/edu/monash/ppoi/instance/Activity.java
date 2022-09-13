package edu.monash.ppoi.instance;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

public abstract class Activity {

	private final int id;
	private final int numRooms;
	private final Room roomSize;
	private final int loadkW;
	private final int duration;

	private final List<Activity> preceding;

	public Activity(int id, int numRooms, Room size, int loadkW, int duration) {
		
		this.id = id;
		this.numRooms = numRooms;
		this.roomSize = size;
		this.loadkW = loadkW;
		this.duration = duration;
		
		this.preceding = new ArrayList<>();
	}

	public int getID() {
		return id;
	}

	public String getIDLabel() {
		return Integer.toString(id);
	}

	public int getNumRooms() {
		return numRooms;
	}

	public Room getRoomSize() {
		return roomSize;
	}

	public int getLoadkW() {
		return loadkW;
	}

	public int getDuration() {
		return duration;
	}

	public int getNumPreceding() {
		return preceding.size();
	}

	public List<Activity> getPreceding() {
		return preceding;
	}

	protected String getPrecedenceString() {
		return (preceding.size() > 0)
				? preceding.stream()
						   .map(Activity::getIDLabel)
						   .collect(Collectors.joining(" ", " ", ""))
				: "";
	}

	public void addPreceding(Activity a) {
		this.preceding.add(a);
	}

	public void setPreceding(List<? extends Activity> preceding) {
		this.preceding.clear();
		this.preceding.addAll(preceding);
	}

	public String toString() {
		return this.getFormatString();
	}

	public abstract String getActivityLabel();
	public abstract String getFormatString();

	public boolean usesLarge() {
		return Room.Large.equals(roomSize);
	}

	public static <A extends Activity> List<List<Integer>> getPrecedenceClosure(List<A> activities) {

		List<Set<Integer>> preceding = new ArrayList<>();

		// Initialize the collection using the immediate 
		for (int i = 0; i < activities.size(); i++) {
			A activity = activities.get(i);
			Set<Integer> precedences = new LinkedHashSet<>();
			activity.getPreceding().stream().map(Activity::getID).forEach(precedences::add);
			preceding.add(precedences);
		}

		// Recursively capture precedences.
		boolean changed = true;
		while (changed) {
			changed = false;
			for (int i = 0; i < preceding.size(); i++) {
				Set<Integer> precedences = new LinkedHashSet<>(preceding.get(i));
				for (int j : precedences) {
					changed = preceding.get(i).addAll(preceding.get(j)) || changed;
				}
			}
		}

		// Sort precedences by ID.
		List<List<Integer>> sorted = new ArrayList<>();
		for (Set<Integer> prevSet : preceding) {
			List<Integer> prevList = new ArrayList<>(prevSet);
			prevList.sort(Comparator.naturalOrder());
			sorted.add(prevList);
		}

		return sorted;
	}
}
