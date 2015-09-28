import serial

ser=serial.Serial('/dev/ttyUSB4',115200)

def mspRequest(code):
	ser.write(chr(36))
	ser.write(chr(77))
	ser.write(chr(60))
	ser.write(chr(0))
	ser.write(chr(code))
	ser.write(chr(0^code))
	while(not ser.inWaiting()):
		pass
	str=ser.read(ser.inWaiting())
	if(str[0]=='$' and str[1]=='M' and str[2]=='>'):
		size=ord(str[3])
		mpsCmd=ord(str[4])
		body=str[5:-1]
		checkSum=size^mpsCmd
		for c in body:
			checkSum^=ord(c)
		if(ord(str[-1])==checkSum and len(body)==size):
			return body
		else:
			return 0
	else:
		return 0

def mspSend(code,data):
	ser.write(chr(36))
	ser.write(chr(77))
	ser.write(chr(60))
	ser.write(chr(len(data)))
	ser.write(chr(code))

	checkSum=len(data)^code
	for c in data:
		ser.write(chr(c))
		checkSum^=c

	ser.write(chr(checkSum))

def serial16_int16(low,high):
	if(ord(high)>=128):
		return -((ord(high)^255)*256+(ord(low)-1)^255)
	else:
		return ord(high)*256+ord(low)

#from low to high
def serial32_int32(b1,b2,b3,b4):
	if(ord(b4)>=128):
		return -((ord(b4)^255)*256**3+(ord(b3)^255)*256**2+(ord(b2)^255)*256+(ord(b1)-1)^255)
	else:
		return ord(b4)*256**3+ord(b3)*256**2+ord(b2)*256+ord(b1)		


def getRawImu():
	RawImu=[]
	str=mspRequest(102)
	if(str):
		try:
			for i in range(9):
				if(i<3):
					# m/s/s
					RawImu.append(serial16_int16(str[i*2],str[i*2+1])/512.0*9.80665)
				else:
					if(i<6):
						# deg/s
						RawImu.append(serial16_int16(str[i*2],str[i*2+1])*(1/16.4))
					else:
						RawImu.append(serial16_int16(str[i*2],str[i*2+1])/1090.0)
		except:
			return "Request Failed"
	return RawImu

def getAttitude():
	Attitude=[0,0,0]
	str=mspRequest(108)
	if(str):
		try:
			Attitude[0]=serial16_int16(str[0],str[1])/10.0
			Attitude[1]=serial16_int16(str[2],str[3])/10.0
			Attitude[2]=serial16_int16(str[4],str[5])
		except:
			return "Request Failed"
	return Attitude

def getAltitude():
	# Imu+Baro, Baro, vel   cm
	Altitude=[0,0,0]
	str=mspRequest(109)
	if(str):
		try:
			Altitude[0]=serial32_int32(str[0],str[1],str[2],str[3])
			Altitude[1]=serial16_int16(str[4],str[5])
			# Altitude[1]=serial32_int32(str[4],str[5],str[6],str[7])
			# Altitude[2]=serial16_int16(str[8],str[9])
		except:
			return "Request Failed"
	return Altitude

def reBoot():
	mspSend(68,[])

def imuCalibration():
	mspSend(205,[])

def getMotor():
	Motor=[]
	str=mspRequest(104)
	if(str):
		try:
			for i in range(8):
				Motor.append(serial16_int16(str[2*i],str[2*i+1]))
		except:
			return "Request Failed"
	return Motor

def setMotor(Motor):
	data=[]
	for i in range(len(Motor)):
		low=Motor[i]%256
		high=Motor[i]/256
		data.append(low)
		data.append(high)
	mspSend(214,data)

def stopMotor():
	Motor=[1000,1000,1000,1000]
	data=[]
	for i in range(len(Motor)):
		low=Motor[i]%256
		high=Motor[i]/256
		data.append(low)
		data.append(high)
	mspSend(214,data)



