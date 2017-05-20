
CREATE PROCEDURE acq.etlLogActivity
	@etlTableName nvarchar(255)
	,@etlJobID nvarchar(255)
	,@etlStartSK bigint

AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET NOCOUNT ON;

	INSERT INTO [acq].[etlLoggingTable]
			   ([etlJobID]
			   ,[etlTableName]
			   ,[etlStartRowSK]
			   ,[etlStopRowSK]
			   ,[etlJobDate])
	SELECT 
		@etlJobID AS etlJobID
		,@etlTableName AS etlTableName
		,@etlStartSK
		,MAX([maxDeviceUsageDataSK]) AS etlStopRowSK
		,MAX(factEffectiveDate) AS etlJobDate
	FROM [acq].[etlFactRecordStaging]

END
