package edu.monash.ppoi.instance;

public class OnceOff extends Activity {

	public static final String LABEL = "a";

	private final int value;
	private final int outOfficeDiscount;

	public OnceOff(int id, int numRooms, Room size, int loadkW, int duration, int value, int cost) {
		super(id, numRooms, size, loadkW, duration);

		this.value = value;
		this.outOfficeDiscount = cost;
	}

	public int getValue() {
		return value;
	}

	public int getOutOfOfficePenalty() {
		return outOfficeDiscount;
	}

	@Override
	public String getActivityLabel() {
		return LABEL;
	}

	@Override
	public String getFormatString() {
		return String.format("%s %d %d %s %d %d %d %d %d%s",
				this.getActivityLabel(),
				this.getID(),
				this.getNumRooms(),
				this.getRoomSize().toString(),
				this.getLoadkW(),
				this.getDuration(),
				this.getValue(),
				this.getOutOfOfficePenalty(),
				this.getNumPreceding(),
				getPrecedenceString());

	}

	public static OnceOff parseOnceOff(String lines) {

		String[] line = lines.split(" ");
		if (line.length < 9 || !LABEL.equals(line[0])) {
			throw new RuntimeException("Unexpected format for once-off.");
		}

		return new OnceOff(
				Integer.parseInt(line[1]),
				Integer.parseInt(line[2]),
				Room.parse(line[3]),
				Integer.parseInt(line[4]),
				Integer.parseInt(line[5]),
				Integer.parseInt(line[6]),
				Integer.parseInt(line[7]));
	}
}
