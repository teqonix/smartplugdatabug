CREATE PROCEDURE [acq].[etlLogJobHistory]
	-- Add the parameters for the stored procedure here
	@etlJobName nvarchar(255)
	,@etlStartStop nvarchar(25) 
	,@etlStartStopDate datetime = NULL
	,@etlStatus nvarchar(255) = NULL
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET NOCOUNT ON;

    IF @etlStartStop = 'Start'
		INSERT INTO [acq].[etlAuditLog]
				   ([etlJobName]
				   ,[etlStartOrStop]
				   ,[etlStartStopDate]
				   ,[etlJobResult])
		 VALUES
			   (
				@etlJobName
				,@etlStartStop
				,@etlStartStopDate
				,@etlStatus
			   )
		;


	IF @etlStartStop = 'Stop'
		INSERT INTO [acq].[etlAuditLog]
				   ([etlJobName]
				   ,[etlStartOrStop]
				   ,[etlStartStopDate]
				   ,[etlJobResult])
		 VALUES
			   (
				@etlJobName
				,@etlStartStop
				,getdate()
				,@etlStatus
			   )
		;	

END

GO
GRANT EXECUTE
    ON OBJECT::[acq].[etlLogJobHistory] TO [TEQNET\SSIS_SVC]
    AS [wemoSSIS];

