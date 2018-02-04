import wemoFetchClass
import ConfigParser
import logging

if __name__ == "__main__":
    print("")
    print("Object oriented test of Local Wemo Fetch Project")
    print("---------------")

    logging.basicConfig(level=logging.WARNING, filename='./wemoLinuxLog.log')

    config = ConfigParser.ConfigParser()
    config.readfp(open(r'config.cfg'))

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

    testObject = wemoFetchClass.LocalNetworkWemoFetcher(localdb_config_parameters)

    currentdevices = testObject.getDeviceHardwareIDs(testObject.wemoenvironment)

    print(currentdevices)

    testObject.aggregatedevicedata()

    testObject.closeconnection()
