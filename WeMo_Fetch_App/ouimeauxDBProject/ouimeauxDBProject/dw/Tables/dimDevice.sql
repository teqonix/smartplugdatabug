CREATE TABLE [dw].[dimDevice] (
    [deviceIK]                    BIGINT          CONSTRAINT [DF_dimDevice_deviceIK] DEFAULT (NEXT VALUE FOR [dw].[dimDeviceIK]) NOT NULL,
    [deviceNaturalKey]            BIGINT          NOT NULL,
    [macAddress]                  NVARCHAR (12)   NULL,
    [serialNumber]                NVARCHAR (75)   NULL,
    [friendlyName]                NVARCHAR (255)  NULL,
    [deviceTypeLabel]             NVARCHAR (255)  NULL,
    [deviceIsSwitch]              BIT             NULL,
    [deviceIsThermostat]          BIT             NULL,
    [deviceCanMeasureEnergyUsage] BIT             NULL,
    [deviceIsLightBulb]           BIT             NULL,
    [firmwareName]                NVARCHAR (255)  NOT NULL,
    [firmwareVersion]             NVARCHAR (255)  NULL,
    [firmwareSignature]           NVARCHAR (1000) NULL,
    [ipAddress]                   NVARCHAR (255)  NULL,
    [subnetMask]                  NVARCHAR (255)  NULL,
    [tcpIPversion]                NVARCHAR (6)    NULL,
    [deviceFirstSeenDate]         DATETIME        NULL,
    [recordEffectiveDate]         DATETIME        CONSTRAINT [DF_dimDevice_recordEffectiveDate] DEFAULT (getdate()) NULL,
    [recordExpirationDate]        DATETIME        NULL,
    [isCurrent]                   BIT             NULL,
    CONSTRAINT [PK_dimDevice] PRIMARY KEY CLUSTERED ([deviceIK] ASC)
);



