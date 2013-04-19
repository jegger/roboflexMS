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
import time

#get configuration-file
CONFIGFILE = os.path.join(os.path.dirname(__file__), 'server.conf')

class Server(object):
    '''Represent the CherryPy server class.
    '''
    def __init__(self, *kwargs):
        #create modbus object
        self.modbus=modbus.ModbusClient()
        self.last_request=0
        
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
        if time.time()-self.last_request<6:
            time.time()
            print "you pressed again to soon"
            return
        self.last_request=time.time()
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
        if time.time()-self.last_request<6:
            time.time()
            print "you pressed again to soon"
            return
        self.last_request=time.time()
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
        if not final:
            print "CANT SEND BAHN - INVALID DATA"
            return False
        if not self.modbus.send_array(final):
            return False
        
        #read that bahn in the sps into array
        self.modbus.transfer_bahn_nr(10)
    process.exposed = True
    
    
    def calculate(self, lager1, bahn):
        '''This function calculates the new Bahn. 
        With depot
        '''
        #create temp. dicts
        lager=[]
        for cube in lager1:
            lager.append(cube)
        
        final=[]
        for i in lager:
            final.append(i)
                    
        #Pass every cube in bahn
        for cube in bahn:
            
            #fetch typ of cube
            typ=cube['typ']
            
            #get all cubes from the lager which have the same typ as the current cube
            types=[]
            for cu in lager:
                if cu['typ']==typ:
                    types.append(cu)
            print len(types), "cubes of type", typ, "available"
            
            #highest cube in types
            z=0
            ind=-1
            for cu in types:
                if cu['z']>=z:
                    ind=types.index(cu,)
            if ind==-1:
                print "No highest cube found", "To much("+str(len(types))+") cubes of type:"+str(typ), "max cubes:"
                return False
            
            #remove cube out of lager
            lager.remove(types[ind])
            final.remove(types[ind])
            #add cube to final array which will sent to the PLC
            final.append(cube)
        
        #Check if the final array has the same size as the lager array (no cube got lost)
        if len(final)!=len(lager1):
            print "Cube(s) got lost:", len(final), "of", len(lager1)
            return False
        
        return final
        

#Start cherrypy server    
cherrypy.quickstart(Server(), config=CONFIGFILE)