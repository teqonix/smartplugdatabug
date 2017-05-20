CREATE TABLE [acq].[etlAuditLog] (
    [etlJobName]       NVARCHAR (255) NOT NULL,
    [etlStartOrStop]   NVARCHAR (25)  NOT NULL,
    [etlStartStopDate] DATETIME       NOT NULL,
    [etlJobResult]     NVARCHAR (255) NULL
);

