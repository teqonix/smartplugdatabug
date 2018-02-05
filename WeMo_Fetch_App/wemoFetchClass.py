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

    def aggregatedevicedata(self):
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


                # if deviceHardwareData[currentSwitchHardwareIndex][1].find('insight') > 0:
                    # print("Insight switch found!")
                    # print( currentSwitch.insight_params.keys() )
                    # print( currentSwitch.insight_params.values() )
            #         currentSwitch.insight.GetInsightParams()
            #         if switchCurrentState[
            #             'BinaryState'] == '0':  # There seems to be a bug in the Ouimeaux API that keeps returning energy usage when a plug is off; it seems rare, but it is happening in the data
            #             insightCurrentPower = 0
            #         else:
            #             insightCurrentPower = currentSwitch.insight_params['currentpower']
            #         switchPowerDataArray.append([deviceHardwareData[currentSwitchHardwareIndex][0]['MacAddr']
            #                                         , deviceHardwareData[currentSwitchHardwareIndex][3]
            #                                         , switchSignalStrength['SignalStrength']
            #                                         , deviceHardwareData[currentSwitchHardwareIndex][0]['SerialNo']
            #                                         , deviceHardwareData[currentSwitchHardwareIndex][5]
            #                                         , deviceHardwareData[currentSwitchHardwareIndex][2]['FirmwareVersion']
            #                                         , switchStr
            #                                         , switchCurrentState['BinaryState']
            #                                         , insightCurrentPower]
            #                                     )
            #     exportDataString = ([deviceHardwareData[currentSwitchHardwareIndex][0]['MacAddr'],
            #                          deviceHardwareData[currentSwitchHardwareIndex][3],
            #                          switchSignalStrength['SignalStrength'],
            #                          deviceHardwareData[currentSwitchHardwareIndex][0]['SerialNo'],
            #                          deviceHardwareData[currentSwitchHardwareIndex][5],
            #                          deviceHardwareData[currentSwitchHardwareIndex][2]['FirmwareVersion'], switchStr,
            #                          switchCurrentState['BinaryState'], insightCurrentPower])
            #     print(exportDataString)
            # currentLoopIteration = currentLoopIteration + 1
            # env.wait(fetchDataDelaySeconds)
            # print("Current loop count: " + str(currentLoopIteration))
        # currentPowerSum = 0
        # for powerDataPoint in switchPowerDataArray:
        #     currentPowerSum = currentPowerSum + powerDataPoint[8]

            # print(powerDataPoint)
        # Average out the data points collected throughout looping through the above logic and group it by device.  This will go into the permanent database.
        # tableQuery = """SELECT
        #                     MACAddress
        #                     , MAX(IPAddress) AS IPAddress
        #                     , MIN(SignalStrength) AS SignalStrength
        #                     , SerialNbr
        #                     , MAX(ModelNbr) AS ModelNbr
        #                     , MAX(FirmwareVersion) AS FirmwareVersion
        #                     , MIN(DeviceName) AS DeviceName
        #                     , MAX(Status) AS Status
        #                     , AVG(EnergyUse) AS EnergyUse
        #                     , COUNT(0) AS dataPointsAggregated
        #                     , datetime(datetime(), 'localtime') AS DataPulledDate
        #             FROM switchDataPoints
        #             GROUP BY MACAddress, SerialNbr"""
        # returnData = []
        # for dataRow in databaseCursor.execute(tableQuery):
        #     returnData.append(dataRow)
        #
        # tableQuery = """
        #                  SELECT
        #                     MACAddress,
        #                     IPAddress,
        #                     SignalStrength,
        #                     SerialNbr,
        #                     ModelNbr,
        #                     FirmwareVersion,
        #                     DeviceName,
        #                     Status,
        #                     EnergyUse
        #                  FROM switchDataPoints
        #              """
        # Debug query and output to see detail data in the database table:
        # for detailData in databaseCursor.execute(tableQuery):
        #    print(detailData)

        # I had to manually kill the UPnP server and remove the ouimeaux environment in order to fetch the
        #    device name in case it changed since the last call to this function
        # env.upnp.server.stop()
        # env.registry.server.stop()
        # del env
        # return returnData

    # databaseCursor.execute(
    #     'DELETE FROM switchDataPoints')  # Remove any existing data from this table, as it should`ve already been stored elsewhere