package edu.monash.ppoi.instance;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

import edu.monash.io.FileUtils;

public class Instance {

	private final List<Building> buildings;
	private final List<Solar> solarpanels;
	private final List<Battery> batteries;
	private final List<Recurring> recurring;
	private final List<OnceOff> onceoff;

	public Instance() {
		this.buildings = new ArrayList<>();
		this.solarpanels = new ArrayList<>();
		this.batteries = new ArrayList<>();
		this.recurring = new ArrayList<>();
		this.onceoff = new ArrayList<>();
	}

	public void add(Building b) {
		buildings.add(b);
	}

	private Building getBuilding(int id) {
		for (Building b : buildings) {
			if (b.getID() == id) {
				return b;
			}
		}
		return null;
	}

	public void add(Solar s) {
		solarpanels.add(s);
		getBuilding(s.getBuildingID()).attach(s);
	}

	public void add(Battery c) {
		batteries.add(c);
		getBuilding(c.getBuildingID()).attach(c);
	}

	public void add(Recurring r) {
		recurring.add(r);
	}

	public void add(OnceOff a) {
		onceoff.add(a);
	}

	public List<Building> getAllBuildings() {
		return buildings;
	}

	public int getMaxBuildingID() {
		return buildings.stream().mapToInt(Building::getID).max().orElse(0);
	}

	public List<Solar> getAllSolar() {
		return solarpanels;
	}

	public Recurring getRecurring(int id) {
		return recurring.get(id);
	}

	public List<Recurring> getAllRecurring() {
		return recurring;
	}

	public OnceOff getOnceOff(int id) {
		return onceoff.get(id);
	}

	public List<OnceOff> getAllOnceOff() {
		return onceoff;
	}

	public Battery getBattery(int id) {
		return batteries.get(id);
	}

	public List<Battery> getAllBatteries() {
		return batteries;
	}

	public String getHeaderString() {
		return String.format("ppoi %d %d %d %d %d",
				buildings.size(),
				solarpanels.size(),
				batteries.size(),
				recurring.size(),
				onceoff.size());
	}

	public String toString() {

		StringBuilder builder = new StringBuilder();

		builder.append(this.getHeaderString());
		builder.append('\n');

		this.appendAll(buildings, builder);
		this.appendAll(solarpanels, builder);
		this.appendAll(batteries, builder);
		this.appendAll(recurring, builder);
		this.appendAll(onceoff, builder);

		return builder.toString();
	}

	private void appendAll(List<?> items, StringBuilder builder) {
		for (Object item : items) {
			builder.append(item.toString());
			builder.append('\n');
		}
	}

	public static Instance parseInstance(File file) {

		if (!file.exists()) {
			throw new RuntimeException("Missing file " + file.getAbsolutePath());
		}

		String[] lines = FileUtils.readFileAsString(file.getPath()).split("[\r\n]+");

		int lineNum = 0;
		String[] header = lines[lineNum].split(" ");
		if (header.length != 6 || !"ppoi".equals(header[0])) {
			throw new RuntimeException("Instance does not start with instance identifier 'ppoi'.");
		}

		Instance instance = new Instance();

		int numBuildings = Integer.parseInt(header[1]);
		int numSolar = Integer.parseInt(header[2]);
		int numBattery = Integer.parseInt(header[3]);
		int numRecurring = Integer.parseInt(header[4]);
		int numOnceOff = Integer.parseInt(header[5]);

		for (int i = 0; i < numBuildings; i++) {
			instance.add(Building.parseBuilding(lines[++lineNum]));
		}

		for (int i = 0; i < numSolar; i++) {
			instance.add(Solar.parseSolar(lines[++lineNum]));
		}

		for (int i = 0; i < numBattery; i++) {
			instance.add(Battery.parseBattery(lines[++lineNum]));
		}

		int reset = lineNum;
		for (int i = 0; i < numRecurring; i++) {
			instance.add(Recurring.parseRecurring(lines[++lineNum]));
		}

		int reset2 = lineNum;
		for (int i = 0; i < numOnceOff; i++) {
			instance.add(OnceOff.parseOnceOff(lines[++lineNum]));
		}

		lineNum = reset;
		for (int i = 0; i < numRecurring; i++) {
			lineNum++;
			
			String[] line = lines[lineNum].split(" ");

			int id = Integer.parseInt(line[1]);
			int numPredecessor = Integer.parseInt(line[6]);
			for (int j = 0; j < numPredecessor; j++) {
				Recurring current = instance.getRecurring(id);
				Recurring previous = instance.getRecurring(Integer.parseInt(line[7+j]));
				current.addPreceding(previous);
			}
		}

		lineNum = reset2;
		for (int i = 0; i < numOnceOff; i++) {
			lineNum++;
			
			String[] line = lines[lineNum].split(" ");

			int id = Integer.parseInt(line[1]);
			int numPredecessor = Integer.parseInt(line[8]);
			for (int j = 0; j < numPredecessor; j++) {
				OnceOff current = instance.getOnceOff(id);
				OnceOff previous = instance.getOnceOff(Integer.parseInt(line[9+j]));
				current.addPreceding(previous);
			}
		}

		return instance;
	}
}
