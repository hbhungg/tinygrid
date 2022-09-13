package edu.monash.ppoi.instance;

public class Recurring extends Activity {

	public static final String LABEL = "r";

	public Recurring(int id, int numRooms, Room size, int loadkW, int duration) {
		super(id, numRooms, size, loadkW, duration);
	}

	@Override
	public String getActivityLabel() {
		return LABEL;
	}

	@Override
	public String getFormatString() {
		return String.format("%s %d %d %s %d %d %d%s",
				this.getActivityLabel(),
				this.getID(),
				this.getNumRooms(),
				this.getRoomSize().toString(),
				this.getLoadkW(),
				this.getDuration(),
				this.getNumPreceding(),
				getPrecedenceString());

	}

	public static Recurring parseRecurring(String line) {

		String[] parts = line.split(" ");
		if (parts.length < 7 || !LABEL.equals(parts[0])) {
			throw new RuntimeException("Unexpected format for recurring.");
		}

		return new Recurring(
				Integer.parseInt(parts[1]),
				Integer.parseInt(parts[2]),
				Room.parse(parts[3]),
				Integer.parseInt(parts[4]),
				Integer.parseInt(parts[5]));
	}
}
