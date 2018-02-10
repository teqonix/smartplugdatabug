CREATE TABLE [acq].[deviceUsageData] (
    [deviceUsageDataSK]        BIGINT   NOT NULL,
    [deviceFK]                 BIGINT   NOT NULL,
    [deviceSignalStrength]     SMALLINT NULL,
    [deviceStateFK]            BIGINT   NULL,
    [devicePowerUsage]         INT      NULL,
    [devicePowerScaleFK]       BIGINT   NULL,
    [deviceTemperatureSetting] INT      NULL,
    [deviceCurrentTemperature] INT      NULL,
    [dataPointSampleSize]      INT      NULL,
    [dataPointAddedDate]       DATETIME NOT NULL
);

