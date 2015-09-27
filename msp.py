import serial

def openSerial():
	ser=serial.Serial('/dev/ttyUSB1',115200)
	return ser

def mspRequest(ser,c):
	ser.write(chr(36))
	ser.write(chr(77))
	ser.write(chr(60))
	ser.write(chr(0))
	ser.write(chr(c))
	ser.write(chr(0^c))
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

def serial16_int16(low,high):
	if(ord(high)>=128):
		return -((ord(high)^255)*256+(ord(low)-1)^255)
	else:
		return ord(high)*256+ord(low)

def requestRawImu(ser):
	RawImu=[]
	str=mspRequest(ser,102)
	if(str):
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
	return RawImu


