ReadMe for byCycle Trip Planner
01/28/2006


Introduction
------------

The byCycle Trip Planner is a system for finding and planning trips made by 
bicycle (other travel modes are possible but none have been implemented yet). 
It uses different data modes and associated weighting functions to do trip 
planning for different datasets and travel modes.

The system is being designed so that any interface (within reason) should be 
able to call the back end. To that end a RESTful web service interface has 
been implemented. The result is returned in JavaScript Object Notation (JSON). 
See http://www.bycycle.org/tripplanner/rest.html for more info on that.

Using web services, creating an AJAX-enhanced Web interface (for example) 
should be fairly easy (and, in fact, this is what we have done for the latest 
version).


This Version
------------

This is version 0.3. 0.3 is a big jump from 0.2. It includes facilities for 
easily incorporating and using new sets of data. It also includes enhanced
dynamic functionality in the user interface (using DHTML & AJAX). The next minor
release will reincorporate "traditional" non-AJAX queries (the current version 
makes queries via AJAX only).


License and Warranty
--------------------

This system is distributed under the terms of the GNU Public License (GPL), 
for noncommercial uses only. Commercial or business entities may not use this 
system for any purpose whatsoever without making special arrangements with us to 
do so. 

There is NO WARRANTY of any kind.

Please see the file LICENSE.txt for more details regarding the license and
warranty.


Installation
------------

See the INSTALL file in this directory.


More Information
----------------

Information about the byCycle project can be found at http://www.byCycle.org/. 
Information about the Trip Planner in particular can be found at 
http://www.byCycle.org/tripplanner/.


Contact
-------

You can contact us to ask questions, make comments, offer suggestions, get 
help, offer help, etc at support@bycycle.org or by going to 
http://www.byCycle.org/contact.html and using the form there (it will allow 
you to send anonymous messages).
