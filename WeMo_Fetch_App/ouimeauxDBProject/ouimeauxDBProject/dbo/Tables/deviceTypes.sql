CREATE TABLE [dbo].[deviceTypes] (
    [deviceTypeSK]                BIGINT         CONSTRAINT [DF_deviceTypes_deviceTypeSK] DEFAULT (NEXT VALUE FOR [deviceTypeSK]) NOT NULL,
    [deviceTypeLabel]             NVARCHAR (255) NULL,
    [deviceIsSwitch]              BIT            NULL,
    [deviceIsThermostat]          BIT            NULL,
    [deviceCanMeasureEnergyUsage] BIT            NULL,
    [deviceIsLightBulb]           BIT            NULL,
    CONSTRAINT [PK_deviceTypes] PRIMARY KEY CLUSTERED ([deviceTypeSK] ASC)
);

