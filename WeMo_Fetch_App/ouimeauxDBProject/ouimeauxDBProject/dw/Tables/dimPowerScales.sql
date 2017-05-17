CREATE TABLE [dw].[dimPowerScales] (
    [powerScaleIK]         BIGINT         CONSTRAINT [DF_dimPowerScales_powerScaleIK] DEFAULT (NEXT VALUE FOR [dw].[dimPowerScalesIK]) NOT NULL,
    [unitOfPower]          NVARCHAR (255) NULL,
    [scaleAddedDate]       DATE           NULL,
    [recordEffectiveDate]  DATE           NOT NULL,
    [recordExpirationDate] DATE           NULL,
    [isCurrent]            BIT            NOT NULL,
    CONSTRAINT [PK_dimPowerScales] PRIMARY KEY CLUSTERED ([powerScaleIK] ASC)
);

