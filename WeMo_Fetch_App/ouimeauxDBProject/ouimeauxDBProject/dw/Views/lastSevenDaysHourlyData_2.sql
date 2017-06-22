
CREATE VIEW [dw].[lastSevenDaysHourlyData] AS (
SELECT
  dw.dimDevice.macAddress
  ,dw.dimDevice.serialNumber
  ,dw.dimDevice.friendlyName
  ,dw.dimDevice.deviceTypeLabel
  ,dw.dimDevice.deviceIsSwitch
  ,dw.dimDevice.deviceCanMeasureEnergyUsage
  ,dw.dimDevice.firmwareName
  ,dw.dimDevice.firmwareVersion
  ,dw.dimDevice.ipAddress
  ,dw.dimDevice.subnetMask
  ,dw.dimLocation.locationName
  ,dw.dimLocation.locationFloor
  ,dw.dimLocation.locationRoom
  ,dw.dimPowerScales.unitOfPower
  ,dw.dimStatusList.statusLabel
  ,dw.dimStatusList.statusNumberRepresentation
  ,AVG(dw.factDeviceMeasurement.deviceSignalStrength) AS deviceSignalStrength
  ,AVG(dw.factDeviceMeasurement.devicePowerUsage / 1000) AS devicePowerUsageWatts
  ,AVG(dw.factDeviceMeasurement.dataPointSampleSize) AS dataPointSampleSize
  --,dw.dimDateQuarterHourCurrent.DateString
  --,dw.dimDateQuarterHourCurrent.MinuteOfHour
  ,dw.dimDateQuarterHourCurrent.[DateTime]
  --,dw.dimDateQuarterHourCurrent.[Day]
  --,dw.dimDateQuarterHourCurrent.DayofYear
  --,dw.dimDateQuarterHourCurrent.DayofWeek
  --,dw.dimDateQuarterHourCurrent.DayofWeekName
  --,dw.dimDateQuarterHourCurrent.Week
  --,dw.dimDateQuarterHourCurrent.[Month]
  --,dw.dimDateQuarterHourCurrent.MonthName
  --,dw.dimDateQuarterHourCurrent.Quarter
  --,dw.dimDateQuarterHourCurrent.[Year]
  ,dw.dimDateQuarterHourCurrent.IsWeekend
  ,dw.dimDateQuarterHourCurrent.IsLeapYear
FROM
  dw.factDeviceMeasurement
  INNER JOIN dw.dimLocation
    ON dw.factDeviceMeasurement.dimLocationIK = dw.dimLocation.LocationIK
  INNER JOIN dw.dimStatusList
    ON dw.factDeviceMeasurement.dimStatusListIK = dw.dimStatusList.statusIK
  INNER JOIN dw.dimPowerScales
    ON dw.factDeviceMeasurement.dimPowerScalesIK = dw.dimPowerScales.powerScaleIK
  INNER JOIN dw.dimDevice
    ON dw.factDeviceMeasurement.dimDeviceIK = dw.dimDevice.deviceIK
  INNER JOIN dw.dimDateQuarterHourCurrent
    ON dw.factDeviceMeasurement.dataPointDateIK = dw.dimDateQuarterHourCurrent.dateTimeIK
WHERE dw.dimDateQuarterHourCurrent.[Date] > DATEADD(d,-7,getdate())
GROUP BY   dw.dimDevice.macAddress
  ,dw.dimDevice.serialNumber
  ,dw.dimDevice.friendlyName
  ,dw.dimDevice.deviceTypeLabel
  ,dw.dimDevice.deviceIsSwitch
  ,dw.dimDevice.deviceCanMeasureEnergyUsage
  ,dw.dimDevice.firmwareName
  ,dw.dimDevice.firmwareVersion
  ,dw.dimDevice.ipAddress
  ,dw.dimDevice.subnetMask
  ,dw.dimDevice.deviceFirstSeenDate
  ,dw.dimLocation.locationName
  ,dw.dimLocation.locationFloor
  ,dw.dimLocation.locationRoom
  ,dw.dimPowerScales.unitOfPower
  ,dw.dimStatusList.statusLabel
  ,dw.dimStatusList.statusNumberRepresentation
  ,dw.dimDateQuarterHourCurrent.[DateTime]
  ,dw.dimDateQuarterHourCurrent.IsWeekend
  ,dw.dimDateQuarterHourCurrent.IsLeapYear
--ORDER BY dw.dimDateQuarterHourCurrent.[DateTime] DESC
)