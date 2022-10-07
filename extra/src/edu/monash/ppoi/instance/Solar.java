package edu.monash.ppoi.instance;

public class Solar {

	private final int solarID;
	private final int buildingID;

	public Solar(int sID, int bID) {
		this.solarID = sID;
		this.buildingID = bID;
	}

	public int getSolarID() {
		return solarID;
	}

	public int getBuildingID() {
		return buildingID;
	}

	@Override
	public int hashCode() {
		return getSolarID();
	}

	@Override
	public String toString() {
		return String.format("s %d %d", solarID, buildingID);
	}

	@Override
	public boolean equals(Object obj) {
		return (obj instanceof Solar) ? this.internalEquals((Solar) obj) : false;
	}

	private boolean internalEquals(Solar that) {
		return this.getSolarID() == that.getSolarID() && this.getBuildingID() == that.getBuildingID();
	}

	public static Solar parseSolar(String line) {

		String[] parts = line.split(" ");
		if (parts.length != 3 || !"s".equals(parts[0])) {
			throw new RuntimeException("Unexpected format for solar.");
		}

		return new Solar(
				Integer.parseInt(parts[1]),
				Integer.parseInt(parts[2]));
	}
}
