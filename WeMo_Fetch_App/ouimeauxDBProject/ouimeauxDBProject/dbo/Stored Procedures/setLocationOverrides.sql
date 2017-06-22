
CREATE PROCEDURE [dbo].[setLocationOverrides]
	
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET NOCOUNT ON;

	BEGIN TRANSACTION

	--If a new serial number is found in the OLTP schema, add it to the location override table 
	MERGE [dbo].[locationOverride] AS TARGET
	USING (SELECT serialNumber FROM dbo.IoTDevice) AS SOURCE
		ON source.serialNumber = target.deviceserialNumber
	WHEN NOT MATCHED 
		THEN INSERT (
						deviceSerialNumber
						, locationName
						, locationFloor
						, locationRoom
						, overrideAddedDate
					) 
			VALUES (
					source.serialNumber
					,'Unknown Location'
					,'Unknown Floor'
					,'Unknown Room'
					,GETDATE()
			)
	;
	
	COMMIT;

	BEGIN TRANSACTION

	--If we found a new location permutation in the locationOverride table, add it to the locations table:
	MERGE dbo.locations AS TARGET
	USING (
			SELECT DISTINCT lo.locationName
				,lo.locationFloor
				,lo.locationRoom
			FROM dbo.locationOverride lo 
		) AS source
			ON source.locationName = target.locationName
			AND source.locationFloor = target.locationFloor
			AND source.locationRoom = target.locationRoom
	WHEN NOT MATCHED THEN 
		INSERT (locationName, locationFloor, locationRoom, locationAddedDate)
		VALUES (source.locationName, source.locationFloor , source.locationRoom, GETDATE())
	;

	COMMIT;

	BEGIN TRANSACTION

	--Fetch the locationSK from the location table based on the locationOverride table..  This join honestly sucks because it's varchar based, but that`s okay because this is such a small scale solution
	--If we're being honest, the database shouldn't even need to do this; the application shouldn`t send false data to the DB
	MERGE dbo.IoTDevice AS TARGET
	USING (
			SELECT 
				lo.deviceSerialNumber
				,lo.locationName
				,lo.locationFloor
				,lo.locationRoom
				,ISNULL(l.locationSK,-1) AS locationFK --Set the default value to -1 if nothing was found in the master location table (which is the unknown value)
			FROM dbo.locationOverride lo
				LEFT OUTER JOIN dbo.locations l
					ON lo.locationName = l.locationName
					AND lo.locationFloor = l.locationFloor
					AND lo.locationRoom = l.locationRoom
		) AS SOURCE
			ON source.deviceSerialNumber = target.serialNumber
	WHEN MATCHED THEN 
		UPDATE SET LocationFK = source.locationFK
	;

	COMMIT;

END
GO
GRANT EXECUTE
    ON OBJECT::[dbo].[setLocationOverrides] TO [TEQNET\SSIS_SVC]
    AS [dbo];


GO
GRANT EXECUTE
    ON OBJECT::[dbo].[setLocationOverrides] TO [wemoSSIS]
    AS [dbo];

