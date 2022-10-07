package edu.monash.ppoi.instance;

public enum Room {

	Small("S"), Large("L");

	private final String label;

	private Room(String label) {
		this.label = label;
	}

	public String toString() {
		return label;
	}

	public static Room parse(String label) {
		if ("S".equals(label)) {
			return Small;
		} else if ("L".equals(label)) {
			return Large;
		} else {
			throw new IllegalArgumentException("Unexpected label " + label);
		}
	}
}
