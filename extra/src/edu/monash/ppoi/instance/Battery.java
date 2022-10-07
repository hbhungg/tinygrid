package edu.monash.ppoi.instance;

public class Battery {

	public static enum Act {
		CHARGE, HOLD, DISCHARGE;
	}

	public static final String LABEL = "c";

	private final int batteryID;
	private final int buildingID;
	private final int capacitykWh;
	private final int maxChargekW;
	private final double efficiency;

	public Battery(int batteryID, int buildingID, int capacitykWh, int maxChargekW, double efficiency) {
		this.batteryID = batteryID;
		this.buildingID = buildingID;
		this.capacitykWh = capacitykWh;
		this.maxChargekW = maxChargekW;
		this.efficiency = efficiency;
	}

	public int getBatteryID() {
		return batteryID;
	}

	public int getBuildingID() {
		return buildingID;
	}

	public double getCapacityKWh() {
		return capacitykWh;
	}

	public double getMaxChargeKW() {
		return maxChargekW;
	}

	public double getEfficiency() {
		return Math.sqrt(efficiency);
	}

	public double getLoadKW(Act action) {
		switch (action) {
			case DISCHARGE: return -maxChargekW * getEfficiency();
			case CHARGE:    return  maxChargekW / getEfficiency();
			default:        return  0d;
		}
	}

	public double getEnergyKWh(Act action, double delta) {
		switch (action) {
			case DISCHARGE: return -maxChargekW * delta;
			case CHARGE:    return  maxChargekW * delta;
			default:        return 0d;
		}
	}

	@Override
	public int hashCode() {
		return getBatteryID();
	}

	@Override
	public boolean equals(Object other) {
		return (other instanceof Battery) ? this.internalEquals((Battery) other) : false;
	}

	private boolean internalEquals(Battery that) {
		return this.getBatteryID() == that.getBatteryID() &&
			   this.getBuildingID() == that.getBuildingID();
	}

	@Override
	public String toString() {
		return String.format("%s %d %d %d %d %.2f", LABEL, batteryID, buildingID, capacitykWh, maxChargekW, efficiency);
	}

	public static Battery parseBattery(String line) {

		String[] parts = line.split(" ");
		if (parts.length != 6 || !LABEL.equals(parts[0])) {
			throw new RuntimeException("Unexpected format for battery.");
		}

		return new Battery(
				Integer.parseInt(parts[1]),
				Integer.parseInt(parts[2]),
				Integer.parseInt(parts[3]),
				Integer.parseInt(parts[4]),
				Double.parseDouble(parts[5]));
	}
}
