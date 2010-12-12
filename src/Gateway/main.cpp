/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- */
/*
 * main.cpp
 * Copyright (C) Matt Lindsay 2010 <matthew.scott.lindsay@gmail.com>
 *
 * CSE521S project
 * Gateway is is part of a parking guidance and information system
 * designed to take advantage of the TelosB and an analog range finder.
 * 
 */

#define MAX_NUMBER_SPACES_PER_BASESTATION 100

#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

#include "serial.h"
#include "curl.h"

using namespace std;

typedef struct thread_info
{
	pthread_t thread_id;
	UINT16 *command;
};

typedef struct meter_info
{
	UINT16 parking_space_id;
	UINT16 packet_id;
	UINT16 light_sensor;
	UINT16 passive_ir_sensor;
	UINT16 temp_sensor;
	UINT16 humid_sensor;
	UINT16 active_ir_sensor;
	UINT16 minutes_occupied;
};

void printStatusMessage(parking_garage_packet<parking_garage_status_msg> *msg)
{
	system("clear");
	cout << "STATUS_MESSAGE" << endl;
	cout << "Status:parking_space_id = " << msg->payload.parking_space_id << endl;
	cout << "Status:packet_id = " << msg->payload.packet_id << endl;
	cout << "Status:sensor = " << msg->payload.sensor << endl;
	cout << "Status:sensor_value = " << msg->payload.sensor_value << endl << endl;
	cout << endl << endl << endl << endl;
}

void printDebugMessage(parking_garage_packet<parking_garage_status_debug_msg> *msg)
{
	system("clear");
	cout << "STATUS_DEBUG_MESSAGE" << endl;
	cout << "Debug:parking_space_id = " << msg->payload.parking_space_id << endl;
	cout << "Debug:packet_id = " << msg->payload.packet_id << endl;
	cout << "Debug:light_sensor = " << msg->payload.light_sensor << endl;
	cout << "Debug:passive_ir_sensor = " << msg->payload.passive_ir_sensor << endl;
	cout << "Debug:temp_sensor = " << msg->payload.temp_sensor << endl;
	cout << "Debug:humid_sensor = " << msg->payload.humid_sensor << endl;
	cout << "Debug:active_ir_sensor = " << msg->payload.active_ir_sensor << endl;
	cout << "Debug:actual_active_ir_sensor = " << msg->payload.minutes_occupied << endl << endl;
}

void printMenu()
{
	cout << "Menu:" << endl;
}

UINT16 addNewMeter(meter_info *meters[], UINT16 *space_id)
{
	for(UINT16 i; i < MAX_NUMBER_SPACES_PER_BASESTATION; i++)
	{
		if(meters[i]->parking_space_id == *space_id)
		{
			return i;
		}
	}
	return 1;
}

int main()
{	
	Serial serial;
	Curl curl;
	
    char device[] = "/dev/tty.usbserial-XBTFSM1C";
    char baudRate[] = "115200";

    UINT16 command = 0;
    thread_info info;

    info.command = &command;
 
   		
	serial.SetDevice(device);
	serial.SetBaudRate(baudRate);
	while(!serial.OpenSource())
	{
		sleep(5);
	}
			
	system("clear");
	fprintf(stdout,"***-Gateway Started-***\n\n");

    parking_garage_packet<parking_garage_status_msg> status_buffer;
    parking_garage_packet<parking_garage_status_debug_msg> status_debug_buffer;
    parking_garage_packet<parking_garage_config_msg> config_buffer;
 //   parking_garage_packet<parking_garage_command_msg> command_buffer;

    UINT8 message_type;
    UINT8 config_packet_id = 0;
    bool config_one_time = false;

	while(true)
	{
        if(serial.Receive(&message_type, &status_buffer, &status_debug_buffer))
		{
            switch ( message_type )
            {
                case PARKING_GARAGE_STATUS_MSG:
	                printStatusMessage(&status_buffer);
                    break;
                case PARKING_GARAGE_STATUS_DEBUG_MSG:
	                printDebugMessage(&status_debug_buffer);
	
					if(status_debug_buffer.payload.parking_space_id != 0)
                    {
                        config_one_time = false;
                    }

                    if(status_debug_buffer.payload.parking_space_id == 0 && !config_one_time)
                    {
                        cout << "Found new mote!\nEnter Parking_Space_ID" << endl;
                        cin >> config_buffer.payload.new_parking_space_id;

                        config_buffer.payload.parking_space_id = 0;
                        config_buffer.payload.packet_id = config_packet_id;
                        config_buffer.payload.status_interval = 1;                     
                        config_buffer.fix_endian();

                        for(int i = 0; i<5; i++)
                        {
                            serial.SendPacket<parking_garage_config_msg>(0xffff, 0, 1, PARKING_GARAGE_CONFIG_MSG ,&config_buffer.payload);
                            usleep(100);
                        }

                        config_one_time = true;
                    }
					else
					{
						if(status_debug_buffer.payload.parking_space_id < 60000)
						{
							curl.putSpace(status_debug_buffer.payload.parking_space_id, status_debug_buffer.payload.active_ir_sensor, status_debug_buffer.payload.light_sensor, status_debug_buffer.payload.temp_sensor);
						}
						if(status_debug_buffer.payload.active_ir_sensor == 0)
						{
							cout << endl << "** Space Vacant **" << endl;
						}
						else if(status_debug_buffer.payload.active_ir_sensor == 1)
						{
							cout << endl << "** Space Occupied **" << endl;
						}
						else
						{
							cout << endl << "** Bad Value **" << endl;
						}
					}
                    break;
                default:
                    break;
            }
            //printMenu();
		}
        else
        {
			
	        // No Packets
        }
	}
    
    return 0;
}
