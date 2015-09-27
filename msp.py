import serial

def openSerial():
	ser=serial.Serial('/dev/ttyUSB0',115200)
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



