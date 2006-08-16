"""$Id$

Description goes here.

Copyright (C) 2006 Wyatt Baldwin, byCycle.org <wyatt@bycycle.org>

All rights reserved.

TERMS AND CONDITIONS FOR USE, MODIFICATION, DISTRIBUTION

1. The software may be used and modified by individuals for noncommercial, 
private use.

2. The software may not be used for any commercial purpose.

3. The software may not be made available as a service to the public or within 
any organization.

4. The software may not be redistributed.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR 
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
import sys, time

class Meter(object):
    def __init__(self, percentages=None, num_items=0, start_now=False):
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

        if start_now:
            self.startTimer()
        
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
            sys.stdout.write("\r%s" % (" " * self.length))

            # end marker
            sys.stdout.write("| Processing %s items\r" % self.num_items)

            # % done
            sys.stdout.write("%3s" % (self.percentages[self.per_idx]))
            
            self.per_idx+=1
            
            sys.stdout.write("%% |%s" % ("*" * self.per_idx))
            sys.stdout.flush()
            
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
    def __init__(self, start_now=True):
        self.start_time = 0
        self.elapsed_time = 0
        self.paused = True        
        self.elapsed_time = 0
        if start_now:
            self.start()
    
    def start(self):
        """Start the timer.

        Starting is just a special case of unpausing where we reset the
        elapsed time.

        """
        if not self.paused:
            return
        self.elapsed_time = 0
        self.unpause()
        
    def stop(self):
        self.pause()
        units = 'second'
        if self.elapsed_time > 60:
            self.elapsed_time /= 60.0
            units = 'minute'
        if self.elapsed_time != 1:
            units += 's'
        return '%.2f %s' % (self.elapsed_time, units)

    def pause(self):
        if self.paused:
            return        
        self.paused = True
        self.elapsed_time += (time.time() - self.start_time)

    def unpause(self):
        if not self.paused:
            return
        self.paused = False
        self.start_time = time.time()
