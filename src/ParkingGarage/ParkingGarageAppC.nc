/* 
 * Matt Lindsay
 * CSE521S project
 * ParkingGarage is is part of a parking guidance and information system
 * designed to take advantage of the TelosB and an analog range finder.
 */

#include <Timer.h>
#include <UserButton.h>
#include "ParkingGarage.h"

configuration ParkingGarageAppC
{
	
}
implementation
{
	components MainC;
	components ParkingGarageC as App;
	components LedsC;
	components ActiveMessageC;
	components new AMSenderC(PARKING_GARAGE_STATUS_MSG) as StatusSenderC;
	components new AMSenderC(PARKING_GARAGE_STATUS_DEBUG_MSG) as StatusDebugSenderC;
	components new AMReceiverC(PARKING_GARAGE_CONFIG_MSG) as ConfigReceiverC;
	components new AMReceiverC(PARKING_GARAGE_COMAND_MSG) as CommandReceiverC;
	components new TimerMilliC() as StatusTimerC;
	components new TimerMilliC() as SensorTimerC;
	components new TimerMilliC() as LEDTimerC;
	components new TimerMilliC() as TimeoutTimerC;
	components UserButtonC;
	components new AdcReadClientC() as A1_Client;
	components AdcChannel1C;
	components new SensirionSht11C() as HumidityTempC;
	components new HamamatsuS10871TsrC() as TotalSolarC;
	components new HamamatsuS1087ParC() as PhotoActiveC;

	App.Boot -> MainC.Boot;
  
	App.ConfigReceive -> ConfigReceiverC;
	App.CommandReceive -> CommandReceiverC;

	App.StatusSend -> StatusSenderC;
	App.StatusDebugSend -> StatusDebugSenderC;
	
	App.RadioControl -> ActiveMessageC;
	App.Packet -> ActiveMessageC;
		
	App.Leds -> LedsC;
	
	App.StatusTimer -> StatusTimerC;
	App.SensorTimer -> SensorTimerC;
	App.LEDTimer -> LEDTimerC;
	App.TimeoutTimer -> TimeoutTimerC;
			
	A1_Client.AdcConfigure -> AdcChannel1C;
	AdcChannel1C.Read -> A1_Client;
	App.AdcC1 -> AdcChannel1C.ReadMe;
	
	App.ButtonNotify -> UserButtonC;
	App.Temp -> HumidityTempC.Temperature;
	App.Humid -> HumidityTempC.Humidity;
	App.Light -> 	PhotoActiveC;
	App.IR -> TotalSolarC;
}
