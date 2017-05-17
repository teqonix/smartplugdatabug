CREATE TABLE [acq].[deviceFirmware] (
    [deviceFirmwareSK]    BIGINT          NULL,
    [firmwareName]        NVARCHAR (255)  NOT NULL,
    [firmwareVersion]     NVARCHAR (255)  NULL,
    [firmwareSignature]   NVARCHAR (1000) NULL,
    [firmwareAddedDate]   DATETIME        NULL,
    [firmwareChangedDate] DATETIME        NULL,
    [isCurrent]           BIT             NULL
);

