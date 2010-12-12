/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- */
/*
 * main.h
 * Copyright (C) Matt Lindsay 2010 <matthew.scott.lindsay@gmail.com>
 *
 * CSE521S project
 * Gateway is is part of a parking guidance and information system
 * designed to take advantage of the TelosB and an analog range finder.
 * 
 */

#ifndef _PACKETS_H_
#define _PACKETS_H_

#pragma pack(push,1)
typedef struct packet_header
{
    UINT8 AMPacket;
    UINT16 dest_addr; // Destination address (2 bytes)
    UINT16 src_addr; // Link source address (2 bytes)
    UINT8 msg_length; // Message length (1 byte)
    UINT8 group_id; // Group ID (1 byte)
    UINT8 active_msg_handler; // Active Message handler type (1 byte) 

    void swapEndian(UINT16* data)
    {
        UINT8 *dataPtr = (UINT8*)data;
        UINT16 buffer;
        UINT8 *bufferPtr = (UINT8*)(&buffer);
	
        bufferPtr[1] = dataPtr[0];
        bufferPtr[0] = dataPtr[1];

        *data = buffer;
    }

    void fix_endian()
    {
        swapEndian( &dest_addr );
        swapEndian( &src_addr );
    }

} packet_header_msg_t;

typedef struct parking_garage_config_msg
{
	UINT16 parking_space_id;
	UINT16 packet_id;
	UINT16 new_parking_space_id;
	UINT16 status_interval;
} parking_garage_config_msg_t;

typedef struct parking_garage_status_msg
{
 	UINT16 parking_space_id;
 	UINT16 packet_id;
 	UINT16 sensor;
    UINT16 sensor_value;
} parking_garage_status_msg_t;

typedef struct parking_garage_status_debug_msg
{
	UINT16 parking_space_id;
	UINT16 packet_id;
	UINT16 light_sensor;
	UINT16 passive_ir_sensor;
	UINT16 temp_sensor;
	UINT16 humid_sensor;
	UINT16 active_ir_sensor;
	UINT16 minutes_occupied;
} parking_garage_status_debug_msg_t;

typedef struct parking_garage_command_msg
{
	UINT16 parking_space_id;
	UINT16 packet_id;
	UINT16 online_status;
	UINT16 data;
} parking_garage_command_msg_t;

template <typename PAYLOAD_STRUCT>
struct parking_garage_packet
{
    packet_header header;
    PAYLOAD_STRUCT payload;

    void swapEndian(UINT16* data)
    {
        UINT8 *dataPtr = (UINT8*)data;
        UINT16 buffer;
        UINT8 *bufferPtr = (UINT8*)(&buffer);
	
        bufferPtr[1] = dataPtr[0];
        bufferPtr[0] = dataPtr[1];

        *data = buffer;
    }

    void fix_endian()
    {
        UINT16 *buffer = (UINT16*)(&payload);

        for( UINT16 i = 0; i < (sizeof(PAYLOAD_STRUCT)/2); i++)
        {
            swapEndian(&buffer[i]);
        }
    }
    
};

#pragma pack(pop)

enum
{ 
	// Message Structures 
	PARKING_GARAGE_CONFIG_MSG = 200,
	PARKING_GARAGE_STATUS_MSG = 201,
	PARKING_GARAGE_STATUS_DEBUG_MSG = 202,
	PARKING_GARAGE_COMAND_MSG = 203,
};

enum
{
	// Packets
	/*
	 * Error Messages 0 - 10
	 *	0 - General Error
	 */
	ERROR_MESSAGE = 0,

	/*
	 * Config Messages 11 - 20
	 *	11 - Setup Message
	 */
	CONFIG_SETUP_MESSAGE = 11,

	/*
	 * Sensor Messages 21 - 90
	 *	21 - Sensor Light
	 */
	SENSOR_LIGHT = 21,

	/*
	 * Debug Messages 91+
	 *	91 - All Sensors
	 */
	DEBUG_MESSAGE = 91,
};

enum
{
	ADC1 = 0,
	TEMPERATURE = 1,
	HUMIDITY = 2,
	LIGHT = 3,
	IR = 4,
};

#endif
