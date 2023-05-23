# CA-EV-charging_report
This repository contains python 3 code to report whether right now is an ideal time to charge an electric car, based on what percent of the grid's electricity comes from clean energy.

Current dependencies:
- requests
- responses
- pandas
- pytest

For those not very familiar with python, here are some quick instructions to make use of this code:
- clone this repo to your local machine. For example, open terminal and run, git clone https://github.com/glenncarson/CA-EV-charging_repor
- Add this repo to your python virtualenv's python path, e.g., export PYTHONPATH="${PYTHONPATH}:/Users/glenn.carson/Coding_Workspace/python_learning/venv/bin"
- I find it helpful to run the main charging_report_gen.py script via an alias that also launches my virtual environment, e.g., alias charge='source ~/Coding_Workspace/python_learning/venv/bin/activate ; python /Users/glenn.carson/Coding_Workspace/python_learning/ev_charging_>
