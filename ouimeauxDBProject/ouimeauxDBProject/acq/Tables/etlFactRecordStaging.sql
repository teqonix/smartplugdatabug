CREATE TABLE [acq].[etlFactRecordStaging] (
    [deviceIK]                 BIGINT   NULL,
    [LocationIK]               BIGINT   NULL,
    [powerScaleIK]             BIGINT   NULL,
    [statusIK]                 BIGINT   NULL,
    [dateTimeIK]               BIGINT   NULL,
    [averageUsageAmount]       INT      NULL,
    [sampleSize]               INT      NULL,
    [deviceSignalStrength]     INT      NULL,
    [deviceTemperatureSetting] INT      NULL,
    [deviceCurrentTemperature] INT      NULL,
    [factEffectiveDate]        DATETIME NOT NULL,
    [maxDeviceUsageDataSK]     BIGINT   NULL
);

