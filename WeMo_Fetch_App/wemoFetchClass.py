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
                            EnergyUse INTEGER
                            )'''
                        )
        self.wemoenvironment = Environment()
        self.config = config_params

    def getDeviceHardwareIDs(self, environment):
        current_switches = self.wemoenvironment.list_switches()
        if current_switches.__len__() == 0:
            self.wemoenvironment.start()
            self.wemoenvironment.discover(5)

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
                "MAC Address": switchmac,
                "Universal Unique Identifier": switchudnlowercase,
                "Firmware Version": switchfirmwareversion,
                "IP Address": switchipaddress,
                "Serial Number": switchserialnumber,
                "Model Number:": switchmodelnbr
            }
            devicehardwaredata.append(
                dict_currentswitchattributes
            )
        return devicehardwaredata

    def closeconnection(self):
        self.db.close()
        os.remove(self.dbfile)

    # def aggregatedevicedata(self, numSecondsForDiscovery, numMinutesToGatherData, fetchDataDelaySeconds, databaseCursor):
    #     test_ip_addr = "127.0.0.1"  # get_ip_address()
    #     test_port = 54321
    #
    #     # Set up a socket using the same port that ouimeaux uses so we can kill it if it's still in use for some reason
    #     test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     try:
    #         test_socket.bind((test_ip_addr, test_port))
    #     except socket.error as e:
    #         if e.errno == 98:
    #             print("Port is already in use")
    #             sys.exit(e)
    #         else:
    #             # something else raised the socket.error exception
    #             print(e)
    #
    #     try:
    #         env.start()
    #     except OSError as err:
    #         print("Error Occurred!", err)
    #         logging.exception("OSError Occurred when setting up a ouimeaux environment..")
    #         env.upnp.server.stop()
    #         env.registry.server.stop()
    #         del env
    #         raise
    #
    #     databaseCursor.execute(
    #         'DELETE FROM switchDataPoints')  # Remove any existing data from this table, as it should`ve already been stored elsewhere
    #     env.discover(numSecondsForDiscovery)
    #     # print(Environment.list_switches()) #DEBUG: See what devices we grabbed during discovery
    #     switchPowerDataArray = []  # We will store a list of power measurements in this list and then average them before sending them to a flat file or database (we don`t need 300 measurements per minute stored in the database; it should be flattened out)
    #     switchPowerDataArray.clear()
    #     # Fetch the current date/time into a variable, then find the date/time one minute from now; we'll use that
    #     currentDateTime = datetime.datetime.now()
    #     minuteFromNow = currentDateTime - datetime.timedelta(minutes=(-1 * numMinutesToGatherData))
    #     currentLoopIteration = 0  # We will only gather the switch hardware / firmware details at the first iteration of fetching power data; no need to get it multiple times during execution
    #     deviceHardwareData = getDeviceHardwareIDs(env)
    #     while datetime.datetime.now() <= minuteFromNow:
    #         for switchStr in (env.list_switches()):
    #             currentSwitch = env.get_switch(switchStr)
    #             switchMAC = currentSwitch.basicevent.GetMacAddr()
    #             for index, deviceHardwareIDRow in enumerate(deviceHardwareData):
    #                 if switchMAC == deviceHardwareIDRow[0]:
    #                     # print("Oh hey we found the matching device for: " + deviceHardwareIDRow[0]['MacAddr'])
    #                     currentSwitchHardwareIndex = index
    #             switchSignalStrength = currentSwitch.basicevent.GetSignalStrength()
    #             switchCurrentState = currentSwitch.basicevent.GetBinaryState()
    #             # print(switchUDNlowercase)
    #             # print( "This is the switch we are using: ", switchStr )
    #             # currentSwitch.explain()ccc
    #             # switchHWInfo = currentSwitch.metainfo.GetMetaInfo()
    #             # switchManufacture= currentSwitch.manufacture.GetManufactureData()
    #             if deviceHardwareData[currentSwitchHardwareIndex][1].find('insight') > 0:
    #                 # print("Insight switch found!")
    #                 # print( currentSwitch.insight_params.keys() )
    #                 # print( currentSwitch.insight_params.values() )
    #                 currentSwitch.insight.GetInsightParams()
    #                 if switchCurrentState[
    #                     'BinaryState'] == '0':  # There seems to be a bug in the Ouimeaux API that keeps returning energy usage when a plug is off; it seems rare, but it is happening in the data
    #                     insightCurrentPower = 0
    #                 else:
    #                     insightCurrentPower = currentSwitch.insight_params['currentpower']
    #                 switchPowerDataArray.append([deviceHardwareData[currentSwitchHardwareIndex][0]['MacAddr']
    #                                                 , deviceHardwareData[currentSwitchHardwareIndex][3]
    #                                                 , switchSignalStrength['SignalStrength']
    #                                                 , deviceHardwareData[currentSwitchHardwareIndex][0]['SerialNo']
    #                                                 , deviceHardwareData[currentSwitchHardwareIndex][5]
    #                                                 , deviceHardwareData[currentSwitchHardwareIndex][2]['FirmwareVersion']
    #                                                 , switchStr
    #                                                 , switchCurrentState['BinaryState']
    #                                                 , insightCurrentPower]
    #                                             )
    #             exportDataString = ([deviceHardwareData[currentSwitchHardwareIndex][0]['MacAddr'],
    #                                  deviceHardwareData[currentSwitchHardwareIndex][3],
    #                                  switchSignalStrength['SignalStrength'],
    #                                  deviceHardwareData[currentSwitchHardwareIndex][0]['SerialNo'],
    #                                  deviceHardwareData[currentSwitchHardwareIndex][5],
    #                                  deviceHardwareData[currentSwitchHardwareIndex][2]['FirmwareVersion'], switchStr,
    #                                  switchCurrentState['BinaryState'], insightCurrentPower])
    #             print(exportDataString)
    #         currentLoopIteration = currentLoopIteration + 1
    #         env.wait(fetchDataDelaySeconds)
    #         # print("Current loop count: " + str(currentLoopIteration))
    #     currentPowerSum = 0
    #     for powerDataPoint in switchPowerDataArray:
    #         currentPowerSum = currentPowerSum + powerDataPoint[8]
    #         databaseCursor.execute(
    #             'INSERT INTO switchDataPoints(MACAddress, IPAddress, SignalStrength, SerialNbr, ModelNbr, FirmwareVersion, DeviceName, Status, EnergyUse) VALUES (?,?,?,?,?,?,?,?,?)',
    #             powerDataPoint)  # This method must iterate through the list and replace the variables (?'s) in the INSERT statement from left to right
    #         db.commit()
    #         # print(powerDataPoint)
    #     # Average out the data points collected throughout looping through the above logic and group it by device.  This will go into the permanent database.
    #     tableQuery = """SELECT
    #                         MACAddress
    #                         , MAX(IPAddress) AS IPAddress
    #                         , MIN(SignalStrength) AS SignalStrength
    #                         , SerialNbr
    #                         , MAX(ModelNbr) AS ModelNbr
    #                         , MAX(FirmwareVersion) AS FirmwareVersion
    #                         , MIN(DeviceName) AS DeviceName
    #                         , MAX(Status) AS Status
    #                         , AVG(EnergyUse) AS EnergyUse
    #                         , COUNT(0) AS dataPointsAggregated
    #                         , datetime(datetime(), 'localtime') AS DataPulledDate
    #                 FROM switchDataPoints
    #                 GROUP BY MACAddress, SerialNbr"""
    #     returnData = []
    #     for dataRow in databaseCursor.execute(tableQuery):
    #         returnData.append(dataRow)
    #
    #     tableQuery = """
    #                      SELECT
    #                         MACAddress,
    #                         IPAddress,
    #                         SignalStrength,
    #                         SerialNbr,
    #                         ModelNbr,
    #                         FirmwareVersion,
    #                         DeviceName,
    #                         Status,
    #                         EnergyUse
    #                      FROM switchDataPoints
    #                  """
    #     # Debug query and output to see detail data in the database table:
    #     # for detailData in databaseCursor.execute(tableQuery):
    #     #    print(detailData)
    #
    #     # I had to manually kill the UPnP server and remove the ouimeaux environment in order to fetch the device name in case it changed since the last call to this function
    #     env.upnp.server.stop()
    #     env.registry.server.stop()
    #     del env
    #     return returnData