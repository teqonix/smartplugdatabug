import wemoFetchClass

if __name__ == "__main__":
    print("")
    print("Object oriented test of Local Wemo Fetch Project")
    print("---------------")

    testObject = wemoFetchClass.localNetworkWemoFetcher()

    currentdevices = testObject.getDeviceHardwareIDs(testObject.wemoenvironment)

    print(currentdevices)
