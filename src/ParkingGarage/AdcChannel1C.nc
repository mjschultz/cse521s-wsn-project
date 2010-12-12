#include "Msp430Adc12.h"

module AdcChannel1C {
  provides {
    interface AdcConfigure<const msp430adc12_channel_config_t*>;
    interface Read<uint16_t> as ReadMe;
  }
  uses {
    interface Read<uint16_t>;
  }
}
implementation {

  const msp430adc12_channel_config_t config = {
      inch: INPUT_CHANNEL_A0,
      sref: REFERENCE_AVcc_AVss,
      ref2_5v: REFVOLT_LEVEL_NONE,
      adc12ssel: SHT_SOURCE_ACLK,
      adc12div: SHT_CLOCK_DIV_1,
      sht: SAMPLE_HOLD_4_CYCLES,
      sampcon_ssel: SAMPCON_SOURCE_SMCLK,
      sampcon_id: SAMPCON_CLOCK_DIV_1
  };

  event void Read.readDone( error_t result, uint16_t val )
  {
    signal ReadMe.readDone(result, val);
  }

  command error_t ReadMe.read() {
    return call Read.read();
  }

  async command const msp430adc12_channel_config_t* AdcConfigure.getConfiguration()
  {
    return &config; // must not be changed
  }
}
