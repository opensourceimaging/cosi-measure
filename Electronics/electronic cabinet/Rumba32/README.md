# Rumba32

The [Rumba32](https://github.com/Aus3D/RUMBA32) is a 3D-printer mainboard with a microcontroller which is controlling the stepper motors, endstops etc. 
- It is not compatibel with industrial 12 V or 24 V limit switches so a levelshifter is needed, see [here](Endstop_Levelshifter/README.md). 
- It is not designed for external motor drivers with extended safe-torque-off (emergency stop) functionality, so breakoutboards instead of the motor drivers are needed, see [here](Driver_BreakoutBoard/README.md)
- The external motor drivers need 5 V signals, thus a little work on the Rumba32 PCB is needed, see [here](Driver_BreakoutBoard/README.md#stepper_driver_logic-jumper)
- [Klipper](https://github.com/Klipper3d/klipper) requires a temperatur signal from the nozzle and the heated bed. COSI Measure usually does not have this, so please plug two 100 k resistors to the PT100 inputs.
