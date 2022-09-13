## Schedule evaluation
This module is from https://ieee-dataport.org/competitions/ieee-cis-technical-challenge-predictoptimize-renewable-energy-scheduling, with minor modification to fit this project.

`compile.sh` script to compile.

`run.sh` script to run this module. The solution is the sample solution given by ieee-cis, store the sample solution to tinygrid/cache folder.

The original script accept 2 arguments, this one accept 3, the third arg denote which phase. (Why is this not the default behaviour??)

Inside the Phase.java file, there will be paths to the energy data for each phase, suppose that would be pointing to the predicted data. Right now it is pointing to the real data.

## TODOs:
* Create a Python wrapper around this (compile and run).
* Port this all to Python.

# Original README 
## Prerequisites

Running the code:
 - [Java 1.8 SE JRE](https://www.oracle.com/au/java/technologies/javase-jre8-downloads.html)

Compiling the code:
 - [Java 1.8 SE JDK](https://www.oracle.com/au/java/technologies/javase/javase-jdk8-downloads.html)
 - [Apache Maven](https://maven.apache.org/download.cgi)


## Building the code

Compile the code with your favourite IDE, or package `.jar` with Maven:

    mvn package

Running the instance schedule evaluation:

    java -jar target/evaluate_instance.jar <path_to_instance> <path_to_schedule>

Examples:

    java -jar target/evaluate_instance.jar instances/demoinstance.txt instances/demovalid.txt
    java -jar target/evaluate_instance.jar instances/demoinstance.txt instances/demoinvalid.txt


## Core classes

Main class to start from is found in `edu.monash.ppoi.EvaluateSchedule`. To fit the
local execution environment, change the root folder in `edu.monash.ppoi.Phase` to point
to your input datafiles.

  * `edu.monash.ppoi.instance` contains parser and data classes for instances.
  * `edu.monash.ppoi.solution` contains parser and data classes for solutions.
  * `edu.monash.ppoi.checker` contains classes for checking solution validity and value.
