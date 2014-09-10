import serial
import os, sys, time

DB_DEBUG = True

def DEBUG(message):
    if DB_DEBUG:
        print "Communicator: %s"%message

class Communicator():
    PORT='/dev/ttyUSB0'
    BAUD=9600
    GPIO_PATH='/sys/class/gpio/gpio2/value'
    RECEIVE_TIMEOUT=2                          # in seconds
    ACK_TIMEOUT=6
    STATS="STATS."

    FIELD_AD = 'AnalogDevices'
    FIELD_TI = 'TexasInstruments'
    FIELD_THERM = 'Thermistor'
    FIELD_HUM = 'Humidity'

    def __init__(self):
        self.__initialized = True
        self.__serialPort = None
        try:
            self.__serialPort = serial.Serial(
                port=Communicator.PORT,
                baudrate=Communicator.BAUD,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
        except:
            self.__initialized = False
            DEBUG("Unable to initialize serial port")

        # Initialize the pin
        os.system('/usr/sbin/pinSetup')

    def IsInitialized(self):
        return self.__initialized

    def GetCurrentStats(self):
        retDict = dict()

        # Alert the device and wait for acknowledgement
        self.__triggerInterrupt()
        ackReceived = False
        ackTimeout=time.time()+Communicator.ACK_TIMEOUT
        while ((time.time()-ackTimeout)<0) and not ackReceived:
            ackString=self.ReceiveString(True)
            if ackString.find('error')==-1:			#Error wasn't returned, so we have a valid ack string. continue
                ackReceived=True
            else:
                time.sleep(100.0/1000.0)

        # If ACK received, query for current stats
        if ackReceived:
            DEBUG("GetCurrentStats: ACK RECEIVED!")
            self.SendString(Communicator.STATS)
            time.sleep(75.0/100.0)
            statsString = self.ReceiveString(False)

            if statsString != 'error':
                retDict = self.__parseString(statsString)
        else:
            DEBUG("GetCurrentStats: NO ACK RECEIVED!")

        return retDict

    def __parseString(self, stringToParse):
        retDict = dict()
        fields=stringToParse.split('/')
        for field in fields:
            DEBUG("Parse String: looking at field: %s"%field)
            if field.find('AD')!=-1:
                retDict[Communicator.FIELD_AD] = float(field[2:])
                DEBUG("ParseString: %s = %f"%(Communicator.FIELD_AD, retDict[Communicator.FIELD_AD]))
            elif field.find('TI')!=-1:
                retDict[Communicator.FIELD_TI] = float(field[2:])
                DEBUG("ParseString: %s = %f"%(Communicator.FIELD_TI, retDict[Communicator.FIELD_TI]))
            elif field.find('TH')!=-1:
                retDict[Communicator.FIELD_THERM] = float(field[2:])
                DEBUG("ParseString: %s = %f"%(Communicator.FIELD_THERM, retDict[Communicator.FIELD_THERM]))
            elif field.find('HU')!=-1:
                retDict[Communicator.FIELD_HUM] = float(field[2:7])
                DEBUG("ParseString: %s = %f"%(Communicator.FIELD_HUM, retDict[Communicator.FIELD_HUM]))

        return retDict

    def __triggerInterrupt(self):
        # Raise pin high
        os.system("echo 1 > /sys/class/gpio/gpio2/value")
        time.sleep(25.0/1000.0)
        os.system("echo 0 > /sys/class/gpio/gpio2/value")

    def SendString(self,theString):
        #Loop through each character in the string and write it.
        for char in theString:
            self.__serialPort.write(char)
            time.sleep(50.0/1000.0)

    def ReceiveString(self,waitingForAck = False):
        # Wait for an X that signifies the end of data.
        gotTerminator=False
        timeout=time.time()+Communicator.RECEIVE_TIMEOUT
        captureString=''
        returnStr='error'
        while not gotTerminator and ((time.time()-timeout) < 0):
            captureString+=self.__serialPort.read(self.__serialPort.inWaiting())
            if captureString.find('X')!=-1:
                gotTerminator=True
                returnStr = captureString.strip().rstrip().replace('X','')
            elif captureString.find('ACK.')!=-1 and waitingForAck:
                gotTerminator=True
                returnStr = captureString.strip().rstrip()
            else:
                time.sleep(20.0/1000.0)		#Wait for another 20 milliseonces
        DEBUG("Receive String - %s"%returnStr)
        return returnStr

if __name__ == "__main__":
    print "Running communicator test..."
    comm = Communicator()
    if comm.IsInitialized():
        statDict = comm.GetCurrentStats()


