CREATE TABLE [dbo].[IoTDevice] (
    [deviceSK]          BIGINT         CONSTRAINT [DF_IoTDevice_deviceSK] DEFAULT (NEXT VALUE FOR [deviceSK]) NOT NULL,
    [macAddress]        NVARCHAR (12)  NULL,
    [serialNumber]      NVARCHAR (75)  NULL,
    [friendlyName]      NVARCHAR (255) NULL,
    [deviceTypeFK]      BIGINT         NOT NULL,
    [deviceFirmwareFK]  BIGINT         NOT NULL,
    [deviceAddedDate]   DATETIME       CONSTRAINT [DF_IoTDevice_deviceAddedDate] DEFAULT (getdate()) NOT NULL,
    [deviceChangedDate] DATETIME       NOT NULL,
    [retiredDevice]     BIT            NOT NULL,
    [deviceIPAddressFK] BIGINT         NOT NULL,
    [LocationFK]        BIGINT         NULL,
    CONSTRAINT [PK_IoTDevice] PRIMARY KEY CLUSTERED ([deviceSK] ASC),
    CONSTRAINT [FK_IoTDevice_deviceFirmware] FOREIGN KEY ([deviceFirmwareFK]) REFERENCES [dbo].[deviceFirmware] ([deviceFirmwareSK]),
    CONSTRAINT [FK_IoTDevice_deviceTypes] FOREIGN KEY ([deviceTypeFK]) REFERENCES [dbo].[deviceTypes] ([deviceTypeSK]),
    CONSTRAINT [FK_IoTDevice_locations] FOREIGN KEY ([LocationFK]) REFERENCES [dbo].[locations] ([locationSK]),
    CONSTRAINT [FK_IoTDevice_networkMetadata] FOREIGN KEY ([deviceIPAddressFK]) REFERENCES [dbo].[networkMetadata] ([networkMetadataSK])
);







