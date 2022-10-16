# Tinygrid
Tinygrid is a small Python library that team DS-9 use to solve the [IEEE-CIS Monash Microgrid prediction and optimization challenge](https://ieee-dataport.org/competitions/ieee-cis-technical-challenge-predictoptimize-renewable-energy-scheduling). 

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

The project is developed and tested with Python 3.9, but should be able to work with Python >= 3.7. It is recommended to set up a Python virtual environment for dealing with Tinygrid's dependencies.
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```
This will create a virtual env inside Tinygrid's folder, activate it and install all of the dependencies listed in the `requirements.txt`. 

## Quick example
_(The project is in development stage, some of the import API and modules name might change)._
### Forecasting
First, load the IEEE-CIS dataset.
```python
from tinygrid.dataset import IEEE_CIS
from tinygrid.utils import Const

# Data manager object
ieee_cis = IEEE_CIS()

# Load the solar + building energy data and weather data
energy_data = ieee_cis.load_energy_data()
weather_data = ieee_cis.load_ERA5_weather_data()
```
As an example, we will work on 2 data instances, Building0 and Solar0, and forecast 2976 datapoints (15-minute time step) for the whole month Oct 2020 (Phase 1 of the competition).
```python
# Data up to the end of November 2020
solar0 = energy_data['Solar0']
building0 = energy_data['Building0']

# Split the dataset into training (before Oct 2020) and testing dataset (Oct 2020)
solar0_train = solar0[:Const.PHASE1_TIME_S1]
solar0_test = solar0[Const.PHASE1_TIME_S1:Const.PHASE1_TIME_S2]

building0_train = building0[:Const.PHASE1_TIME_S1]
building0_test = building0[Const.PHASE1_TIME_S1:Const.PHASE1_TIME_S2]
```
To clean and augment the data, you can use Tinygrid's `generate_building_data()` and `generate_solar_data()`.
```python
from tinygrid.forecaster import generate_building_data, generate_solar_data

# Generate data for training
building0_x_train, building0_y_train = generate_building_data(building0_train)
# If no input data, and with start and end time, generate_building_data will generate features for forecaster to predict on. 
# This case we input in the start and end time of Oct 2020.
building0_x_test = generate_building_data(None, start=Const.PHASE1_TIME, end=Const.PHASE2_TIME)

# The same for solar data, but instead we use generate_building_data(), and it also required weather data.
solar0_x_train, solar0_y_train = generate_solar_data(solar0_train, weather_data)
solar0_x_test = generate_solar_data(None, weather_data, start=Const.PHASE1_TIME, end=Const.PHASE2_TIME)
```

Create Forecaster object for each data instance to fit the dataset, generate forecast and evaluate the forecast performance. The IEEE-CIS challenge assess the performance using [MASE](https://www.sciencedirect.com/science/article/abs/pii/S0169207006000239?via%3Dihub) metric.
```python
# Evaluation metric
from tinygrid.utils import mase
from tinygrid.forecaster import Forecaster

# Init Forecaster object 
solar0_forecaster = Forecaster()
building0_forecaster = Forecaster()

# Fit the processed data
solar0_forecaster.fit(solar0_x_train, solar0_y_train)
# Generate forecast
solar0_pred = bf.predict(solar0_x_test)
# Evaluate the forecasted data with actual data, using MASE.
score = mase(solar0_pred, solar0_test['energy'].to_numpy(), solar0_train['energy'].to_numpy())

# Similar to the above steps
building_forecaster.fit(building0_x_train, building0_y_train)
solar_pred = bf.predict(building0_x_test)
# Evaluate the forecasted data with actual data, using MASE.
score = mase(solar0_pred, solar0_test['energy'].to_numpy(), solar0_train['energy'].to_numpy())
 ```

### Scheduling
Load the instance. As an example, we will optimize for phase 1 instance small 0.
```python
from tinygrid.dataset import IEEE_CIS

# Data manager object
ieee_cis = IEEE_CIS()
# Load the instance
ins = ieee_cis.load_instance_data()["phase1_instance_small_0.txt"]
# Load the sample solution for warm start (optional)
sam_sol = ieee_cis.load_instance_sample_solution_data()["phase1_instance_solution_small_0.txt"]
# Load the price data
price = ieee_cis.load_AEMO_price_data()['RRP']
```

Create a optimizer object. The optimizer underneath is Google's [ortool](https://github.com/google/or-tools), using the [CP SAT Solver](https://developers.google.com/optimization/cp/cp_solver). 
The optimizer attempt to reframe the problem into an integer programming problem, inspired by [this paper](https://arxiv.org/pdf/2112.03595.pdf).
```python
sol = optimizer(instance=ins, warm_start=sam_sol, price=price, start_time=p1s, end_time=p1e)
save_schedule("oo.txt", sol)
```

# Contributor (Team DS-9): 
- Aldrich Lado Buntoro
- Anirudh Prakash
- Ba Hung Huynh
- Harris Perdikoyiannis
