﻿CREATE TABLE [dbo].[deviceTypes] (
    [deviceTypeSK]                BIGINT         CONSTRAINT [DF_deviceTypes_deviceTypeSK] DEFAULT (NEXT VALUE FOR [deviceTypeSK]) NOT NULL,
    [deviceTypeLabel]             NVARCHAR (255) NULL,
    [deviceIsSwitch]              BIT            NOT NULL,
    [deviceIsThermostat]          BIT            NOT NULL,
    [deviceCanMeasureEnergyUsage] BIT            NOT NULL,
    [deviceIsLightBulb]           BIT            NOT NULL,
    CONSTRAINT [PK_deviceTypes] PRIMARY KEY CLUSTERED ([deviceTypeSK] ASC)
);



