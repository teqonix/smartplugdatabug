CREATE TABLE [dbo].[deviceFirmware] (
    [deviceFirmwareSK]    BIGINT          CONSTRAINT [DF_deviceFirmware_deviceFirmwareSK] DEFAULT (NEXT VALUE FOR [deviceFirmwareSK]) NOT NULL,
    [firmwareName]        NVARCHAR (255)  NOT NULL,
    [firmwareVersion]     NVARCHAR (255)  NULL,
    [firmwareSignature]   NVARCHAR (1000) NULL,
    [firmwareAddedDate]   DATETIME        NULL,
    [firmwareChangedDate] DATETIME        NULL,
    [isCurrent]           BIT             NULL,
    CONSTRAINT [PK_deviceFirmware] PRIMARY KEY CLUSTERED ([deviceFirmwareSK] ASC)
);



