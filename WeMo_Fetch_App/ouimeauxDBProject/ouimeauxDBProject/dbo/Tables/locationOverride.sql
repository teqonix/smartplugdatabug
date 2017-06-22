CREATE TABLE [dbo].[locationOverride] (
    [locationOverrideSK] BIGINT         CONSTRAINT [DF_Table_1_locationOverrideIK] DEFAULT (NEXT VALUE FOR [dbo].[locationOverrideSK]) NOT NULL,
    [deviceSerialNumber] NVARCHAR (75)  NOT NULL,
    [locationName]       NVARCHAR (255) NOT NULL,
    [locationFloor]      NVARCHAR (255) NOT NULL,
    [locationRoom]       NVARCHAR (255) NOT NULL,
    [overrideAddedDate]  DATETIME       CONSTRAINT [DF_locationOverride_overrideAddedDate] DEFAULT (getdate()) NOT NULL,
    CONSTRAINT [PK_locationOverride] PRIMARY KEY CLUSTERED ([locationOverrideSK] ASC)
);

