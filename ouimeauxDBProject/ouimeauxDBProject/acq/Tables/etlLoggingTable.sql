CREATE TABLE [acq].[etlLoggingTable] (
    [etlJobID]      NVARCHAR (255) NOT NULL,
    [etlTableName]  NVARCHAR (255) NOT NULL,
    [etlStartRowSK] BIGINT         NOT NULL,
    [etlStopRowSK]  BIGINT         NOT NULL,
    [etlJobDate]    DATETIME       CONSTRAINT [DF_etlLoggingTable_etlJobDate] DEFAULT (getdate()) NOT NULL,
    [etlLogSK]      BIGINT         CONSTRAINT [DF_etlLoggingTable_etlLogSK] DEFAULT (NEXT VALUE FOR [acq].[etlLoggingTableSK]) NOT NULL,
    CONSTRAINT [PK_etlLoggingTable] PRIMARY KEY CLUSTERED ([etlLogSK] ASC)
);

