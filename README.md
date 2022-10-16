# Tinygrid
Tinygrid is a small Python library that team DS-9 use to solve the [Monash Microgrid prediction and optimization challenge](https://ieee-dataport.org/competitions/ieee-cis-technical-challenge-predictoptimize-renewable-energy-scheduling). 

This library provide:
* Modules to load the energy dataset.
* Module to parse and load the instance schedule text file.
* Data augmentation and forecaster (achieved 0.80 MASE score).
* Optimization function to schedule the instance.

## Setup (MacOS/Ubuntu)
Open your terminal, clone the repository and cd into it.
```
git clone git@github.com:hbhungg/tinygrid.git 
cd tinygrid/
```

Export the repository into `$PYTHONPATH`.
```
export PYTHONPATH=$(pwd)
```
You can echo it out using `echo $PYTHONPATH` to check if the correct path has been set.

The project is developed and tested with Python 3.9, but should be able to work with Python < 3.7.

It is recommended to set up a Python virtual environment for dealing with Tinygrid's dependencies.
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```
This will create a virtual env inside Tinygrid's folder, activate it and install all of the dependencies listed in the `requirements.txt`. 

# Contributor (Team DS-9): 
- Aldrich Lado Buntoro
- Anirudh Prakash
- Ba Hung Huynh
- Harris Perdikoyiannis
