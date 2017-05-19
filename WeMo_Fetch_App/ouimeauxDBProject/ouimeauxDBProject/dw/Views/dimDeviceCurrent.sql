CREATE VIEW dw.dimDeviceCurrent AS (
SELECT deviceIK, deviceNaturalKey, macAddress, serialNumber, friendlyName, deviceTypeLabel, deviceIsSwitch, deviceIsThermostat, deviceCanMeasureEnergyUsage, deviceIsLightBulb, firmwareName, firmwareVersion, firmwareSignature, ipAddress, subnetMask, tcpIPversion, deviceFirstSeenDate, recordEffectiveDate, recordExpirationDate, isCurrent
FROM [dw].[dimDevice] dd
WHERE dd.recordExpirationDate IS NULL
)
;