import sqlite3
import datetime
import pymssql
import logging
import time
import socket
import sys
import uuid
import os
import atexit
from ouimeaux.utils import get_ip_address
from ouimeaux.environment import Environment

class LocalNetworkWemoFetcher:

    def __init__(self,config_params):
        # We will use an in-memory database & table to store and aggregate our data we've pulled from our WeMo devices
        self.dbfile = str(uuid.uuid4()) + ".db"
        self.db = sqlite3.connect(self.dbfile)
        self.cur = self.db.cursor()
        # This function will create the database to store our WeMo device data;
        # since this is a simple example, it`s just one table:
        self.cur.execute('''CREATE TABLE switchDataPoints (
                            MACAddress TEXT,
                            IPAddress TEXT,
                            SignalStrength INTEGER,
                            SerialNbr TEXT,
                            ModelNbr TEXT,
                            FirmwareVersion TEXT,
                            DeviceName TEXT,
                            Status INTEGER,
                            EnergyUse INTEGER,
                            DateDataFetched DATE
                            )'''
                        )
        self.cur.execute('''CREATE TABLE averagedDataPoints (
                            MACAddress TEXT,
                            IPAddress TEXT,
                            SignalStrength INTEGER,
                            SerialNbr TEXT,
                            ModelNbr TEXT,
                            FirmwareVersion TEXT,
                            DeviceName TEXT,
                            Status INTEGER,
                            AvgEnergyUse INTEGER,
                            CountDataPoints INTEGER,
                            DateDataFetched DATE
                            )'''
                        )
        try:
            self.wemoenvironment = Environment()
            self.wemoenvironment.start()
            self.wemoenvironment.discover(config_params.get("Seconds For Environment Discovery"))
        except:
            logging.exception("Failed to initialize new instance of LocalNetworkWemoFetcher!  Ouimeaux environment did not start correctly!")
            raise
        self.config = config_params

    def getDeviceHardwareIDs(self, environment):
        current_switches = self.wemoenvironment.list_switches()
        if current_switches.__len__() == 0:
            logging.exception("No devices exist in ouimeaux environment; cannot fetch hardware data")
            raise NameError("No ouimeaux environment data exists!")

        devicehardwaredata = []
        for switchStr in (self.wemoenvironment.list_switches()):
            currentswitch = self.wemoenvironment.get_switch(switchStr)
            dict_switchinfo = currentswitch.basicevent.GetMacAddr()
            switchmac = dict_switchinfo.get("MacAddr")
            switchudnlowercase = dict_switchinfo.get("PluginUDN").lower()
            dict_switchfirmwareversion = currentswitch.firmwareupdate.GetFirmwareVersion()
            switchfirmwareversion = dict_switchfirmwareversion.get("FirmwareVersion")
            switchipaddress = currentswitch.host
            switchserialnumber = currentswitch.serialnumber
            switchmodelnbr = currentswitch.model
            dict_currentswitchattributes = {
                "Device Name": switchStr,
                "MAC Address": switchmac,
                "Universal Unique Identifier": switchudnlowercase,
                "Firmware Version": switchfirmwareversion,
                "IP Address": switchipaddress,
                "Serial Number": switchserialnumber,
                "Model Number": switchmodelnbr
            }
            devicehardwaredata.append(
                dict_currentswitchattributes
            )
        return devicehardwaredata

    def closeconnection(self):
        #Call this after ensuring data has been captured so that the temp db file is destroyed
        self.db.close()
        os.remove(self.dbfile)

    def fetchdevicedata(self):
        # print(Environment.list_switches()) #DEBUG: See what devices we grabbed during discovery
        switchPowerDataArray = []  # We will store a list of power measurements in this list and then average them before sending them to a flat file or database (we don`t need 300 measurements per minute stored in the database; it should be flattened out)
        # Fetch the current date/time into a variable, then find the date/time one minute from now; we'll use that
        currentDateTime = datetime.datetime.now()
        minuteFromNow = currentDateTime - datetime.timedelta(minutes=(-1 * self.config.get("Minutes to Gather Data")))
        currentLoopIteration = 0  # We will only gather the switch hardware / firmware details at the first iteration of fetching power data; no need to get it multiple times during execution
        deviceHardwareData = self.getDeviceHardwareIDs(self.wemoenvironment)
        while datetime.datetime.now() <= minuteFromNow:
            for wemoDevice in (deviceHardwareData):
                currentSwitch = self.wemoenvironment.get_switch(wemoDevice.get("Device Name"))
                print(currentSwitch)
                switchsignalstrength = currentSwitch.basicevent.GetSignalStrength()
                switchcurrentbinarystate = currentSwitch.basicevent.GetBinaryState()
                switchhwinfo = currentSwitch.metainfo.GetMetaInfo()
                switchmanufacture= currentSwitch.manufacture.GetManufactureData()
                if currentSwitch.model.find('Insight') > 0:
                    if currentSwitch.insight_params.get("state") == 0:
                        #API sometimes show power usage when turned off; force usage to zero when off
                        switchpowerconsumption = 0
                    else: switchpowerconsumption = currentSwitch.current_power
                    switchcurrentstate = currentSwitch.insight_params.get("state")
                datatoinsert = (
                    wemoDevice.get("MAC Address"),
                    wemoDevice.get("IP Address"),
                    float(switchsignalstrength.get("SignalStrength")),
                    wemoDevice.get("Serial Number"),
                    wemoDevice.get("Model Number"),
                    wemoDevice.get("Firmware Version"),
                    wemoDevice.get("Device Name"),
                    int(switchcurrentbinarystate.get("BinaryState")),
                    switchpowerconsumption
                )
                logging.info(datatoinsert)
                self.cur.execute(
                    '''INSERT INTO switchDataPoints(
                            MACAddress
                            , IPAddress
                            , SignalStrength
                            , SerialNbr
                            , ModelNbr
                            , FirmwareVersion
                            , DeviceName
                            , Status
                            , EnergyUse
                            , DateDataFetched
                        ) VALUES (?,?,?,?,?,?,?,?,?, datetime('now'))''',
                     datatoinsert)  # This method must iterate through the list and replace the variables (?'s) in the INSERT statement from left to right
                self.db.commit()
                derp = 1
            self.wemoenvironment.wait(self.config.get("Delay in Seconds When Fetching Data"))
        derp = 2

    def aggregateusagedata(self):
        self.cur.execute(
            '''INSERT INTO averagedDataPoints
                    SELECT
                            MACAddress
                            , MAX(IPAddress) AS IPAddress
                            , MIN(SignalStrength) AS SignalStrength
                            , SerialNbr
                            , MAX(ModelNbr) AS ModelNbr
                            , MAX(FirmwareVersion) AS FirmwareVersion
                            , DeviceName AS DeviceName
                            , MAX(Status) AS Status
                            , AVG(EnergyUse) AS EnergyUse
                            , COUNT(0) AS DataPointsCollected 
                            , datetime('now') AS DataPulledDate
                    FROM switchDataPoints
                    GROUP BY MACAddress, SerialNbr, DeviceName
            '''
        )
        self.db.commit()
        self.cur.execute(
            # Clear the ongoing log as we've already summarized and stored the averaged usage data
            '''DELETE FROM switchDataPoints'''
        )

        tablequery = '''SELECT                             
                            ROWID
                            ,MACAddress
                            ,IPAddress
                            ,SignalStrength
                            ,SerialNbr 
                            ,ModelNbr
                            ,FirmwareVersion
                            ,DeviceName
                            ,Status
                            ,AvgEnergyUse
                            ,CountDataPoints
                            ,DateDataFetched
                        FROM averagedDataPoints'''

        returnusagedata = []
        for dataRow in self.cur.execute(tablequery):
            rowdict = {
                "SQLite3 - averagedDataPoints Row ID": dataRow[0]
                ,"MAC Address": dataRow[1]
                ,"IP Address": dataRow[2]
                ,"Signal Strength": dataRow[3]
                , "Serial Number": dataRow[4]
                , "Model Number": dataRow[5]
                , "Firmware Version": dataRow[6]
                , "Device Name": dataRow[7]
                , "Device Status": dataRow[8]
                , "Average Energy Usage": dataRow[9]
                , "Data Points Collected": dataRow[10]
                , "Date Stamp for Data": dataRow[11]
            }
            returnusagedata.append(rowdict)
        return returnusagedata

    def InsertOrUpdateDatabase(self,currentDataSet):
        try:
            #Connect to the MS SQL Server instance the database application is stored:
            mssqldb = pymssql.connect(
                self.config.get("server_ip")
                , self.config.get("serviceaccount")
                , self.config.get("db_password")
                , self.config.get("databasename")
            )
            mssqlcursor = mssqldb.cursor()
            for currentDataRow in currentDataSet:
                print("Beginning work in MS SQL Server for ", currentDataRow.get("Device Name"))
                #First, we need to fill the lookup tables before we can start filling the tables with FK's to the lookups:
                mssqlcursor.execute("""
                            MERGE INTO dbo.deviceFirmware AS target
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
                """,currentDataRow.get("Firmware Version")) #http://stackoverflow.com/questions/3410455/how-do-i-use-sql-parameters-with-python
                currentFirmwareSK = mssqlcursor.fetchone()
                mssqlcursor.execute("""
                            MERGE INTO dbo.networkMetadata AS target
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
                """,(currentDataRow.get("IP Address"),'IPv4'))
                currentNetworkMetadataSK = mssqlcursor.fetchone()
                mssqlcursor.execute("""
                            MERGE INTO dbo.deviceTypes AS target
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
                """,(currentDataRow.get("Model Number")))
                currentDeviceTypeSK = mssqlcursor.fetchone()
                #Now that we have the SK's for our lookups, upsert into the IoTDevice table:
                mssqlcursor.execute("""
                            MERGE INTO dbo.IoTDevice AS target
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
                """,(currentDataRow.get("MAC Address"),currentDataRow.get("Serial Number"),currentDataRow.get("Device Name"),currentDeviceTypeSK,currentFirmwareSK,currentNetworkMetadataSK))
                currentDeviceSK = mssqlcursor.fetchone()
                mssqlcursor.execute("""
                            MERGE INTO dbo.powerScales AS target
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
                            MERGE INTO dbo.statusList AS target
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
                """,(currentDataRow.get("Device Status"),'OuimeauxPython'))
                currentstatusSK = mssqlcursor.fetchone()
                #Now that we've filled all the lookup tables for the device itself, we can store the usage data for that device (after ensuring that
                mssqlcursor.execute("""
                                    INSERT INTO dbo.deviceUsageData (
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
                """,(currentDeviceSK, currentDataRow.get("Signal Strength"), currentstatusSK, currentDataRow.get("Average Energy Usage"), currentPowerScaleSK, currentDataRow.get("Data Points Collected")))
                mssqlcursor.execute("""
                                        COMMIT;
                                    """
                                    )
                mssqldb.commit()
                self.cur.execute("DELETE FROM averagedDataPoints WHERE ROWID = ?", (int(currentDataRow.get("SQLite3 - averagedDataPoints Row ID")),))
            mssqldb.close() #end of for loop per device
        except Exception as e:
            print(e)
            print("SQL SERVER LOAD RAN INTO A PROBLEM - CONTINUING...")
            pass #Ideally, error handling should fill an in-memory python buffer that is flushed into the DB when the exception state clears, but this is a home project for data that has little value (unlike, say, money changing hands), so meh.
        print("Finished with MS SQL Server work!")