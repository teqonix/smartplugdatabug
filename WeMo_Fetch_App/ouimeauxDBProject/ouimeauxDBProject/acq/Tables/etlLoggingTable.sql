CREATE TABLE [acq].[etlLoggingTable] (
    [etlJobID]      NVARCHAR (255) NOT NULL,
    [etlTableName]  NVARCHAR (255) NOT NULL,
    [etlStartRowSK] BIGINT         NOT NULL,
    [etlStopRowSK]  BIGINT         NOT NULL,
    [etlJobDate]    DATE           CONSTRAINT [DF_etlLoggingTable_etlJobDate] DEFAULT (getdate()) NOT NULL
);

