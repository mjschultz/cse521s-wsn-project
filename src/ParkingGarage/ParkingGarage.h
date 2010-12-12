/* 
 * Matt Lindsay
 * CSE521S project
 * ParkingGarage is is part of a parking guidance and information system
 * designed to take advantage of the TelosB and an analog range finder.
 */

#ifndef PARKING_GARAGE_H
#define PARKING_GARAGE_H

typedef nx_struct parking_garage_config_msg
{
	nx_uint16_t parking_space_id;
	nx_uint16_t packet_id;
	nx_uint16_t new_parking_space_id;
	nx_uint16_t status_interval;
} parking_garage_config_msg_t;

typedef nx_struct parking_garage_status_msg
{
	nx_uint16_t parking_space_id;
	nx_uint16_t packet_id;
    nx_uint16_t sensor;
	nx_uint16_t sensor_value;
} parking_garage_status_msg_t;

typedef nx_struct parking_garage_status_debug_msg
{
	nx_uint16_t parking_space_id;
	nx_uint16_t packet_id;
	nx_uint16_t light_sensor;
	nx_uint16_t passive_ir_sensor;
	nx_uint16_t temp_sensor;
	nx_uint16_t humid_sensor;
	nx_uint16_t active_ir_sensor;
	nx_uint16_t minutes_occupied;
} parking_garage_status_debug_msg_t;

typedef nx_struct parking_garage_command_msg
{
	nx_uint16_t parking_space_id;
	nx_uint16_t packet_id;
	nx_uint16_t online_status;
	nx_uint16_t data;
} parking_garage_command_msg_t;

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
	IR_LIGHT = 4,
	/*
	 * Add new sensors here and increment NUMBER_OF_SENSORS
	 */
	NUMBER_OF_SENSORS = 5
};

#endif
