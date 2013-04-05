#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''
In this file are all Functions listed for Modbus communication
Its a simple wrapper for PyModbus, to make the functions
easier accessable.
'''

from pymodbus.client.sync import ModbusTcpClient

class ModbusClient():
    connected=False
    
    def __init__(self, *kwargs):
        self.connect()
    
    def connect(self):
        '''Open Modbus connection
        '''
        if not self.connected:
            self.client = ModbusTcpClient('192.168.50.238', port=502)
            self.client.connect()
            self.connected=True

    
    def send_array(self, array):
        '''Send the array to PLC
        
        :Parameters:
            `array`: list
                list with dictionaries of cubes
            
        :Returns:
            bool, True if sending went well. 
        '''
        if not self.connected:
            print("You don't have an open Modbus connection! - please restart server!")
            return False
        #check array size
        AMMOUNT_OF_CUBES=106
        c=0
        for cube in array: c+=1
        if c!= AMMOUNT_OF_CUBES:
            print("Array size isn't suitable. - size is: "+str(c)+" but it should be:"+str(AMMOUNT_OF_CUBES))
            return False  
        
        #write cubes into PLC
        lis = array
        c=0
        for cube in lis:
            try:
                #write x
                rq = self.client.write_register(c, cube['x'])
                c+=1
                #write y
                rq = self.client.write_register(c, cube['y'])
                c+=1
                #write z
                rq = self.client.write_register(c, cube['z'])
                c+=1
                #write rot
                rq = self.client.write_register(c, cube['typ'])
                c+=1
                #write type
                rq = self.client.write_register(c, cube['rot'])
                c+=1
            except:
                print("Can't send the cube data to PLC over Modbus")
        print("Cubes sent")
        return True
    