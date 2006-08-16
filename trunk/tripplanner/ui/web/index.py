#!/usr/bin/python -OO

import sys
byCycle_path = '/home/u6/bycycle/byCycle/live'
sys.path.insert(0, byCycle_path)

import tripplanner
if __name__ == '__main__':
    tripplanner.TripPlanner().run()
