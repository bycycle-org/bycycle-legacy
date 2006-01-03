"""
$$$
:Author: Wyatt Baldwin
:Copyright: 2005 byCycle.org
:License: GPL
:Version: 0
:Date: 15 Aug 2005
$$$

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
ERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import sys, time

class Meter(object):
    def __init__(self, percentages=None, num_items=0):
        # The percentages of items at which to update the progress meter
        self.percentages = percentages or \
                           [1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90]
        while self.percentages[-1] >= 100: self.percentages.pop()
        self.percentages.append(100)
        self.per_len = len(self.percentages)

        # Reset these after last update (i.e., at 100%)
        self.num_items = num_items
        self.per_idx = -1
        self.update_points = None
        self.warned = False
        self.start_time = None

        self.setNumberOfItems(num_items)

        self.length = 6 + self.per_len

    def startTimer(self):
        if self.start_time:
            print "Progress Meter timer already started."
            return
        self.start_time = time.time()

    def setNumberOfItems(self, num_items):
        if not num_items or self.update_points: return
        self.num_items = num_items
        self.per_idx = 0
        self.update_points = [int(num_items * p * .01)
                              for p in self.percentages]

    def update(self, item_number):
        if not self.update_points:
            self.warn()
            return False

        # Update the progress meter if current item number is an update point
        if item_number == self.update_points[self.per_idx]:
            sys.stdout.write("\r")
            for i in range(self.length): sys.stdout.write(" ")

            # end marker
            sys.stdout.write("| Processing %s items\r" % self.num_items)

            # % done
            sys.stdout.write("%3s" % (self.percentages[self.per_idx]))
            
            sys.stdout.write("% ")
            sys.stdout.write("|") # start marker
            for i in range(self.per_idx): sys.stdout.write("*")
            self.per_idx+=1

            if item_number == self.update_points[-1]:
                self.printElapsedTime(item_number)
                self.reset()

            return True

        return False

    def printElapsedTime(self, last_item_number):
        """Print elapsed number of seconds since the timer was started (if it was)."""
        if self.start_time:
            elapsed_time = int(round(time.time() - self.start_time))
            units = "seconds"
            if elapsed_time > 59:
                elapsed_time = "%.2s" % (elapsed_time / 60.)
                units = "minutes"
            sys.stdout.write("| %s items took %s %s to process" % \
                (last_item_number, elapsed_time, units))

    def reset(self):
        self.num_items = 0
        self.per_idx = -1
        self.update_points = None
        self.warned = False
        self.start_time = None

    def warn(self):
        if self.warned: return
        self.warned == True
        print "Progress Meter was not initialized."


class Timer(object):
    """Super simple wall clock timer."""    
    def __init__(self):
        self.start_time = 0
        self.end_time = 0
        self.elapsed_time = 0
    
    def startTiming(self, msg):
        self.start_time = time.time()
        print 'Timer started. %s' % msg
        
    def stopTiming(self):
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        units = 'second'
        if self.elapsed_time > 60:
            self.elapsed_time /= 60.0
            units = 'minute'
        if self.elapsed_time != 1:
            units += 's'
        print "Timer stopped after %.2f %s." % (self.elapsed_time, units)

    def getElapsedTime(self):
        return 
