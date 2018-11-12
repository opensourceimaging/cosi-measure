# J5-BOB, a BeBoPr++ stepper driver breakout board

*2015-03-04 SJL - content with real PCBs, initial version*
## Introduction

**J5** is the name of the expansion connector on all the BeBoPr, BeBoPr+ and BeBoPr++ boards. It is used to expand the number of axes (or digital outputs) controlled by a BeBoPr, or when using external stepper drivers. Example expansion boards that connect to J5 are the [**PEPPER**](https://github.com/modmaker/BeBoPr-plus-plus/wiki/PEPPER-Intro), [**TAKE-5**](https://github.com/modmaker/TAKE-5), [**XTRUDR**](https://github.com/modmaker/XTRUDR) and [**DECAMUX**](https://github.com/modmaker/DECAMUX).

Now there is also the **J5-BOB**, a simple breakout board for easy access of the J5 signals and the necessary buffer for the enable signal.

The J5-BOB makes it easy to connect external stepper drivers to the BeBoPr. No breadboard or complex siring needed. Instead of having to split a ribbon cable, identify each wire, and finding a way to connect it to the stepper drivers, the J5-BOB provides industrial wiring connectors with the stepper signals logically grouped for straight forward routing to the stepper drivers.

The image below shows as example a **LeadShine DM422C driver** and **Nema-23 stepper motor** connected as **X-axis** to a **BeBoPr++**.

![](http://imageshack.com/a/img661/9599/fEKKi3.jpg)

## External driver input signal type

Most drivers use either **plain TTL/CMOS** level inputs, or **opto couplers** for the stepper input signals. Depending on how the inputs of the opto couplers are interconnected, the BeBoPr should either source or sink the LED current. The J5-BOB can be configured (by the **SRCE/SINK jumper**) to handle either one of these configurations.

## Assembly

All components on the J5-BOB are though hole parts *(not SMD)* for easy (DIY) assembly.

One or two transistors and up to three resistors form the buffer and optional inverter for the enable signal. The most common configuration *(common anode, sinking drivers with inactive/inverted enable inputs)* requires only a single resistor and one transistor on the board (see image below). See below or the [schematics](https://github.com/modmaker/J5-BOB/tree/master/doc) for the assembly options.

![](http://imageshack.com/a/img673/4877/45wZPE.jpg)

## Attachment to the BeBoPr

Like most BeBoPr expansion boards, the J5-BOB can be assembled to attach via a ribbon cable, or to mount directly on the BeBoPr. The latter seems the most likely mounting option as it increases the width (size) of the BeBoPr by no more than 5 mm.

![](http://imageshack.com/a/img538/7312/XLVr7Y.jpg)
*This image shows the J5-BOB mounted directly on a BeBoPr++.*

**J5** Used to be a simple 16 pin dual row pin header on older boards. This required some extra attention when attaching a cable. Reversal or misalignment was possible. The version of the BeBoPr++ that currently ships has a polarized boxed header that prevents these mistakes from being made.

![](http://imagizer.imageshack.us/v2/640x480q90/901/CvXVNr.png)

*J5-BOB with socket connector (on the bottom side) for direct attachment to J5 on the BeBoPr.*

![](http://imagizer.imageshack.us/v2/640x480q90/538/YOj9js.png)
*J5-BOB with boxed header connector for attachment via ribbon cable.*

## Driver Enables

Most external drivers have separate enable inputs, so the J5-BOB buffers the BeBoPr's output to be able to drive all these inputs in parallel.

Some external driver modules have inverted the function of the enable input. If left open, or with an inactive signal, the driver is enabled in stead of disabled. This requires an extra inversion in the enable signal from the BeBoPr. This is also an assembly option for the J5-BOB.

When properly configured, all external drivers will be disabled when the ESTOP on the BeBoPr++ is activated.

## Assembly options

How to choose between source and sink? If all inputs have both LED connections available on the connector, either option can be used. However, most of the time either all anodes or all cathodes are connected to a common signal to reduce the number of connections needed.

If the **input LEDs** have the **common** on the **anode** (positive) side, the **sink** configuration is needed. The *common* signal on the J5-BOB is connected to the +5 Volt supply and **the BeBoPr's driver sinks the LED current**.

If the **input LEDs** have the **common** on the **cathode** (negative) side, the **source** configuration is needed. The common signal is 0 Volt and **the BeBoPr's driver sources the LED current**.

| source | sink | enable | disable | mounted components |
|:--:|:--:|:--:|:--:|:--|
|   | X |   | X | R1, Q3 |
|   | X | X |   | R2, R3, R4, Q1, Q3 |
| X |   |   | X | R2, R3, R4, Q1, Q2 |
| X |   | X |   | R1, Q2 |

Note that the sink configuration requires jumper JP4 on the BeBoPr++ to be closed, otherwise there is no +5 Volt supply present on J5.

## The Bill Of Materials

Depending on the assembly options and the mounting method, not all parts are needed.

| item | count | part | description |
|:----:|:-----:|:----------|:-----------------|
| 1 | 1 | PCB | J5-BOB-R0 printed circuit board |
| 2 | 5 | J2, J3, J4, J5, J6 | Phoenix Contact PTSA 1.5/4-3,5-Z |
| 3 | 1 | J1  | combine two SIL-8 sockets (those used for Pololu modules) |
| 4 | 2 | Q1, Q3 | BC547B or other general purpose NPN transistor |
| 5 | 1 | Q2 | BC557B or other general purpose PNP transistor |
| 6 | 4 | R1, R2, R3, R4 | 3k3 1/4W axial leaded resistor, e.g. MRS25 |
| 7 | 2 | - | HEX standoff M/F 11mm M3 (e.g. Harwin R30-3001102)| 
| 8 | 2 | - | Nylon isolating washer M3 | 

*Note 1: not all components are necessary for all configurations*
*Note 2: J1 can either be a header on the top side, or a socket on the bottom side of the board!*

## Where to buy

The design is intended to be open source and free for anyone to build, modify and/or sell. The [PCB](https://oshpark.com/shared_projects/GzRHdh6A) can be ordered directly from [OSH Park](https://oshpark.com/shared_projects/GzRHdh6A) (3 for $19.35 incl. world shipping). The Gerbers can also be downloaded from that place (Use the download button).

If demand justifies the effort, I'll order a couple of PCBs and assemble some kits. Send me an email if you're interested.

|![](http://www.oshwa.org/wp-content/uploads/2014/03/oshw-logo-100-px.png)|![](http://imageshack.com/a/img913/8575/OcYMJB.png)|
|:-:|:-:|
||*PCB Top view*|
