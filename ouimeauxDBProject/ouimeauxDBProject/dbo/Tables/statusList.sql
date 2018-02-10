CREATE TABLE [dbo].[statusList] (
    [statusSK]                   BIGINT         CONSTRAINT [DF_statusList_statusSK] DEFAULT (NEXT VALUE FOR [statusListSK]) NOT NULL,
    [statusLabel]                NVARCHAR (75)  NULL,
    [statusNumberRepresentation] INT            NULL,
    [statusAddedDate]            DATETIME       NOT NULL,
    [statusChangedDate]          DATETIME       NULL,
    [sourceSystem]               NVARCHAR (255) NULL,
    CONSTRAINT [PK_statusList] PRIMARY KEY CLUSTERED ([statusSK] ASC)
);

