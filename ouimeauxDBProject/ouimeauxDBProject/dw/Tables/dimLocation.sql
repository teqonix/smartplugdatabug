CREATE TABLE [dw].[dimLocation] (
    [LocationIK]            BIGINT         CONSTRAINT [DF_dimLocation_LocationIK] DEFAULT (NEXT VALUE FOR [dw].[dimLocationIK]) NOT NULL,
    [locationNaturalKey]    BIGINT         NOT NULL,
    [locationName]          NVARCHAR (255) NOT NULL,
    [locationFloor]         NVARCHAR (255) NOT NULL,
    [locationRoom]          NVARCHAR (255) NOT NULL,
    [locationFirstSeenDate] DATETIME       NOT NULL,
    [recordEffectiveDate]   DATETIME       CONSTRAINT [DF_dimLocation_recordEffectiveDate] DEFAULT (getdate()) NULL,
    [recordExpirationDate]  DATETIME       NULL,
    [isCurrent]             BIT            NULL,
    CONSTRAINT [PK_dimLocation] PRIMARY KEY CLUSTERED ([LocationIK] ASC)
);

