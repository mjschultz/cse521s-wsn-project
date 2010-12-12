/* 
 * Matt Lindsay
 * CSE521S project
 * ParkingGarage is is part of a parking guidance and information system
 * designed to take advantage of the TelosB and an analog range finder.
 */

module ParkingGarageC {//}@safe(){
	uses
	{
		interface Boot;
		interface SplitControl as RadioControl;
		interface Packet;
		interface Receive as ConfigReceive;
		interface Receive as CommandReceive;
		interface AMSend as StatusSend;
		interface AMSend as StatusDebugSend;
		interface Leds;
		interface Timer<TMilli> as StatusTimer;
		interface Timer<TMilli> as SensorTimer;
		interface Timer<TMilli> as LEDTimer;
		interface Timer<TMilli> as TimeoutTimer;
		interface Read<uint16_t> as AdcC1;
		interface Read<uint16_t> as Temp;
		interface Read<uint16_t> as Humid;
		interface Read<uint16_t> as Light;
		interface Read<uint16_t> as IR;
		interface Notify<button_state_t> as ButtonNotify;  
	}
}
implementation {

	uint16_t sensor_max = 0;
	uint16_t sensor_min = 0;
	uint16_t sensor_config = 0;
	uint16_t actual_active_ir_sensor = 0;
	uint16_t carPresentThreshold = 0;
	uint16_t parkingSpaceID = 0;
	uint16_t statusPacketID = 0;
	uint16_t statusDebugPacketID = 0;
	uint16_t numberOfReads = 10;
	uint16_t read_count[NUMBER_OF_SENSORS];
    uint16_t temp_sensor_value[NUMBER_OF_SENSORS];
    uint16_t sensor_value[NUMBER_OF_SENSORS];
	message_t buf;

	task void sendStatusMessage();
	task void sendStatusDebugMessage();
	task void readAdcC1();
	task void readTemp();
	task void readHumid();
	task void readLight();
	task void readIR();
	void ComposeStatusMessage(parking_garage_status_msg_t *msg, uint16_t sensor);
	void ComposeStatusDebugMessage(parking_garage_status_debug_msg_t *msg);
	int ReadAllSensors();

	task void sendStatusMessage()
	{
		parking_garage_status_msg_t * payload = (parking_garage_status_msg_t *)call Packet.getPayload(&buf, sizeof(parking_garage_status_msg_t));
		
		// TODO - add a queue of status message sensors
		ComposeStatusMessage(payload, LIGHT);

		if(call StatusSend.send(AM_BROADCAST_ADDR, &buf, sizeof(parking_garage_status_msg_t)) != SUCCESS)
		{	
                  post sendStatusMessage();
		}
	}

	task void sendStatusDebugMessage()
	{
		parking_garage_status_debug_msg_t * payload = (parking_garage_status_debug_msg_t *)call Packet.getPayload(&buf, sizeof(parking_garage_status_debug_msg_t));
		
		ComposeStatusDebugMessage(payload);

		if(call StatusDebugSend.send(AM_BROADCAST_ADDR, &buf, sizeof(parking_garage_status_debug_msg_t)) != SUCCESS)
		{	
                  post sendStatusDebugMessage();
		}
	}

	task void readAdcC1()
	{
		if(call AdcC1.read() != SUCCESS)
			post readAdcC1();
	}

	task void readTemp()
	{
		if(call Temp.read() != SUCCESS)
			post readTemp();
	}

	task void readHumid()
	{
		if(call Humid.read() != SUCCESS)
			post readHumid();
	}

	task void readLight()
	{
		if(call Light.read() != SUCCESS)
			post readLight();
	}

	task void readIR()
	{
		if(call IR.read() != SUCCESS)
			post readIR();
	}

	void ComposeStatusMessage(parking_garage_status_msg_t *msg, uint16_t sensor)
	{
 		msg->parking_space_id = parkingSpaceID;
		msg->packet_id = statusPacketID;
		msg->sensor = sensor;
        msg->sensor_value = sensor_value[sensor];
        if(sensor !=0)
        {
        }
	}

	void ComposeStatusDebugMessage(parking_garage_status_debug_msg_t *msg)
	{
		msg->parking_space_id = parkingSpaceID;
		msg->packet_id = statusDebugPacketID;
		msg->light_sensor = sensor_value[LIGHT];
		msg->passive_ir_sensor = sensor_value[IR_LIGHT];
		msg->temp_sensor = sensor_value[TEMPERATURE];
		msg->humid_sensor = sensor_value[HUMIDITY];
		msg->active_ir_sensor = sensor_value[ADC1];
		msg->minutes_occupied = actual_active_ir_sensor;
	}

	int ReadAllSensors()
	{
		int i = 0;
		int done = 1;

		if(read_count[ADC1] < numberOfReads)
		{
			post readAdcC1();
			done -= 1;
		}
		if(read_count[LIGHT] < numberOfReads)
		{
			post readLight();
			done -= 1;
		}
		if(read_count[IR_LIGHT] < numberOfReads)
		{
			post readIR();
			done -= 1;
		}
		if(read_count[TEMPERATURE] < numberOfReads)
		{
			post readTemp();
			done -= 1;
		}
		if(read_count[HUMIDITY] < numberOfReads)
		{
			post readHumid();
			done -= 1;
		}	
		
		if(done == 1)
		{
			call SensorTimer.stop();
			
			if(sensor_config == 0)
			{
				sensor_max = temp_sensor_value[ADC1]/numberOfReads;
				sensor_value[ADC1] = temp_sensor_value[ADC1]/numberOfReads;
				actual_active_ir_sensor = carPresentThreshold;
				for(i=0; i < NUMBER_OF_SENSORS; i += 1)
				{
					temp_sensor_value[i] = 0;
					read_count[i] = 0;
				}
			}
			else if(sensor_config == 1)
			{
				sensor_min = temp_sensor_value[ADC1]/numberOfReads;
				sensor_value[ADC1] = temp_sensor_value[ADC1]/numberOfReads;
				carPresentThreshold = ((sensor_max - sensor_min)*.8)+sensor_min;
				actual_active_ir_sensor = carPresentThreshold;
				for(i=0; i < NUMBER_OF_SENSORS; i += 1)
				{
					temp_sensor_value[i] = 0;
					read_count[i] = 0;
				}
			}
			else
			{
				for(i=0; i < NUMBER_OF_SENSORS; i += 1)
				{
					if(i != ADC1)
					{
						sensor_value[i] = temp_sensor_value[i]/numberOfReads;
					}
					else
					{
						actual_active_ir_sensor = temp_sensor_value[i]/numberOfReads;
					
						if((temp_sensor_value[i]/numberOfReads) < carPresentThreshold)
						{
							sensor_value[i] = 1;
							call Leds.led2On();
						}
						else
						{
							sensor_value[i] = 0;
							call Leds.led2Off();
						}
					}
					temp_sensor_value[i] = 0;
					read_count[i] = 0;
				}
			}
			
			post sendStatusDebugMessage();
			
			return 1;
		}
		else
		{
			return 0;
		}

	}

	event void Boot.booted()
	{
		call RadioControl.start();
		call ButtonNotify.enable();
	}

	event void RadioControl.startDone(error_t err)
	{
		if (err == SUCCESS)
		{
		}
	}
	
	event void RadioControl.stopDone(error_t err) {}

	event void ButtonNotify.notify( button_state_t state )
	{
		if( state == BUTTON_PRESSED )
		{
			if(sensor_config == 0)
			{
				call Leds.led1On();
				parkingSpaceID = 65001;
				call SensorTimer.startPeriodic(1024);
			}
			else if(sensor_config == 1)
			{
				call Leds.led1On();
				parkingSpaceID = 65002;
				call SensorTimer.startPeriodic(1024);
			}
			else if(sensor_config == 2)
			{	
				parkingSpaceID = 0;			
				post sendStatusDebugMessage();
				call StatusTimer.startPeriodic(1024);
			}
			else
			{}
		}
		else if( state == BUTTON_RELEASED )
		{
			/*
				TODO 	
			*/
		}
	}

	event void StatusTimer.fired()
	{
		if(parkingSpaceID != 0)
		{
			call StatusTimer.startPeriodic(1024*15);
			call SensorTimer.startPeriodic(256);
		}
	}
	event void SensorTimer.fired()
	{
		ReadAllSensors();
	}
	event void LEDTimer.fired()
	{
		/*
			TODO 	
		*/
	}
	event void TimeoutTimer.fired()
	{
		/*
			TODO 	
		*/
	}
	
	event void StatusSend.sendDone(message_t* bufPtr, error_t error)
	{
		statusPacketID++;
	}

	event void StatusDebugSend.sendDone(message_t* bufPtr, error_t error)
	{
		statusDebugPacketID++;
		
		if(sensor_config == 1)
		{
			call Leds.led1Off();
			sensor_config = 2;
		}
		else if(sensor_config == 0)
		{
			call Leds.led1Off();
			sensor_config = 1;
		}
	}
	
	event void AdcC1.readDone(error_t result, uint16_t data) 
	{
		if (result == SUCCESS)
		{
			read_count[ADC1] += 1;
			temp_sensor_value[ADC1] += data;	
		}
	}

	event void Temp.readDone(error_t result, uint16_t data) 
	{
		if (result == SUCCESS)
		{
			read_count[TEMPERATURE] += 1;
			temp_sensor_value[TEMPERATURE] += (9/5)*(-38.4 + 0.0098 * data)+32;	
		}
	}

	event void Humid.readDone(error_t result, uint16_t data) 
	{
		if (result == SUCCESS)
		{
			read_count[HUMIDITY] += 1;
			temp_sensor_value[HUMIDITY] += -0.0000028*data*data + 0.0405*data-4;		
		}
	}

	event void Light.readDone(error_t result, uint16_t data) 
	{
		if (result == SUCCESS)
		{
			read_count[LIGHT] += 1;
			temp_sensor_value[LIGHT] += data;	
		}
	}

	event void IR.readDone(error_t result, uint16_t data) 
	{
		if (result == SUCCESS)
		{
			read_count[IR_LIGHT] += 1;
			temp_sensor_value[IR_LIGHT] += data;	
		}
	}

	event message_t* ConfigReceive.receive(message_t* bufPtr, void* payload, uint8_t len)
	{
		if (len != sizeof(parking_garage_config_msg_t)) 
		{			parking_garage_config_msg_t* pgc = (parking_garage_config_msg_t*)payload;

            parkingSpaceID = pgc->new_parking_space_id;

            call Leds.led0Toggle();
			return bufPtr;
		}
		else
		{
			parking_garage_config_msg_t* pgc = (parking_garage_config_msg_t*)payload;

			if(parkingSpaceID == 0)
			{
				parkingSpaceID = pgc->new_parking_space_id;
			}

            call Leds.led0Toggle();
		}
		return bufPtr;
	}
	
	event message_t* CommandReceive.receive(message_t* bufPtr, void* payload, uint8_t len)
	{
		if (len != sizeof(parking_garage_command_msg_t)) 
		{
			return bufPtr;
		}
		else
		{
            call Leds.led0Toggle();
		}
		return bufPtr;
	}
}
