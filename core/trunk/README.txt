ReadMe for byCycle Trip Planner
01/28/2006


Introduction
------------

The byCycle Trip Planner is a system for planning trips made by bicycle. 
Other travel modes are possible but none have been implemented yet.

The system uses data modes and associated weighting functions to do trip 
planning for different datasets (e.g., geographic regions) and travel modes.

The system is being designed so that any interface (within reason) should be 
able to call the back end. To that end a RESTful web service interface has 
been implemented. By default, the result is returned in JavaScript Object 
Notation (JSON), which can easily be parsed in most programming languages. 
Future implementations should allow users to specify a preferred format 
(e.g., XML).

Note: We need to produce some docs for the web service interface.


This Version
------------

This is version 0.3.?. 0.3 is a big jump from 0.2. It includes facilities for 
easily incorporating and using new sets of regional data. It also includes 
enhanced dynamic functionality in the user interface (using DHTML & AJAX).


License and Warranty
--------------------

Please see the file LICENSE.txt for more details regarding the license and
warranty.


Installation
------------

See the INSTALL file in this directory.


More Information
----------------

Information about the byCycle project can be found at http://byCycle.org/. 
Information about the Trip Planner in particular can be found at 
http://byCycle.org/tripplanner/.


Contact
-------

You can contact us to ask questions, make comments, offer suggestions, get 
help, offer help, etc at contact@bycycle.org or by going to 
http://byCycle.org/contact.html and using the form there.
