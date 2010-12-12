# README #

This project is for the CSE 521S: Wireless Sensor Networks class.  It is
designed to implement a parking guidance and information system with TinyOS.
The goal is to enable distinct hardware sensors to interact with a Tmote
Sky/TelosB node, the node is then connected to a mesh network that sends
updates to a base station, and the base station interacts with a display
service to present the information to end users.

The basic directory structure is as follows:

* README.md - this file!
* doc - all documents/presentations generated for this project
  * proposal - original project proposal document source
  * demo_i - first demo presentation slides
  * demo_ii - second demo presentation slides
  * demo_iii - final presentation slides (PowerPoint and PDF)
  * paper - find project report document source
* src - source code for this project
  * ParkingGarage - source for Parking Garage motes with sonar sensors
  * Gateway - bridge between the sensor network and the AppEngine instance
  * aggregator - backend and frontend code for the AppEngine instance
  * BaseStation - virturally identical to BaseStation source from TinyOS

Source directories each have their own README file with further information
about the component.

A video demonstration is noted in the final report.
