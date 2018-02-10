CREATE TABLE [dbo].[deviceFirmware] (
    [deviceFirmwareSK]    BIGINT          CONSTRAINT [DF_deviceFirmware_deviceFirmwareSK] DEFAULT (NEXT VALUE FOR [deviceFirmwareSK]) NOT NULL,
    [firmwareName]        NVARCHAR (255)  NOT NULL,
    [firmwareVersion]     NVARCHAR (255)  NULL,
    [firmwareSignature]   NVARCHAR (1000) NULL,
    [firmwareAddedDate]   DATETIME        CONSTRAINT [DF_deviceFirmware_firmwareAddedDate] DEFAULT (getdate()) NULL,
    [firmwareChangedDate] DATETIME        NULL,
    [isCurrent]           BIT             CONSTRAINT [DF_deviceFirmware_isCurrent] DEFAULT ((1)) NULL,
    CONSTRAINT [PK_deviceFirmware] PRIMARY KEY CLUSTERED ([deviceFirmwareSK] ASC)
);

