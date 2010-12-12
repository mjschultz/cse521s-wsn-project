/* -*- Mode: C; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- */
/*
 * serial.h
 * Copyright (C) Matt Lindsay 2010 <matthew.scott.lindsay@gmail.com>
 *
 * CSE521S project
 * Gateway is is part of a parking guidance and information system
 * designed to take advantage of the TelosB and an analog range finder.
 * 
 */

#ifndef _SERIAL_H_
#define _SERIAL_H_

typedef unsigned long long UINT64;
typedef unsigned int UINT32;
typedef unsigned short UINT16;
typedef unsigned char UINT8;

#include "packets.h"

extern "C"
{
	#include "serialsource.h"
}

class Serial
{
public:
	Serial();
	~Serial();

	void SetDevice(const char *setDevice);
	const char* GetDevice();

	void SetBaudRate(char *setBaud_rate);
	char* GetBaudRate();
	bool Receive(UINT8 *message_type, parking_garage_packet<parking_garage_status_msg> *status_buffer, parking_garage_packet<parking_garage_status_debug_msg> *status_debug_buffer);

	template <typename PACKET_STRUCT>
		bool SendPacket(UINT16 dest_addr, UINT16 src_addr, UINT8 group_id, UINT8 active_msg_handler ,PACKET_STRUCT *structToSend)
		{
			parking_garage_packet<PACKET_STRUCT> packet;

			packet.header.AMPacket = 0;
			packet.header.dest_addr = dest_addr;
			packet.header.src_addr = src_addr;
			packet.header.msg_length = sizeof(PACKET_STRUCT);
			packet.header.group_id = group_id;
			packet.header.active_msg_handler = active_msg_handler;

			packet.payload = *structToSend;
			
			if (write_serial_packet(src, &packet, sizeof(packet)) == 0)
			{
				return true;
			}
			else
			{
				return false;
			}
		}
	bool OpenSource();
	void swapEndian(UINT16* data);

protected:

private:
	static const char *msgs[];
	const char *device; 
	char *baud_rate;
						
	void stderr_msg(serial_source_msg problem);

	serial_source src;

};

#endif // _SERIAL_H_
