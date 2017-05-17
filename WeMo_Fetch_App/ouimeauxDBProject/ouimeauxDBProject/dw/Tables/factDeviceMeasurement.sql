CREATE TABLE [dw].[factDeviceMeasurement] (
    [deviceMeasurementIK]      BIGINT   CONSTRAINT [DF_factDeviceMeasurement_deviceMeasurementIK] DEFAULT (NEXT VALUE FOR [dw].[factDeviceMeasurementIK]) NOT NULL,
    [dimDeviceIK]              BIGINT   NOT NULL,
    [dimLocationIK]            BIGINT   NOT NULL,
    [dimStatusListIK]          BIGINT   NOT NULL,
    [dimPowerScalesIK]         BIGINT   NOT NULL,
    [deviceSignalStrength]     SMALLINT NULL,
    [devicePowerUsage]         INT      NULL,
    [deviceTemperatureSetting] INT      NULL,
    [dataPointSampleSize]      INT      NULL,
    [dataPointDateIK]          BIGINT   NOT NULL,
    [factEffectiveDate]        DATE     NOT NULL,
    CONSTRAINT [PK_factDeviceMeasurement] PRIMARY KEY CLUSTERED ([deviceMeasurementIK] ASC),
    CONSTRAINT [FK_factDeviceMeasurement_dimDateHour] FOREIGN KEY ([dataPointDateIK]) REFERENCES [dw].[dimDateQuarterHour] ([dateTimeIK]),
    CONSTRAINT [FK_factDeviceMeasurement_dimDevice] FOREIGN KEY ([dimDeviceIK]) REFERENCES [dw].[dimDevice] ([deviceIK]),
    CONSTRAINT [FK_factDeviceMeasurement_dimLocation] FOREIGN KEY ([dimLocationIK]) REFERENCES [dw].[dimLocation] ([LocationIK]),
    CONSTRAINT [FK_factDeviceMeasurement_dimPowerScales] FOREIGN KEY ([dimPowerScalesIK]) REFERENCES [dw].[dimPowerScales] ([powerScaleIK]),
    CONSTRAINT [FK_factDeviceMeasurement_dimStatusList] FOREIGN KEY ([dimStatusListIK]) REFERENCES [dw].[dimStatusList] ([statusIK])
);

