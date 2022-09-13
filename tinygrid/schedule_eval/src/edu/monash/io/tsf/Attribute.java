package edu.monash.io.tsf;

public class Attribute {

	public static final Attribute SERIES_NAME = new Attribute("series_name", DataType.STRING);
	public static final Attribute START_TIMESTAMP = new Attribute("start_timestamp", DataType.DATE);
	public static final Attribute DATA = new Attribute("data", DataType.DATA);

	private final String name;
	private final DataType type;

	public Attribute(String name, DataType type) {
		this.name = name;
		this.type = type;
	}

	public String getName() {
		return name;
	}

	public DataType getType() {
		return type;
	}

	@Override
	public String toString() {
		return String.format("[%s, %s]", getName(), getType().toString());
	}

	@Override
	public int hashCode() {
		return getName().hashCode();
	}

	@Override
	public boolean equals(Object other) {
		return (other instanceof Attribute ? this.internalEquals((Attribute) other) : false);
	}

	private boolean internalEquals(Attribute that) {
		return this.getName().equals(that.getName()) && this.getType().equals(that.getType());
	}
}
