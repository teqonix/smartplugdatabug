CREATE TABLE [acq].[statusList] (
    [statusSK]                   BIGINT         NOT NULL,
    [statusLabel]                NVARCHAR (75)  NULL,
    [statusNumberRepresentation] INT            NULL,
    [statusAddedDate]            DATETIME       NOT NULL,
    [statusChangedDate]          DATETIME       NULL,
    [sourceSystem]               NVARCHAR (255) NULL
);

