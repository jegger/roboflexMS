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
        
        #print incomming data
        array= json.loads(data)
        for i in array:
            print "income:", i
        
        #get smalest x
        x=100
        y=100
        for cube in array:
            if cube["x"]<x:
                x=cube["x"]
            if cube["y"]<y:
                y=cube["y"]
        
        #overwrite coordinates in array, and convert them into int
        for cube in array:
            cube["x"]=int(cube["x"]-x+13)
            cube["y"]=int(cube["y"]-y)
            cube["z"]=int(cube["z"])
            cube["typ"]=int(cube["typ"])
        
        #print umformated data
        for cube in array:
            print "output", cube
            
        #send data over modbus
        final=self.calculate(constant_data.depot, array)
        if not self.modbus.send_array(final):
            return False
        
        #read that bahn in the sps into array
        self.modbus.transfer_bahn_nr(10)
    process.exposed = True
    
    def calculate(self, lager, anlage):
        """This function calculates the new Anlage. 
        With depot
        """
        '''Calculates the new anlage
        '''
        final=[]
        for i in lager:
            final.append(i)
            
        c=0
        for i in lager:
            c+=1
        
        for cube in anlage:
            typ=cube['typ']
            
            types=[]
            for cu in lager:
                if cu['typ']==typ:
                    types.append(cu)
            print len(types), "of", typ
            
            #highest cube in types
            z=0
            ind=-1
            for cu in types:
                if cu['z']>z:
                    ind=types.index(cu,)
            if ind==-1:
                print "No highest cube found"
                return False
            print 'Final cube', types[ind]
            
            lager.remove(types[ind])
            final.remove(types[ind])
            final.append(cube)
                
        c=1
        for i in final:
            print c, i
            c+=1
        
        return final
        

#Start cherrypy server    
cherrypy.quickstart(Server(), config=CONFIGFILE)