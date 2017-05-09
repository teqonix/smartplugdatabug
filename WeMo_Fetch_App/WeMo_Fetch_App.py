import ouimeaux
import sqlite3
import datetime
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

if __name__ == "__main__":
    print("")
    print("Unit Test of Ouimeaux")
    print("---------------")
    env = Environment()
    # TODO: run from 10am to 10pm

    #Initialize the database in memory:
    cur = db.cursor()
    init_db(cur)

    try:
        env.start()
        env.discover(2)
        #print(env.list_switches()) #DEBUG: See what devices we grabbed during discovery
        numMinutesToGatherData = 0.10
        fetchDataDelaySeconds = 2
        nbrLoopsBeforeRediscovery = 10
        switchPowerDataArray = [] #We will store a list of power measurements in this list and then average them before sending them to a flat file or database (we don`t need 300 measurements per minute stored in the database; it should be flattened out)

        #Fetch the current date/time into a variable, then find the date/time one minute from now; we'll use that 
        currentDateTime = datetime.datetime.now()
        minuteFromNow = currentDateTime - datetime.timedelta(minutes=(-1 * numMinutesToGatherData))

        currentLoopIteration = 0 #We will only gather the switch hardware / firmware details at the first iteration of fetching power data; no need to get it multiple times during execution
        while datetime.datetime.now() <= minuteFromNow:
            for switchStr in ( env.list_switches() ):
                currentSwitch = env.get_switch(switchStr)
                if currentLoopIteration == 0: #Only gather hardware details the first loop iteration and store them in memory
                    switchMAC = currentSwitch.basicevent.GetMacAddr()
                    switchUDNlowercase = switchMAC['PluginUDN'].lower()
                    switchFirmwareVersion = currentSwitch.firmwareupdate.GetFirmwareVersion()
                    switchIPAddress = currentSwitch.host
                    switchSerialNumber = currentSwitch.serialnumber
                    switchModelNbr = currentSwitch.model
                switchSignalStrength = currentSwitch.basicevent.GetSignalStrength()
                switchCurrentState = currentSwitch.basicevent.GetBinaryState()
                #print(switchUDNlowercase)
                #print( "This is the switch we are using: ", switchStr )                
                #currentSwitch.explain()ccc
                #switchHWInfo = currentSwitch.metainfo.GetMetaInfo()
                #switchManufacture= currentSwitch.manufacture.GetManufactureData()
                if switchUDNlowercase.find('insight') > 0:
                    #print("Insight switch found!")
                    #print( currentSwitch.insight_params.keys() )
                    #print( currentSwitch.insight_params.values() )
                    currentSwitch.insight.GetInsightParams()
                    insightCurrentPower = currentSwitch.insight_params['currentpower']
                    switchPowerDataArray.append([switchMAC['MacAddr'], switchIPAddress, switchSignalStrength['SignalStrength'], switchMAC['SerialNo'], switchModelNbr, switchFirmwareVersion['FirmwareVersion'], switchStr, switchCurrentState['BinaryState'], insightCurrentPower])                    
                                                    #[currentSwitch.name, switchCurrentState['BinaryState'], insightCurrentPower]) #old
    #               print("Current switch power: " , switchPowerOutput)
                exportDataString = (switchMAC['MacAddr'] + "|" + switchIPAddress + "|" + switchSignalStrength['SignalStrength'] + "|" + switchMAC['SerialNo'] + "|" + switchModelNbr + "|" + switchFirmwareVersion['FirmwareVersion'] + "|" + switchStr + "|" + switchCurrentState['BinaryState'] + "|" + str(insightCurrentPower) )
                print( exportDataString )
            currentLoopIteration = currentLoopIteration + 1
            env.wait(fetchDataDelaySeconds)
            print("Current loop count: " + str(currentLoopIteration))

        currentPowerSum = 0
        for powerDataPoint in switchPowerDataArray:
            currentPowerSum = currentPowerSum + powerDataPoint[8]
            cur.execute('INSERT INTO switchDataPoints(MACAddress, IPAddress, SignalStrength, SerialNbr, ModelNbr, FirmwareVersion, DeviceName, Status, EnergyUse) VALUES (?,?,?,?,?,?,?,?,?)',powerDataPoint) #This method must iterate through the list and replace the variables (?'s) in the INSERT statement from left to right
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
	                        , datetime(datetime(), 'localtime') AS DataPulledDate
                    FROM switchDataPoints
                    GROUP BY DeviceName, MACAddress, SerialNbr"""

        for dataRow in cur.execute(tableQuery):
            print(dataRow)

        input("Press Enter to continue...")

    except (KeyboardInterrupt, SystemExit):
        print("---------------")
        print("Goodbye!")
        print("---------------")
        # Turn off all switches
        #for switch in ( env.list_switches() ):
        #    print("Turning Off: " + switch)
        #    env.get_switch( switch ).off()
