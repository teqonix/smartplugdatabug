MERGE INTO deviceFirmware AS target
USING (SELECT 
			'testdsfasdffirmflalalaal' AS firmwareName
			,'v99.5' AS firmwareVersion
	) AS source (firmwareName, firmwareVersion)
ON (target.firmwareName = source.firmwareName)
WHEN MATCHED THEN 
	UPDATE SET target.firmwareName = source.firmwareName
		,target.firmwareVersion = source.firmwareVersion
WHEN NOT MATCHED THEN 
	INSERT (firmwareName, firmwareVersion)
	VALUES (source.firmwareName, source.firmwareVersion)
OUTPUT inserted.[deviceFirmwareSK]
;

--Msg 11742, Level 15, State 1, Line 12
--NEXT VALUE FOR function can only be used with MERGE if it is defined within a default constraint on the target table for insert actions. 


MERGE INTO Sandbox.dbo.statusList AS target
USING (SELECT 
			%s AS statusNumberRepresentation
            ,%s AS sourceSystem
	) AS source (statusNumberRepresentation, sourceSystem)
ON (
    target.statusNumberRepresentation = source.statusNumberRepresentation
    AND target.sourceSystem = source.sourceSystem
)
WHEN MATCHED THEN 
	UPDATE SET target.statusNumberRepresentation = source.statusNumberRepresentation
                ,target.sourceSystem = source.sourceSystem
                ,target.statusChangedDate = getdate()
WHEN NOT MATCHED THEN 
	INSERT (statusNumberRepresentation, sourceSystem, statusAddedDate)
    VALUES(source.statusNumberRepresentation, source.sourceSystem, getdate())
OUTPUT inserted.statusSK
;         



USE [Sandbox]
GO

INSERT INTO [dbo].[deviceFirmware]
           ([deviceFirmwareSK]
           ,[firmwareName]
           ,[firmwareVersion]
           ,[firmwareSignature]
           ,[firmwareAddedDate]
           ,[firmwareChangedDate]
           ,[isCurrent])
     VALUES
           (<deviceFirmwareSK, bigint,>
           ,<firmwareName, nvarchar(255),>
           ,<firmwareVersion, nvarchar(255),>
           ,<firmwareSignature, nvarchar(1000),>
           ,<firmwareAddedDate, datetime,>
           ,<firmwareChangedDate, datetime,>
           ,<isCurrent, bit,>)
GO

;

