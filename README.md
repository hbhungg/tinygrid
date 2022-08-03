# Tinygrid
Prediction and Optimisation for Renewable Energy Scheduling in the Monash Microgrid

## Setup
### On Macos/Linux
Open your terminal at the project folder.
Important: Make sure you upgrade your pip
```
python3 -m venv venv/
source venv/bin/activate
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
```

Export the project dir to `$PYTHONPATH`. This will make Python treat the repo as the root folder.

Get your path using:
```
cd
PWD
```

Nano into file
```
nano .zshrc
```
or
```
nano .bashrc
```

Change the bellow path to your PWD path.
At the first 2 lines type and writeout:
```
export PYTHONPATH=path
export JUPYTER_PATH=path
```
If you have issues in vscode using ipynb files, use instead the web version.
Install notebook and ipykernel, then include the correct virtual kernal.
```
pip install notebook ipykernel
python -m ipykernel install --user --name=venv
```

Once in web version, switch the kernal from the tab view.

To Deactivate venv type the following:
```
deactivate
```


## Forecasting problem
Using `nov_data.tsf` dataset since it is the complete dataset.

- Phase 1: 2976 - 31 days of October 2020
- Phase 2: 2880 - 30 days of November 2020

## Optimization problem
- IDK lol


# Contributor: 
Team DS-9
- Aldrich Lado Buntoro
- Anirudh Prakash
- Ba Hung Huynh
- Harris Perdikoyiannis
