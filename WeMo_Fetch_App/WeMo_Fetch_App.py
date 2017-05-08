import ouimeaux
import sqlite3
from ouimeaux.environment import Environment

db = sqlite3.connect(':memory:')

def init_db(cur):
    cur.execute('''CREATE TABLE switchDataPoints (
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
    try:
        env.start()
        env.discover(2)
        #print(env.list_switches())
        numInterationsBeforeReDiscovery = 3
        loopCount = 0
        switchPowerDataArray = [] #We will store a list of power measurements in this list and then average them before sending them to a flat file or database (we don`t need 300 measurements per minute stored in the database; it should be flattened out)

        cur = db.cursor()
        init_db(cur)

        while loopCount <= numInterationsBeforeReDiscovery:
            for switchStr in ( env.list_switches() ):
                #print( "This is the switch we are using: ", switchStr )
                currentSwitch = env.get_switch(switchStr)
                #currentSwitch.explain()
                #switchHWInfo = currentSwitch.metainfo.GetMetaInfo()
                switchMAC = currentSwitch.basicevent.GetMacAddr()
                #switchManufacture= currentSwitch.manufacture.GetManufactureData()
                switchSignalStrength = currentSwitch.basicevent.GetSignalStrength()
                switchFirmwareVersion = currentSwitch.firmwareupdate.GetFirmwareVersion()
                switchCurrentState = currentSwitch.basicevent.GetBinaryState()
                switchIPAddress = currentSwitch.host
                switchSerialNumber = currentSwitch.serialnumber
                switchModelNbr = currentSwitch.model
                switchMAClowercase = switchMAC['PluginUDN'].lower()
                #print(switchMAClowercase)
                if switchMAClowercase.find('insight') > 0:
                    #print("Insight switch found!")
                    #print( currentSwitch.insight_params.keys() )
                    #print( currentSwitch.insight_params.values() )
                    currentSwitch.insight.GetInsightParams()
                    insightCurrentPower = currentSwitch.insight_params['currentpower']
                    switchPowerDataArray.append([currentSwitch.name, switchCurrentState['BinaryState'], insightCurrentPower])
    #               print("Current switch power: " , switchPowerOutput)
                exportDataString = ( switchMAC['MacAddr'] + "|" + switchIPAddress + "|" + switchSignalStrength['SignalStrength'] + "|" + switchMAC['SerialNo'] + "|" + switchModelNbr + "|" + switchFirmwareVersion['FirmwareVersion'] + "|" + switchStr + "|" + switchCurrentState['BinaryState'] + "|" + str(insightCurrentPower) )
                print( exportDataString )
            loopCount = loopCount + 1
            env.wait(1)
            print("Current loop count: " + str(loopCount))                
        
        switchPowerDataArray.sort() #We need to sort this list before handing it off the be grouped

        currentPowerSum = 0
        for powerDataPoint in switchPowerDataArray:
            currentPowerSum = currentPowerSum + powerDataPoint[2]
            cur.execute('INSERT INTO switchDataPoints(DeviceName, Status, EnergyUse) VALUES (?,?,?)',powerDataPoint)
            db.commit()
            print(powerDataPoint)

        for dataRow in cur.execute('SELECT SUM(EnergyUse) AS SumUsage, DeviceName FROM switchDataPoints GROUP BY DeviceName'):
            print(dataRow)

        input("Press Enter to continue to next switch...")

    except (KeyboardInterrupt, SystemExit):
        print("---------------")
        print("Goodbye!")
        print("---------------")
        # Turn off all switches
        for switch in ( env.list_switches() ):
            print("Turning Off: " + switch)
            env.get_switch( switch ).off()
