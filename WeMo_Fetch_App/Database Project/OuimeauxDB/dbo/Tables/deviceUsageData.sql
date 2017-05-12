CREATE TABLE [dbo].[deviceUsageData] (
    [deviceUsageDataSK]        BIGINT   CONSTRAINT [DF_deviceUsageData_deviceUsageDataSK] DEFAULT (NEXT VALUE FOR [deviceUsageDataSK]) NOT NULL,
    [deviceFK]                 BIGINT   NOT NULL,
    [deviceSignalStrength]     SMALLINT NULL,
    [deviceIsActive]           BIT      NULL,
    [deviceStateFK]            BIGINT   NULL,
    [devicePowerUsage]         INT      NULL,
    [devicePowerScaleFK]       BIGINT   NULL,
    [deviceTemperatureSetting] INT      NULL,
    [deviceCurrentTemperature] INT      NULL,
    CONSTRAINT [PK_deviceUsageData] PRIMARY KEY CLUSTERED ([deviceUsageDataSK] ASC),
    CONSTRAINT [FK_deviceUsageData_IoTDevice] FOREIGN KEY ([deviceFK]) REFERENCES [dbo].[IoTDevice] ([deviceSK]),
    CONSTRAINT [FK_deviceUsageData_powerScales] FOREIGN KEY ([devicePowerScaleFK]) REFERENCES [dbo].[powerScales] ([powerScaleSK]),
    CONSTRAINT [FK_deviceUsageData_statusList] FOREIGN KEY ([deviceStateFK]) REFERENCES [dbo].[statusList] ([statusSK])
);



