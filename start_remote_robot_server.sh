#!/bin/bash
# scripts/start_remote_robot_server.sh
ssh er@qaserver-robot.local "cd ~/server && nohup python3 ~/server/robot_arm_server.py --serial /dev/ttyTHS1 > server.log 2>&1 &"
