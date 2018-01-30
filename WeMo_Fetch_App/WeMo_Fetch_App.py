

def InsertOrUpdateDatabase(server,username,password,mssqldatabase,currentDataSet):
    try:
        #Connect to the MS SQL Server instance the database application is stored:
        mssqldb = pymssql.connect(server, username, password, mssqldatabase)
        mssqlcursor = mssqldb.cursor()    
        for currentDataRow in currentDataSet:
            print("Beginning work in MS SQL Server for ", currentDataRow[0])
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
            mssqlcursor.execute("""
                                    COMMIT;
                                """
                                )
            mssqldb.commit()
        mssqldb.close() #end of for loop per device    
    except Exception as e: 
        print(e)
        print("SQL SERVER LOAD RAN INTO A PROBLEM - CONTINUING...")
        pass #Ideally, error handling should fill an in-memory python buffer that is flushed into the DB when the exception state clears, but this is a home project for data that has little value (unlike, say, money changing hands), so meh.
    print("Finished with MS SQL Server work!")


if __name__ == "__main__":
    print("")
    print("Unit Test of Ouimeaux")
    print("---------------")

    # TODO: run from 10am to 10pm

#Initialize the database in memory:
try:

    logging.basicConfig(level=logging.WARNING, filename='C:\Temp\ouimeauxDEBUG.log')
    numSecondsForDiscovery = 25
    numMinutesToGatherData = 1
    fetchDataDelaySeconds = 10
    server="10.0.60.25"
    username="ouimeaux"
    password="Gj37fAGje_@"
    mssqldatabase="Sandbox"

    while(1==1):
        try:
            currentDataSet = aggregateDeviceData(numSecondsForDiscovery=numSecondsForDiscovery,numMinutesToGatherData=numMinutesToGatherData,fetchDataDelaySeconds=fetchDataDelaySeconds,databaseCursor=cur)
            #if(currentDataSet == -1):
            #    print("An error occurred in the aggregateDeviceData call!  Exiting..")
            #    sys.exit()
            print(currentDataSet)
            #try:
            if currentDataSet != None: 
                InsertOrUpdateDatabase(server,username,password,mssqldatabase,currentDataSet)
            print(datetime.datetime.now())
        except:
            errorText = ("Something went wrong on: " , datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            logging.exception(errorText)            #time.sleep(30)
            sys.exit(1)
            #print("SQL Server work had a problem!")
            #print(err_text)
            #pass #Ideally, there should be a buffer that gets filled and the data should build until all of it can be flushed into the DB, sucessfully but I'm lazy today (2017-05-20).  Thus, we're just leaving it behind


    input("Press Enter to continue...")

except (KeyboardInterrupt, SystemExit):
    print("---------------")
    print("Goodbye!")
    print("---------------")
