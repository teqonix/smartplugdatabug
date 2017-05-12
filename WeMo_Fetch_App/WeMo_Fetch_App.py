import ouimeaux
import sqlite3
import datetime
import pymssql 

from ouimeaux.environment import Environment

#We will use an in-memory database & table to store and aggregate our data we've pulled from our WeMo devices
db = sqlite3.connect(':memory:')

def init_db(cur):
    #This function will create the database to store our WeMo device data; since this is a simple example, it`s just one table:
    cur.execute('''CREATE TABLE switchDataPoints (
                        MACAddress TEXT,
                        IPAddress TEXT,
                        SignalStrength INTEGER,
                        SerialNbr TEXT,
                        ModelNbr TEXT,
                        FirmwareVersion TEXT,
                        DeviceName TEXT,
                        Status INTEGER,
                        EnergyUse INTEGER
                    )'''
    )

def getDeviceHardwareIDs(Environment):
    deviceHardwareData = [] 
    for switchStr in ( Environment.list_switches() ):
        currentSwitch = Environment.get_switch(switchStr)
        switchMAC = currentSwitch.basicevent.GetMacAddr()
        switchUDNlowercase = switchMAC['PluginUDN'].lower()
        switchFirmwareVersion = currentSwitch.firmwareupdate.GetFirmwareVersion()
        switchIPAddress = currentSwitch.host
        switchSerialNumber = currentSwitch.serialnumber
        switchModelNbr = currentSwitch.model
        deviceHardwareData.append([switchMAC, switchUDNlowercase, switchFirmwareVersion, switchIPAddress, switchSerialNumber, switchModelNbr])
    return deviceHardwareData

