CREATE PROCEDURE acq.getIncrimentalTableSK
	@tableName varchar(255)
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET NOCOUNT ON;

    -- Insert statements for procedure here
  SELECT MAX(etlStopRowSK) AS startETLRowSK
  FROM acq.etlLoggingTable
  WHERE etlTableName = @tableName
  ;

END

GO
GRANT EXECUTE
    ON OBJECT::[acq].[getIncrimentalTableSK] TO [TEQNET\SSIS_SVC]
    AS [wemoSSIS];

