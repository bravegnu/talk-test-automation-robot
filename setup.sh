#!/usr/bin/env sh

ip link set can0 down
ip link set can0 up type can bitrate 500000
ifconfig enxf8e43bea52b5:1 192.168.1.2 up
