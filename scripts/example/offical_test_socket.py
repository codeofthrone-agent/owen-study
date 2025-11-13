from pymycobot import MyCobot280Socket
# Default port is 9000
#"172.20.10.14" is the IP of the robot arm, please enter your own IP of the robot arm
mc = MyCobot280Socket("10.42.0.180",9000)

#If the connection is normal, you can control the robot arm
mc.send_angles([45,0,0,0,0,0],20)
res = mc.get_angles()
print(res)
