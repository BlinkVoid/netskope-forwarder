#!/usr/bin/env python

__author__ = 'Josh Madeley'
__version__ = '0.1'

'''
THIS APPLICATION WILL CONNECT TO THE NETSKOPE API AND PULL ALL THE RWEQUIRED EVENTS
AND FORWARD THEM TO A SYSLOG SERVER. THE CONFIGURATION ITEMS WILL BE DONE USING ARGPARSE
'''

import netskope
import logging
from logging.handlers import SysLogHandler
import argparse
#import json
import time
import sys
import ConfigParser
import os


parser = argparse.ArgumentParser(description='TBD')
parser.add_argument('--syslogserver', dest='syslogserver', default='127.0.0.1', required=False,help='IP or Hostname of the syslog server')
parser.add_argument('--syslogport', dest='syslogport', default='514',required=False,help='UDP port of the syslog server')
parser.add_argument('--daemonize', dest='daemonize', default=False, required=False, help='Run as a daemon. Default is to run once and schedule via Cron')
parser.add_argument('--loglevel', dest='loglevel', default='INFO', required=False, help='Set log level')
parser.add_argument('--logfile', dest='logfile', default='netskope-forwarder.log', required=False, help='set the log location')
parser.add_argument('--configfile', dest='configfile', required=False, help='Set\'s the config file location. This file must be formated in an INI style')
parser.add_argument('--tenant', dest='tenant', required=False, help='Used when no config file is present and sets the tenant server')
parser.add_argument('--token', dest='token', required=False, help='Used when no config file is present and sets the token')
parser.add_argument('--events', dest='events', required=False, default='none', help='What events should be forwarded - comma seperated connection | application | audit | all | None (default)')
parser.add_argument('--alerts', dest='alerts', required=False, default='none', help='What alert events should be forwarded - comma seperated policy | dlp | watchlist | all | None (default)' )
parser.add_argument('--timeperiod', dest='timeperiod', required=False, default=3600, help='What time period should be used 3600 (default) | 86400 | 604800 | 2592000')

args = parser.parse_args()

######################################################
#SET GLOBAL VARIABLES
######################################################
syslogserver = str(args.syslogserver)
syslogport = int(args.syslogport)
daemonize = str(args.daemonize)
loglevel = str(args.loglevel)
logfile = str(args.logfile)
configfile = str(args.configfile)
tenant = str(args.tenant)
token = str(args.token)
events = str(args.events)
alerts = str(args.alerts) 
timeperiod = int(args.timeperiod)

section = 'netskope-forwarder'
######################################################
#LOGGING CONFIG
######################################################
#APPLICATION LOGGER
log2disk = logging.getLogger('log2disk')
formatter = logging.Formatter('%(asctime)s : %(message)s')
fileHandler = logging.FileHandler(logfile)
fileHandler.setFormatter(formatter)
log2disk.setLevel(loglevel)
log2disk.addHandler(fileHandler)

#SYSLOGGER FOR FORWARDING
log2syslog = logging.getLogger('log2syslog')
log2syslog.setLevel(logging.INFO)
syslog = SysLogHandler((syslogserver,syslogport))
log2syslog.addHandler(syslog)

######################################################
#INPUT VALIDATION
######################################################
if configfile != 'None':
	None
elif (token != 'None') and (tenant != 'None'):
	None
else:
	print 'either a configfile needs to be set or a token/tenant pair needs to be set'
	sys.exit(1)
######################################################
def syslogforward(type):
	None

def gettime():
	
	return str(int(time.mktime(time.gmtime())))

def writelastrun(epochtime):
	
	lastrun = epochtime
	
	config = ConfigParser.RawConfigParser()
	config.add_section(section)
	config.set(section, 'lastrun', lastrun)
	
	with open(section + '.cfg', 'wb') as configfile:
		config.write(configfile)
	
	config = None
	
	return True

def getlastrun():
	
	if os.path.isfile(section + ".cfg") == False:
		writelastrun('1120057257')
	
	config = ConfigParser.ConfigParser()
	config.read(section + '.cfg')
	lastrun = config.get(section, 'lastrun')
	config = None
	
	return lastrun
	
def getlogs(netskopeobj, endpoint, startend):
	
	if endpoint.lower() == 'events':
		 if events.lower != 'none':
		 	if events.lower() == 'all':
		 		eventtypes = ['connection', 'application', 'audit']
		 	else:
		 		eventtypes = events.split(',')
		 	
		 	for eventtype in eventtypes:
		 		eventjson =netskopeobj.events('', eventtype, startend=startend)
		 		numitems = len(eventjson['data'])
		 		log2disk.info('Event: %s NumItems: %s' % (eventtype, numitems))
		 		if numitems > 0:
		 			for line in eventjson['data']:
		 				msg = "%s netskope type=%s" % (str(time.strftime('%Y-%m-%dT%H:%M:%SZ')), eventtype)
		 				for k,v in line.iteritems():
		 					msg = "%s %s='%s'" % (msg.strip(), k, v)
		 				print msg
		 				log2syslog.info(msg)
		 else:
		 	pass
	elif endpoint.lower() == 'alerts':
		None
	else:
		return False

def main():
	
	log2disk.info("Netskope-Forwarder v%s started successfully" % (__version__))
	endtime = gettime()
	starttime = getlastrun()
	
	log2disk.info("Starttime: %s" % starttime)
	log2disk.info("Endtime: %s" % endtime)
	
	startend = [starttime, endtime]
	
	netsk = netskope.netskope(token, tenant, debug=False)

	getlogs(netsk, 'events', startend)
	getlogs(netsk, 'alerts', startend)
	
	if writelastrun(endtime):
		log2disk.info("successfully recorded endtime to config")
	log2disk.info("-"*40)
	
if __name__ == '__main__':
	main()