#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
RoboFlexMS-Server
=================

This is part of the machine "RoboFlexMS", which is built as
project by Dominique Burnand, Stephan Cortesi and Jonathan Osterwalder.
This Code-project is done by Dominique Burnand.
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
    
    
    def build_bahn(self, number):
        ''' /build_bahn page. 
        This function transfers the command further to the PLC. The PLC will load the Bahn Lager.
        
        :Parameters:
            `number`: int
        '''
        number=int(number)
        self.modbus.transfer_bahn_nr(number)
    build_bahn.exposed = True
        
    
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
        
        #invert coordinates x and y
        for cube in array:
            cube["x"]=cube["x"] * -1
            cube["y"]=cube["y"] * -1
        
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
            cube["rot"]=int(cube["rot"])
            if cube["rot"]==90:
                cube["rot"]=3
            elif cube["rot"]==180:
                cube["rot"]=2
            elif cube["rot"]==270:
                cube["rot"]=1
        
        #print umformated data
        for cube in array:
            print "output", cube
            pass
        
        #send data over modbus
        final=self.calculate(constant_data.depot, array)
        if not self.modbus.send_array(final):
            return False
        
        #read that bahn in the sps into array
        self.modbus.transfer_bahn_nr(10)
    process.exposed = True
    
    
    def calculate(self, lager1, bahn):
        '''This function calculates the new Bahn. 
        With depot
        '''
        lager=[]
        for cube in lager1:
            lager.append(cube)
        
        final=[]
        for i in lager:
            final.append(i)
            
        c=0
        for i in lager:
            c+=1
        
        for cube in bahn:
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
            #print 'Final cube', types[ind]
            
            lager.remove(types[ind])
            final.remove(types[ind])
            final.append(cube)
                
        c=1
        for i in final:
            #print c, i
            c+=1
        
        return final
        

#Start cherrypy server    
cherrypy.quickstart(Server(), config=CONFIGFILE)