#!/home/u6/bycycle/bin/python -OO

import os
os.environ['PYTHON_EGG_CACHE'] = '/home/u6/bycycle/.python-eggs'

import sys
byCycle_path = '/home/u6/bycycle/byCycle/Live'
sys.path.insert(0, byCycle_path)

import tripplanner
if __name__ == '__main__':
    tripplanner.TripPlanner().run()
