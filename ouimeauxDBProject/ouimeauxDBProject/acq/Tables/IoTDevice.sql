CREATE TABLE [acq].[IoTDevice] (
    [deviceSK]          BIGINT         NOT NULL,
    [macAddress]        NVARCHAR (12)  NULL,
    [serialNumber]      NVARCHAR (75)  NULL,
    [friendlyName]      NVARCHAR (255) NULL,
    [deviceTypeFK]      BIGINT         NOT NULL,
    [deviceFirmwareFK]  BIGINT         NOT NULL,
    [deviceAddedDate]   DATETIME       NOT NULL,
    [deviceChangedDate] DATETIME       NOT NULL,
    [retiredDevice]     BIT            NOT NULL,
    [deviceIPAddressFK] BIGINT         NOT NULL,
    [LocationFK]        BIGINT         NULL
);

