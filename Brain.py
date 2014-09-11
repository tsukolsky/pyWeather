from Communicator import Communicator
from DatabaseProvider import DatabaseProvider
from Server import PyWeatherServer
import threading, time

DB_PRINT = True
def DEBUG(message):
    if DB_PRINT:
        print "Brain: %s"%message


class Brain(threading.Thread):
    FILE_HTML = 'index.html'
    BANNER_TI = 'TI Temp:'
    BANNER_HUM = 'Humidity:'
    BANNER_AD = 'AD Temp:'
    BANNER_THERM = 'Ambient Temp:'
    END_TABLE = '</tr>'

    def __init__(self):
        super(Brain,self).__init__()
        self.__dbProvider = DatabaseProvider()
        self.__communicator = Communicator()
        self.__pyServer = PyWeatherServer()
        self.stopRequest = threading.Event()

    def run(self):
        # Every 30 seconds, wake up and take a reading
        #self.__pyServer.run()
        startTime = time.time()
        DEBUG("In run: start time is %d"%startTime)
        while not self.stopRequest.isSet():
            curTime = time.time()
            DEBUG("curTime = %d, startTime = %d, mod 10 = %d"%(curTime, startTime, (curTime - startTime)%10))
            modResult = int((curTime - startTime)%10)
            DEBUG("modResult = %d, modResult == 0 ? %s"%(modResult, "true" if (int(modResult) == 0) else "false"))
            if (modResult == 0):
                # Take a reading and save it
                DEBUG("Taking a reading...")
                # TODO: Replace with an event "Reading Ready" for dbprovider to write.
                #       Communicator owns event, Brain subscribes dbProvider to it.
                readingDict = self.__communicator.GetCurrentStats()
                self.__dbProvider.SaveReading(readingDict[Communicator.FIELD_HUM], \
                                              readingDict[Communicator.FIELD_AD],  \
                                              readingDict[Communicator.FIELD_TI],  \
                                              readingDict[Communicator.FIELD_THERM])
            else:
                DEBUG("sleeping for 1 second...")
                time.sleep(1)
    def join(self, timeout=None):
        DEBUG("JOIN CALLED")
        self.stopRequest.set()
        time.sleep(100.0/1000.0)
        super(Brain,self).join(timeout)

if __name__ == "__main__":
    DEBUG("making a brain")
    br = Brain()
    br.run()
    while True:
        time.sleep(1)
