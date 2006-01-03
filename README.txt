ReadMe for byCycle.
10/31/2005


Introduction
------------

The byCycle Trip Planner is a system for finding and planning trips made by bicycle. It uses different data modes and associated weighting functions to do trip planning for different datasets and travel modes. At the current time, the system only supports one mode at a time. In the future, we would like to extend the system to support multiple modes in a single trip.

The current version of the system is somewhat bike-centric. It needs some refactoring and changes in architecture to make it more generic and useable for other modes.

The system is being designed so that any interface (within reason) should be able to call the back end. To that end a RESTful web service interface has been implemented. The result is returned in JavaScript Object Notation (JSON). See http://www.bycycle.org/routefinder/rest.html for more info on that.

Using the web service, creating an AJAX interface (for example) should be fairly easy.


This Version
------------

This is version 0.3. 0.3 aims to... blah blah blah.


License
-------

This system is distributed under the terms of the GNU Public License (GPL), for noncommercial uses only. Commercial or business entities may not use this system for any purpose whatsoever without purchasing a license to do so. Please see the file LICENSE.txt for details of the GPL. Please contact us at licensing@bycycle.org to work out terms for commercial use.


Installation
------------
See the INSTALL file in this directory.


