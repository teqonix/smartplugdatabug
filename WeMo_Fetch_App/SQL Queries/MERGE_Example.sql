MERGE INTO deviceFirmware AS target
USING (SELECT 
			'testfirmwarelalalaal' AS firmwareName
			,'v0.5' AS firmwareVersion
	) AS source (firmwareName, firmwareVersion)
ON (target.firmwareName = source.firmwareName)
WHEN MATCHED THEN 
	UPDATE SET target.firmwareName = source.firmwareName
		,target.firmwareVersion = source.firmwareVersion
WHEN NOT MATCHED THEN 
	INSERT (firmwareName, firmwareVersion)
	VALUES (source.firmwareName, source.firmwareVersion);
;

--Msg 11742, Level 15, State 1, Line 12
--NEXT VALUE FOR function can only be used with MERGE if it is defined within a default constraint on the target table for insert actions. 




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


