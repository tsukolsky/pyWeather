import sqlite3, time

DB_DEBUG = True

def DEBUG(message):
    if DB_DEBUG:
        print message

class DbProvider():
    DB_FILE = 'weatherReadings.db'
    SELECT_ALL_STMT = 'SELECT * from READINGS'
    INSERT_STMT = 'INSERT into READINGS values (?, ?, ?, ?, ?,?)'
    def __init__(self):
        DEBUG("DbProvider")
        self.__initialized = True
        self.__nextId = -1
        try:
            # Connect to the database
            self.conn = sqlite3.connect(DbProvider.DB_FILE)
            self.cursor = self.conn.cursor()

            # Update the ID
            self.GetNextId()
        except:
            self.__initialized = False

        DEBUG("DbProvider is %s"%("initialized" if self.__initialized else "not initialized"))

    def IsInitialized():
        return self.__initialized

    def SaveReading(self, time, humidity, adTemp, tiTemp, thermTemp):
        data = (self.GetNextId(), time, humidity, adTemp, tiTemp, thermTemp)
        self.cursor.execute(DbProvider.INSERT_STMT, data)
        self.conn.commit()

    def GetNextId(self):
        # Get the next ID in the table
        self.cursor.execute(DbProvider.SELECT_ALL_STMT)
        readings = self.cursor.fetchall()
        self.conn.commit()
        self.__nextId = len(readings)
        DEBUG("NextID is %d"%len(readings))
        return self.__nextId

if __name__ == "__main__":
    dbProvider = DbProvider()
    dbProvider.SaveReading("2014-12-3 10:10:10",23.3, 33.3, 44.4, 55.5)
