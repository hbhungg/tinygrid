package edu.monash.io.tsf;

public class RecurringTimeSeriesView {

	private final TimeSeries series;
	private final int offset;
	private final int length;

	private int position;

	public RecurringTimeSeriesView(TimeSeries series, int start, int length) {

		this.series = series;
		this.offset = start;
		this.length = length;
		this.position = 0;

		this.series.ensureCached();
	}

	public InstantValue next() {
		
		InstantValue next = series.getInstantValue(offset + position);
		
		position = (position + 1) % length;
		
		return next;
	}
}
