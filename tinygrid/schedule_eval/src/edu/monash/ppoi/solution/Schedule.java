package edu.monash.ppoi.solution;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

import edu.monash.io.FileUtils;
import edu.monash.ppoi.instance.Instance;

public class Schedule {

	private final Instance instance;

	private final List<RecurringSchedule> recurStart;
	private final List<OnceOffSchedule> onceOffStart;
	private final List<BatterySchedule> batterySchedule;

	public Schedule(Instance scheduled) {
		
		this.instance = scheduled;
		
		this.recurStart = new ArrayList<>();
		this.onceOffStart = new ArrayList<>();
		this.batterySchedule = new ArrayList<>();
	}

	public Instance getInstance() {
		return instance;
	}

	public void add(RecurringSchedule schedule) {
		recurStart.add(schedule);
	}

	public void add(OnceOffSchedule schedule) {
		onceOffStart.add(schedule);
	}

	public void add(BatterySchedule schedule) {
		batterySchedule.add(schedule);
	}

	public void addAll(List<BatterySchedule> schedule) {
		batterySchedule.addAll(schedule);
	}

	public List<RecurringSchedule> getRecurringSchedule() {
		return recurStart;
	}

	public List<OnceOffSchedule> getOnceOffSchedule() {
		return onceOffStart;
	}

	public List<BatterySchedule> getBatterySchedule() {
		return batterySchedule;
	}

	@Override
	public String toString() {

		StringBuilder builder = new StringBuilder();

		builder.append(instance.getHeaderString());
		builder.append('\n');

		builder.append(String.format("sched %d %d", recurStart.size(), onceOffStart.size()));
		builder.append('\n');

		appendSchedules(recurStart, builder);
		appendSchedules(onceOffStart, builder);
		appendSchedules(batterySchedule, builder);

		return builder.toString();
	}

	private static void appendSchedules(List<?> schedules, StringBuilder builder) {
		for (Object schedule : schedules)
			builder.append(schedule.toString());
	}

	public static Schedule parseSchedule(File file, Instance instance) {

		if (!file.exists()) {
			throw new RuntimeException("Missing file " + file.getAbsolutePath());
		}

		Schedule schedule = new Schedule(instance);
		String[] lines = FileUtils.readFileAsString(file.getPath()).split("[\r\n]+");

		int lineNum = 0;
		if (!instance.getHeaderString().equals(lines[0])) {
			throw new RuntimeException("Mismatch between schedule and instance.");
		}

		String[] header = lines[1].split(" ");
		int numRecurring = Integer.parseInt(header[1]);
		int numOnceOff = Integer.parseInt(header[2]);
		lineNum = 2;

		for (int i = 0; i < numRecurring; i++) {
			schedule.add(RecurringSchedule.parse(instance, lines[lineNum++]));
		}

		for (int i = 0; i < numOnceOff; i++) {
			schedule.add(OnceOffSchedule.parse(instance, lines[lineNum++]));
		}

		schedule.addAll(BatterySchedule.parse(instance, lines, lineNum));

		return schedule;
	}
}
