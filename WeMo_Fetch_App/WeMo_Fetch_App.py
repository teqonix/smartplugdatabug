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

def aggregateDeviceData(numSecondsForDiscovery, numMinutesToGatherData, fetchDataDelaySeconds, databaseCursor):
    env = Environment()
    env.start()    
    databaseCursor.execute('DELETE FROM switchDataPoints') #Remove any existing data from this table, as it should`ve already been stored elsewhere
    env.discover(numSecondsForDiscovery)
    #print(Environment.list_switches()) #DEBUG: See what devices we grabbed during discovery
    switchPowerDataArray = [] #We will store a list of power measurements in this list and then average them before sending them to a flat file or database (we don`t need 300 measurements per minute stored in the database; it should be flattened out)
    switchPowerDataArray.clear()
    #Fetch the current date/time into a variable, then find the date/time one minute from now; we'll use that 
    currentDateTime = datetime.datetime.now()
    minuteFromNow = currentDateTime - datetime.timedelta(minutes=(-1 * numMinutesToGatherData))
    currentLoopIteration = 0 #We will only gather the switch hardware / firmware details at the first iteration of fetching power data; no need to get it multiple times during execution
    deviceHardwareData = getDeviceHardwareIDs(env)
    while datetime.datetime.now() <= minuteFromNow:
        for switchStr in ( env.list_switches() ):
            currentSwitch = env.get_switch(switchStr)
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
            print( exportDataString )
        currentLoopIteration = currentLoopIteration + 1
        env.wait(fetchDataDelaySeconds)
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
	                    , MIN(DeviceName) AS DeviceName
	                    , MAX(Status) AS Status
	                    , AVG(EnergyUse) AS EnergyUse
                        , COUNT(0) AS dataPointsAggregated
	                    , datetime(datetime(), 'localtime') AS DataPulledDate
                FROM switchDataPoints
                GROUP BY MACAddress, SerialNbr"""
    returnData = []
    for dataRow in databaseCursor.execute(tableQuery):
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

    #I had to manually kill the UPnP server and remove the ouimeaux environment in order to fetch the device name in case it changed since the last call to this function
    env.upnp.server.stop()
    env.registry.server.stop()
    del env
    return returnData

def InsertOrUpdateDatabase(mssqldb, mssqlcursor,currentDataSet):
    for currentDataRow in currentDataSet:
        print("Beginning work in MS SQL Server")
        #I hate that I've hard-coded the order of data in this function; ideally you'd pass a dictionary into this, but I'm not sure how to do that and am too tired to research how this works: http://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
        #print(currentDataRow[5])
        #First, we need to fill the lookup tables before we can start filling the tables with FK's to the lookups:
        mssqlcursor.execute("""
                    MERGE INTO Sandbox.dbo.deviceFirmware AS target
                    USING (SELECT 
			                    %s AS firmwareName
	                    ) AS source (firmwareName)
                    ON (target.firmwareName = source.firmwareName)
                    WHEN MATCHED THEN 
	                    UPDATE SET target.firmwareName = source.firmwareName
                    WHEN NOT MATCHED THEN 
	                    INSERT (firmwareName)
                        VALUES(source.firmwareName)
                    OUTPUT inserted.[deviceFirmwareSK] --This will return the new or fetched SK back to the calling client (Yay!!)
                    ;                    
        """,currentDataRow[5]) #http://stackoverflow.com/questions/3410455/how-do-i-use-sql-parameters-with-python
        currentFirmwareSK = mssqlcursor.fetchone()
        mssqlcursor.execute("""
                    MERGE INTO Sandbox.dbo.networkMetadata AS target
                    USING (SELECT 
			                    %s AS ipAddress
                                ,%s AS tcpIPversion
	                    ) AS source (ipAddress, tcpIPversion)
                    ON (target.ipAddress = source.ipAddress)
                    WHEN MATCHED THEN 
	                    UPDATE SET target.ipAddress = source.ipAddress, target.tcpIPversion = source.tcpIPversion
                    WHEN NOT MATCHED THEN 
	                    INSERT (ipAddress, tcpIPversion)
                        VALUES(source.ipAddress, source.tcpIPversion)
                    OUTPUT inserted.[networkMetadataSK]
                    ;                    
        """,(currentDataRow[1],'IPv4'))
        currentNetworkMetadataSK = mssqlcursor.fetchone()
        mssqlcursor.execute("""
                    MERGE INTO Sandbox.dbo.deviceTypes AS target
                    USING (SELECT 
			                    %s AS deviceTypeLabel
	                    ) AS source (deviceTypeLabel)
                    ON (target.deviceTypeLabel = source.deviceTypeLabel)
                    WHEN MATCHED THEN 
	                    UPDATE SET target.deviceTypeLabel= source.deviceTypeLabel
                    WHEN NOT MATCHED THEN 
	                    INSERT (deviceTypeLabel)
                        VALUES(source.deviceTypeLabel)
                    OUTPUT inserted.[deviceTypeSK]
                    ;                    
        """,(currentDataRow[4]))
        currentDeviceTypeSK = mssqlcursor.fetchone()
        #Now that we have the SK's for our lookups, upsert into the IoTDevice table:
        mssqlcursor.execute("""
                    MERGE INTO Sandbox.dbo.IoTDevice AS target
                    USING (SELECT 
			                    %s AS macAddress
                                ,%s AS serialNumber
                                ,%s AS friendlyName
                                ,%s AS deviceTypeFK
                                ,%s AS deviceFirmwareFK
                                ,%s AS deviceIPAddressFK
                                ,0 AS retiredDevice --If this merge statment is being called from the python app, then obviously the device is active
	                    ) AS source (
			                   macAddress
                               ,serialNumber
                               ,friendlyName
                               ,deviceTypeFK
                               ,deviceFirmwareFK
                               ,deviceIPAddressFK
                               ,retiredDevice
                       )
                    ON (
                        target.macAddress = source.macAddress 
                        AND target.serialNumber = source.serialNumber
                    )
                    --Honestly, this is bad code; you should likely return a SELECT to the application to see if an UPDATE is necessary. This will UPDATE a device record every time the application has data from a device.  Lots and lots of unnecessary writes.
                    WHEN MATCHED THEN 
	                    UPDATE SET 
                            target.macAddress = source.macAddress
                            , target.serialNumber = source.serialNumber
                            , target.friendlyName = source.friendlyName
                            , target.deviceTypeFK = source.deviceTypeFK
                            , target.deviceFirmwareFK = source.deviceFirmwareFK
                            , target.deviceIPAddressFK = source.deviceIPAddressFK
                            , target.retiredDevice = source.retiredDevice
                            , target.deviceChangedDate = getdate()
                    WHEN NOT MATCHED THEN 
	                    INSERT (
			                   macAddress
                               ,serialNumber
                               ,friendlyName
                               ,deviceTypeFK
                               ,deviceFirmwareFK
                               ,deviceIPAddressFK
                               ,retiredDevice
                               ,deviceChangedDate
                        )
                        VALUES(
                            source.macAddress
                            , source.serialNumber
                            , source.friendlyName
                            , source.deviceTypeFK
                            , source.deviceFirmwareFK
                            , source.deviceIPAddressFK
                            , source.retiredDevice
                            , getDate()
                        )
                    OUTPUT inserted.[deviceSK]
                    ;                    
        """,(currentDataRow[0],currentDataRow[3],currentDataRow[6],currentDeviceTypeSK,currentFirmwareSK,currentNetworkMetadataSK))
        currentDeviceSK = mssqlcursor.fetchone()
        mssqlcursor.execute("""
                    MERGE INTO Sandbox.dbo.powerScales AS target
                    USING (SELECT 
			                    %s AS unitOfPower 
	                    ) AS source (unitOfPower)
                    ON (target.unitOfPower = source.unitOfPower)
                    WHEN MATCHED THEN 
	                    UPDATE SET target.unitOfPower = source.unitOfPower
                                   ,target.scaleChangedDate = getdate()
                    WHEN NOT MATCHED THEN 
	                    INSERT (unitOfPower, scaleAddedDate)
                        VALUES(source.unitOfPower, getdate())
                    OUTPUT inserted.powerScaleSK
                    ;                    
        """,('Milliwatt'))
        currentPowerScaleSK = mssqlcursor.fetchone()
        mssqlcursor.execute("""
                    MERGE INTO Sandbox.dbo.statusList AS target
                    USING (SELECT 
			                    %s AS statusNumberRepresentation
                                ,%s AS sourceSystem
	                    ) AS source (statusNumberRepresentation, sourceSystem)
                    ON (
                        target.statusNumberRepresentation = source.statusNumberRepresentation
                        AND target.sourceSystem = source.sourceSystem
                    )
                    WHEN MATCHED THEN 
	                    UPDATE SET target.statusNumberRepresentation = source.statusNumberRepresentation
                                   ,target.sourceSystem = source.sourceSystem
                                   ,target.statusChangedDate = getdate()
                    WHEN NOT MATCHED THEN 
	                    INSERT (statusNumberRepresentation, sourceSystem, statusAddedDate)
                        VALUES(source.statusNumberRepresentation, source.sourceSystem, getdate())
                    OUTPUT inserted.statusSK
                    ;                    
        """,(currentDataRow[7],'OuimeauxPython'))
        currentstatusSK = mssqlcursor.fetchone()
        #Now that we've filled all the lookup tables for the device itself, we can store the usage data for that device (after ensuring that 
        mssqlcursor.execute("""
                            INSERT INTO Sandbox.dbo.deviceUsageData (
				                             deviceFK
				                             ,deviceSignalStrength
				                             ,deviceStateFK
				                             ,devicePowerUsage
				                             ,devicePowerScaleFK
				                             ,dataPointSampleSize
				                             ,dataPointAddedDate
	                            )
                            VALUES(
		                             %s 
		                            ,%s
		                            ,%s
		                            ,%s
		                            ,%s
		                            ,%s
                                    ,getdate()
                            )
                            ;           
        """,(currentDeviceSK, currentDataRow[2], currentstatusSK, currentDataRow[8], currentPowerScaleSK, currentDataRow[9]))
        mssqldb.commit()
        print("Finished with MS SQL Server work!")


if __name__ == "__main__":
    print("")
    print("Unit Test of Ouimeaux")
    print("---------------")

    # TODO: run from 10am to 10pm

#Initialize the database in memory:
try:
    cur = db.cursor()
    init_db(cur)

    numSecondsForDiscovery = 35
    numMinutesToGatherData = 1
    fetchDataDelaySeconds = 10
    server="10.0.60.25"
    username="ouimeaux"
    password="Gj37fAGje_@"
    mssqldatabase="Sandbox"

    #Connect to the MS SQL Server instance the database application is stored:
    mssqldb = pymssql.connect(server, username, password, "tempdb")
    mssqlcursor = mssqldb.cursor()

    while(1==1):
        currentDataSet = aggregateDeviceData(numSecondsForDiscovery=numSecondsForDiscovery,numMinutesToGatherData=numMinutesToGatherData,fetchDataDelaySeconds=fetchDataDelaySeconds,databaseCursor=cur)
        #print(currentDataSet)
        InsertOrUpdateDatabase(mssqldb,mssqlcursor,currentDataSet)

    input("Press Enter to continue...")

except (KeyboardInterrupt, SystemExit):
    print("---------------")
    print("Goodbye!")
    print("---------------")
    # Turn off all switches
    #for switch in ( env.list_switches() ):
    #    print("Turning Off: " + switch)
    #    env.get_switch( switch ).off()
