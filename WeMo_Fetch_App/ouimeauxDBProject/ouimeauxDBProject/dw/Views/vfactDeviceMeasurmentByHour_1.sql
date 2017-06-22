
CREATE VIEW [dw].[vfactDeviceMeasurmentByHour] AS (
SELECT --The grain of the actual fact table is at the 15 minute level, but this view should be used for aggregating hourly date (kiloWatt Hours, specifically).  Therefore, we need to aggregate and group at the hour level and get rid of any IK's at the lower level
	MAX(fdm.deviceMeasurementIK) AS deviceMeasurementIK
	,fdm.dimDeviceIK
	, MIN(fdm.dataPointDateIK) AS dataPointDateIK 
	, fdm.dimLocationIK
	, fdm.dimStatusListIK
	, fdm.dimPowerScalesIK
	, AVG(fdm.deviceSignalStrength) AS deviceSignalStrength
	, AVG(fdm.devicePowerUsage) AS devicePowerUsage
	, ROUND(AVG(CAST(fdm.devicePowerUsage AS DECIMAL)) / 1000,0) AS devicePowerUsageWatts
	, AVG(fdm.dataPointSampleSize) AS dataPointSampleSize
FROM [dw].[factDeviceMeasurement] fdm
	INNER JOIN dw.dimDateQuarterHour dqh
		ON fdm.dataPointDateIK = dqh.dateTimeIK
GROUP BY 
	fdm.dimDeviceIK
	, fdm.dimLocationIK
	, fdm.dimStatusListIK
	, fdm.dimPowerScalesIK
	, dqh.dateTimeHour
)
;