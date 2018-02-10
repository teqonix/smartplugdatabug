CREATE TABLE [acq].[deviceTypes] (
    [deviceTypeSK]                BIGINT         NOT NULL,
    [deviceTypeLabel]             NVARCHAR (255) NULL,
    [deviceIsSwitch]              BIT            NULL,
    [deviceIsThermostat]          BIT            NULL,
    [deviceCanMeasureEnergyUsage] BIT            NULL,
    [deviceIsLightBulb]           BIT            NULL
);

