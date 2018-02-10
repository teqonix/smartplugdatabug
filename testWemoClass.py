import wemoFetchClass
import ConfigParser
import logging
import datetime


def writeRecentActivity():
    try:
        activitycheckfile = open("lastKnownActivity.log", "w")
        file.write(activitycheckfile,
                   "Last known activity in ouimeaux application: " + datetime.datetime.now().strftime(
                       "%Y-%m-%d %H:%M:%S"))
        file.close(activitycheckfile)
    except Exception as e:
        logging.exception("Couldn't write to activity log file: " + str(e.message))
        raise

if __name__ == "__main__":
    print("")
    print("Object oriented test of Local Wemo Fetch Project")
    print("-------------------------------------------------")

    logging.basicConfig(level=logging.ERROR, filename='./wemoLinuxLog.log')

    writeRecentActivity()
    config = ConfigParser.ConfigParser()
    config.readfp(open(r'config.cfg'))

    infiniteloop_param = int(config.get('LOOP BREAKER', 'infiniteloop'))

    localdb_config_parameters = {
        "db_type": config.get('Database Information', 'db_type'),
        "databasename": config.get('Database Information', 'databasename'),
        "serviceaccount": config.get('Database Information', 'serviceaccount'),
        "db_password":  config.get('Database Information', 'password'),
        "server_ip": config.get('Database Information', 'serverip'),
        "Seconds For Environment Discovery": float(config.get('API Parameters', 'numsecondsfordiscovery')),
        "Minutes to Gather Data": float(config.get('API Parameters', 'numminutestogatherdata')),
        "Delay in Seconds When Fetching Data": float(config.get('API Parameters', 'fetchdatadelayseconds')),
    }

    #Instantiate object to do all our work:
    testObject = wemoFetchClass.LocalNetworkWemoFetcher(localdb_config_parameters)

    #Used for debugging the shell script:
    # while 1 == 1:
    #     print("Endless loop!!!!!! " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    #     time.sleep(2)

    while infiniteloop_param == 1:
        try:
            #Check to see if the program should continue running based on the config:
            config.readfp(open(r'config.cfg'))
            infiniteloop_param = int(config.get('LOOP BREAKER', 'infiniteloop'))
            print("Infinite loop still in effect? " + str(infiniteloop_param))

            #Start the ouimeaux environment:
            testObject.startStopWemoEnvironment("start")

            #Fetch wemo data:
            currentdevices = testObject.getDeviceHardwareIDs(testObject.wemoenvironment)
            print(currentdevices)
            testObject.fetchdevicedata()
            datatoload = testObject.aggregateusagedata()
            print("Rows in local cache: " + str(len(datatoload))) #Show how many rows are in cache waiting to go to external DBMS

            #Try to load the data to external DBMS:
            try:
                testObject.InsertOrUpdateDatabase(datatoload)
            except Exception as e:
                logging.exception(str(e.message))
                pass

            #Stop and kill the ouimeaux environment to avoid greenlet hangs:
            testObject.startStopWemoEnvironment("stop")
            writeRecentActivity()

        except Exception as e:
            logging.exception("Unknown error in Python application: " + str(e.message))
            print(e.message)
            raise

    print("Ending program.  Infinite loop param: " + str(infiniteloop_param))

    try:
        testObject.closeconnection()
    except NameError:
        pass
