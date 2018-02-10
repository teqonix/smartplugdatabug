CREATE TABLE [dbo].[powerScales] (
    [powerScaleSK]     BIGINT        CONSTRAINT [DF_powerScales_powerScaleSK] DEFAULT (NEXT VALUE FOR [powerScaleSK]) NOT NULL,
    [unitOfPower]      NVARCHAR (60) NULL,
    [scaleAddedDate]   DATETIME      NULL,
    [scaleChangedDate] DATETIME      NULL,
    CONSTRAINT [PK_powerScales] PRIMARY KEY CLUSTERED ([powerScaleSK] ASC)
);

