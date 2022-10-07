package edu.monash.ppoi.checker;

public interface IScheduleChecker {

	public double getObjective();

	public double getEnergyCost();

	public double getPeakCost();

	public double getScore();
}