def aggregateDeviceData(Environment, numSecondsForDiscovery, numMinutesToGatherData, fetchDataDelaySeconds, databaseCursor):
    databaseCursor.execute('DELETE FROM switchDataPoints') #Remove any existing data from this table, as it should`ve already been stored elsewhere
    Environment.discover(numSecondsForDiscovery)
    #print(Environment.list_switches()) #DEBUG: See what devices we grabbed during discovery
    switchPowerDataArray = [] #We will store a list of power measurements in this list and then average them before sending them to a flat file or database (we don`t need 300 measurements per minute stored in the database; it should be flattened out)
    switchPowerDataArray.clear()
    #Fetch the current date/time into a variable, then find the date/time one minute from now; we'll use that 
    currentDateTime = datetime.datetime.now()
    minuteFromNow = currentDateTime - datetime.timedelta(minutes=(-1 * numMinutesToGatherData))
    currentLoopIteration = 0 #We will only gather the switch hardware / firmware details at the first iteration of fetching power data; no need to get it multiple times during execution
    deviceHardwareData = getDeviceHardwareIDs(env)
    while datetime.datetime.now() <= minuteFromNow:
        for switchStr in ( Environment.list_switches() ):
            currentSwitch = Environment.get_switch(switchStr)
            switchMAC = currentSwitch.basicevent.GetMacAddr()
            for index, deviceHardwareIDRow in enumerate(deviceHardwareData):
                if switchMAC == deviceHardwareIDRow[0]:
                    #print("Oh hey we found the matching device for: " + deviceHardwareIDRow[0]['MacAddr'])
                    currentSwitchHardwareIndex = index
            switchSignalStrength = currentSwitch.basicevent.GetSignalStrength()
            switchCurrentState = currentSwitch.basicevent.GetBinaryState()
            #print(switchUDNlowercase)
            #print( "This is the switch we are using: ", switchStr )                
            #currentSwitch.explain()ccc
            #switchHWInfo = currentSwitch.metainfo.GetMetaInfo()
            #switchManufacture= currentSwitch.manufacture.GetManufactureData()
            if deviceHardwareData[currentSwitchHardwareIndex][1].find('insight') > 0:
                #print("Insight switch found!")
                #print( currentSwitch.insight_params.keys() )
                #print( currentSwitch.insight_params.values() )
                currentSwitch.insight.GetInsightParams()
                insightCurrentPower = currentSwitch.insight_params['currentpower']
                switchPowerDataArray.append([deviceHardwareData[currentSwitchHardwareIndex][0]['MacAddr']
                                             , deviceHardwareData[currentSwitchHardwareIndex][3]
                                             , switchSignalStrength['SignalStrength']
                                             , deviceHardwareData[currentSwitchHardwareIndex][0]['SerialNo']
                                             , deviceHardwareData[currentSwitchHardwareIndex][5]
                                             , deviceHardwareData[currentSwitchHardwareIndex][2]['FirmwareVersion']
                                             , switchStr
                                             , switchCurrentState['BinaryState']
                                             , insightCurrentPower]
                                            )                    
            exportDataString = ([deviceHardwareData[currentSwitchHardwareIndex][0]['MacAddr'], deviceHardwareData[currentSwitchHardwareIndex][3], switchSignalStrength['SignalStrength'], deviceHardwareData[currentSwitchHardwareIndex][0]['SerialNo'], deviceHardwareData[currentSwitchHardwareIndex][5], deviceHardwareData[currentSwitchHardwareIndex][2]['FirmwareVersion'], switchStr, switchCurrentState['BinaryState'], insightCurrentPower] )
            #print( exportDataString )
        currentLoopIteration = currentLoopIteration + 1
        Environment.wait(fetchDataDelaySeconds)
        #print("Current loop count: " + str(currentLoopIteration))
    currentPowerSum = 0
    for powerDataPoint in switchPowerDataArray:
        currentPowerSum = currentPowerSum + powerDataPoint[8]
        databaseCursor.execute('INSERT INTO switchDataPoints(MACAddress, IPAddress, SignalStrength, SerialNbr, ModelNbr, FirmwareVersion, DeviceName, Status, EnergyUse) VALUES (?,?,?,?,?,?,?,?,?)',powerDataPoint) #This method must iterate through the list and replace the variables (?'s) in the INSERT statement from left to right
        db.commit()
        #print(powerDataPoint)
    #Average out the data points collected throughout looping through the above logic and group it by device.  This will go into the permanent database.
    tableQuery = """SELECT 
	                    MACAddress
	                    , MAX(IPAddress) AS IPAddress
	                    , MIN(SignalStrength) AS SignalStrength
	                    , SerialNbr
	                    , MAX(ModelNbr) AS ModelNbr
	                    , MAX(FirmwareVersion) AS FirmwareVersion
	                    , DeviceName AS DeviceName
	                    , MAX(Status) AS Status
	                    , AVG(EnergyUse) AS EnergyUse
                        , COUNT(0) AS dataPointsAggregated
	                    , datetime(datetime(), 'localtime') AS DataPulledDate
                FROM switchDataPoints
                GROUP BY DeviceName, MACAddress, SerialNbr"""
    returnData = []
    for dataRow in databaseCursor.execute(tableQuery):
        #print(dataRow)
        returnData.append(dataRow)
    
    tableQuery = """
                     SELECT                         
                        MACAddress,
                        IPAddress,
                        SignalStrength,
                        SerialNbr,
                        ModelNbr,
                        FirmwareVersion,
                        DeviceName,
                        Status,
                        EnergyUse
                     FROM switchDataPoints
                 """
    #Debug query and output to see detail data in the database table:
    #for detailData in databaseCursor.execute(tableQuery):
    #    print(detailData)
    return returnData



if __name__ == "__main__":
    print("")
    print("Unit Test of Ouimeaux")
    print("---------------")
    env = Environment()
    # TODO: run from 10am to 10pm

#Initialize the database in memory:
try:
    cur = db.cursor()
    init_db(cur)
    env.start()
    nbrLoopsBeforeRediscovery = 10
    numMinutesToGatherData = 0.10
    fetchDataDelaySeconds = 2
    server="10.0.60.25"
    username="ouimeaux"
    password=""
    mssqldatabase="Sandbox"

    #Connect to the MS SQL Server instance the database application is stored:
    mssqldb = pymssql.connect(server, username, password, "tempdb")
    mssqlcursor = mssqldb.cursor()



    currentDataSet = aggregateDeviceData(Environment=env,numSecondsForDiscovery=5,numMinutesToGatherData=1,fetchDataDelaySeconds=3,databaseCursor=cur)
    print(currentDataSet)

    

    input("Press Enter to continue...")

except (KeyboardInterrupt, SystemExit):
    print("---------------")
    print("Goodbye!")
    print("---------------")
    # Turn off all switches
    #for switch in ( env.list_switches() ):
    #    print("Turning Off: " + switch)
    #    env.get_switch( switch ).off()
