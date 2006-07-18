#!/home/bycycle/bin/python -OO

import os
os.environ['PYTHON_EGG_CACHE'] = '/home/bycycle/.python-eggs'

import tripplanner
if __name__ == '__main__':
    tripplanner.TripPlanner().run()
