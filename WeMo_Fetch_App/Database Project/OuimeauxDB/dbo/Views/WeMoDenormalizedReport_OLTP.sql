


/****** Script for SelectTopNRows command from SSMS  ******/
CREATE VIEW [dbo].[WeMoDenormalizedReport_OLTP] AS (
SELECT 
      dud.[deviceSignalStrength]
      --,dud.[deviceStateFK]
	  ,sl.statusLabel
	  ,sl.statusNumberRepresentation
      ,CAST(dud.[devicePowerUsage] AS int) AS powerUsageMilliwatts
	  ,CAST(dud.[devicePowerUsage] AS decimal) / 1000 AS powerUsageWatts
	  ,CAST(dud.[devicePowerUsage] AS decimal) / 1000 / 1000 AS powerUsageMegawatts
      --,[devicePowerScaleFK]
      ,dud.[dataPointSampleSize]
      ,dud.[dataPointAddedDate]
	  ,id.friendlyName
	  ,ISNULL(l.locationFloor,'UNKNOWN') AS locationFloor
	  ,ISNULL(l.locationRoom,'UNKNOWN') AS locationRoom
	  ,ISNULL(l.locationName,'UNKNOWN') AS locationName
	  ,id.macAddress
	  ,id.serialNumber
	  ,id.retiredDevice
	  ,nm.ipAddress
	  ,dt.deviceTypeLabel
  FROM [dbo].[deviceUsageData] dud
	INNER JOIN IoTDevice id
		ON dud.deviceFK = id.deviceSK
	INNER JOIN networkMetadata nm
		ON id.deviceIPAddressFK = nm.networkMetadataSK
	INNER JOIN deviceTypes dt
		ON id.deviceTypeFK = dt.deviceTypeSK
	INNER JOIN statusList sl
		ON dud.deviceStateFK = sl.statusSK
	LEFT OUTER JOIN dbo.locations l
		ON id.LocationFK = l.LocationSK
--ORDER BY dataPointAddedDate DESC
)