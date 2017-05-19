CREATE PROCEDURE [acq].[fillEtlFactRecordStaging]
	-- Add the parameters for the stored procedure here
	@etlJobStartDateTime datetime
	,@etlStartSK bigint

AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET NOCOUNT ON;

WITH deviceUsageByQuarterHour AS (
SELECT
	[deviceUsageDataSK]
    ,deviceFK
	,id.LocationFK
    ,[deviceSignalStrength]
    ,[deviceStateFK]
    ,[devicePowerUsage]
    ,[devicePowerScaleFK]
    ,[deviceTemperatureSetting]
    ,[deviceCurrentTemperature]
    ,[dataPointSampleSize]
    ,[dataPointAddedDate]
	,CASE 
			WHEN datepart(mi,dataPointAddedDate) <= 15 THEN 0
			WHEN datepart(mi,dataPointAddedDate) > 15 AND datepart(mi,dataPointAddedDate) <= 30 THEN 15
			WHEN datepart(mi,dataPointAddedDate) > 30 AND datepart(mi,dataPointAddedDate) <= 45 THEN 30
			WHEN datepart(mi,dataPointAddedDate) > 45 AND datepart(mi,dataPointAddedDate) <= 59 THEN 45
	END AS QuarterHour
	,CONCAT(FORMAT(dud.dataPointAddedDate,'yyyy'),FORMAT(dud.dataPointAddedDate,'MM'),FORMAT(dud.dataPointAddedDate,'dd'),FORMAT(dud.dataPointAddedDate,'HH')) AS yearMonthDayHour
  FROM [Sandbox].[acq].[deviceUsageData] dud
	INNER JOIN acq.IoTDevice id
		ON dud.deviceFK = id.deviceSK
  WHERE 1=1
	AND dud.deviceUsageDataSK > @etlStartSK
)
,AggregateByQuarterHour AS (
	SELECT 
		MAX([deviceUsageDataSK]) AS maxDeviceUsageDataSK
		,AVG(devicePowerUsage) as averageUsageAmount 
		,AVG(dataPointSampleSize) sampleSize
		,AVG([deviceSignalStrength]) as deviceSignalStrength
		,AVG([deviceTemperatureSetting]) AS deviceTemperatureSetting
		,AVG([deviceCurrentTemperature]) AS deviceCurrentTemperature
		,yearMonthDayHour
		,quarterHour
		,deviceFK
		,[devicePowerScaleFK]
		,[deviceStateFK]
		,LocationFK
	FROM deviceUsageByQuarterHour dub
	GROUP BY yearMonthDayHour
		, QuarterHour
		, deviceFK	
		,[devicePowerScaleFK]
		,[deviceStateFK]
		,LocationFK
)
INSERT INTO [acq].[etlFactRecordStaging] (
	deviceIK
	, LocationIK
	, powerScaleIK
	, statusIK
	, dateTimeIK
	, averageUsageAmount
	, sampleSize
	, deviceSignalStrength
	, deviceTemperatureSetting
	, deviceCurrentTemperature
	, factEffectiveDate
	, maxDeviceUsageDataSK
)
	SELECT 
			ddc.deviceIK
			,dlc.[LocationIK]
			,dps.[powerScaleIK]
			,dsl.[statusIK]
			,dqh.dateTimeIK
			,averageUsageAmount 
			,sampleSize
			,deviceSignalStrength
			,deviceTemperatureSetting
			,deviceCurrentTemperature
			,@etlJobStartDateTime AS factEffectiveDate --This should be parameterized for the ETL job start date time
			,maxDeviceUsageDataSK
	FROM AggregateByQuarterHour abq
		LEFT OUTER JOIN dw.dimDeviceCurrent ddc
			ON abq.deviceFK = ddc.deviceNaturalKey
		LEFT OUTER JOIN dw.dimLocationCurrent dlc
			ON abq.LocationFK = dlc.[locationNaturalKey]
		LEFT OUTER JOIN dw.[dimPowerScalesCurrent] dps
			ON abq.[devicePowerScaleFK] = dps.[powerScaleNaturalKey]
		LEFT OUTER JOIN [dw].[dimStatusListCurrent] dsl
			ON abq.[deviceStateFK] = dsl.statusNaturalKey
		LEFT OUTER JOIN dw.dimDateQuarterHour dqh
			ON abq.yearMonthDayHour = dqh.[dateTimeHour]
			AND abq.quarterHour     = dqh.minuteOfHour
;

END