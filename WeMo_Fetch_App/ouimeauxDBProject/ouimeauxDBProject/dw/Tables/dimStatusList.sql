CREATE TABLE [dw].[dimStatusList] (
    [statusIK]                   BIGINT         CONSTRAINT [DF_dimStatusList_statusIK] DEFAULT (NEXT VALUE FOR [dw].[dimStatusListIK]) NOT NULL,
    [statusNaturalKey]           BIGINT         NOT NULL,
    [statusLabel]                NVARCHAR (255) NULL,
    [statusNumberRepresentation] INT            NULL,
    [statusAddedDate]            DATE           NOT NULL,
    [recordEffectiveDate]        DATE           NOT NULL,
    [recordExpirationDate]       DATE           NULL,
    [isCurrent]                  BIT            NULL,
    CONSTRAINT [PK_dimStatusList] PRIMARY KEY CLUSTERED ([statusIK] ASC)
);



