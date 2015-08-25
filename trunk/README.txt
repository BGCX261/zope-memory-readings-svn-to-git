zope-memory-readings
********************

:Author: Peter Bengtsson, Fry-IT, peter@fry-it.com
:License: ZPL

Graphing a Zope's memory usage and correlating this with URLs. With
this you can hopefully find out what URLs requested are causing
massive memory increases for your Zope. 

See examplereport.png for what the report will look like (assuming it
hasn't changed too much since the latest release).

More info available here: http://code.google.com/p/zope-memory-readings/

Basic usage (for the impatient)
===============================

Unpack the scripts and run get_readings.py::

 $ python get_readings.py /path/to/running/zope/instance
 
Let it run, the hit Ctrl-C and it should print the path to the report
which you open with Firefox. 


Credits: Doug Hellmann for CommandLineApp
http://blog.doughellmann.com/2007/08/commandlineapp.html