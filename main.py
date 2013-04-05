#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
RoboFlexMS-Server
=================

This is part of the machine "RoboFlexMS", which is built as
project by Dominique Burnand, Stephan Cortesi and Jonathan Osterwalder
@msw-Winterthur. http://www.msw.ch

This server is the bridge between the iPad application and the ABB
AC-500 PLC. This application receives the data over CherryPy and sends
it over PyModbus to the PLC.

The data gets send synchronous! - You can expect a hang of 1-2sec.
(This isn't a bug)
'''

import cherrypy
import os.path
import json
import modbus
import constant_data

#get configuration-file
CONFIGFILE = os.path.join(os.path.dirname(__file__), 'server.conf')

class Server(object):
    '''Represent the CherryPy server class.
    '''
    def __init__(self, *kwargs):
        #create modbus object
        self.modbus=modbus.ModbusClient()
        
    def index(self):
        '''Readme start page
        
        :Returns:
            str, Radme page.
        '''
        return 'This is a server for the Project RoboflexMS. Send your data to /process via POST in a JSON'
    index.exposed = True
    
    def process(self, data):
        '''/process page. This page receives the JSON-data (of the cubes
        over POST and process them further (transfer them to the PLC).
        
        :Parameters:
            `data`: str
                JSON data containing all the cubes
            
        :Returns:
            bool, True if the processing went well. 
        '''
        #check if data is sent
        if not data:
            return 'please send JSON over POST'
        
        print data
        array= json.loads(data)
        for i in array:
            print i 
            
        #send data over modbus
        if not self.modbus.send_array(constant_data.depot):
            return False
        
    process.exposed = True
        

#Start cherrypy server    
cherrypy.quickstart(Server(), config=CONFIGFILE)