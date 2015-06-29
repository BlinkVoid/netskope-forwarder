# netskope-forwarder
syslog forwarder for netskope.

This application will use the RESTful API interface created at https://github.com/joshmad/netskope to pull all of the log files at a set interval and convert them to a syslog format and forward them to a syslog server. 

###Requirements
httplib2 0.9.1
netskope 0.1 (currently in development)

###Currently In Development
1. Run as a cron job and track the last timestamp in a temp file. Run on a schedule
2. Use the syslog handler in the Python Standard Library
3. handle pagination - for corporate use

###Long term
1. Run as a daemon
2. multithread (depending on enterprise scale workloads)

###Notes
No Splunk or ElasticSearch interface will be created. It is recommended that you use LogStash if you want to push the syslog to different indexing systems.
