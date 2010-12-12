/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- */
/*
 * serial.cpp
 * Copyright (C) Matt Lindsay 2010 <matthew.scott.lindsay@gmail.com>
 *
 * CSE521S project
 * Gateway is is part of a parking guidance and information system
 * designed to take advantage of the TelosB and an analog range finder.
 * 
 */

#include <stdio.h>
#include <stdlib.h>

#include "serial.h"

const char *Serial::msgs[] = {	
	"unknown_packet_type",
	"ack_timeout",
	"sync",
	"too_long",
	"too_short",
	"bad_sync",
	"bad_crc",
	"closed",
	"no_memory",
	"unix_error"
};

Serial::Serial()
{	
}

Serial::~Serial()
{
}

void Serial::SetDevice(const char *setDevice)
{
	device = setDevice;
}

const char* Serial::GetDevice()
{
	return device;
}

void Serial::SetBaudRate(char *setBaud_rate)
{
	baud_rate = setBaud_rate;
}

char* Serial::GetBaudRate()
{
	return baud_rate;
}

void Serial::stderr_msg(serial_source_msg problem)
{
	fprintf(stderr, "Note: %s\n", msgs[problem]);
}

bool Serial::OpenSource()
{
	src = open_serial_source(device, platform_baud_rate(baud_rate), 1, NULL);

	if(!src)
	{
		fprintf(stderr, "Couldn't open serial port at %s:%s\n", device, baud_rate);
		return false;
	}
	else
	{
		return true;
	}
}

void Serial::swapEndian(UINT16* data)
{
	UINT8 *dataPtr = (UINT8*)data;
	UINT16 buffer;
	UINT8 *bufferPtr = (UINT8*)(&buffer);
	
	bufferPtr[1] = dataPtr[0];
	bufferPtr[0] = dataPtr[1];

	*data = buffer;
}

bool Serial::Receive(UINT8 *message_type, parking_garage_packet<parking_garage_status_msg> *status_buffer, parking_garage_packet<parking_garage_status_debug_msg> *status_debug_buffer)
{
	int len;
	const UINT8 *packet = (const UINT8*)read_serial_packet(src, &len);
	UINT8 *buffer = (UINT8*)packet;
	
	if (packet)
	{
		*message_type = buffer[7];
		switch ( buffer[7] )
		{
         case PARKING_GARAGE_STATUS_MSG:
	         if(len == sizeof(parking_garage_packet<parking_garage_status_msg>))
		     {
			     *status_buffer = *((parking_garage_packet<parking_garage_status_msg>*)buffer);
			     status_buffer->fix_endian();
		     }
	         else
		     {
			     fprintf(stderr,"ERROR: Not all of parking_garage_packet<parking_garage_status_msg> recieved\n");
			     return false;
		     }
            break;
         case PARKING_GARAGE_STATUS_DEBUG_MSG:
	         if(len == sizeof(parking_garage_packet<parking_garage_status_debug_msg>))
		     {
			     *status_debug_buffer = *((parking_garage_packet<parking_garage_status_debug_msg>*)buffer);
			     status_debug_buffer->fix_endian();
		     }
	         else
		     {
			     fprintf(stderr,"ERROR: Not all of parking_garage_packet<parking_garage_status_debug_msg> recieved\n");
			     return false;
		     }
            break;
         default:
            return false;
            }

		free((void *)packet);
		return true;
	}
	else
	{
		return false;
	}
}
