CREATE TABLE [acq].[networkMetadata] (
    [networkMetadataSK] BIGINT         NOT NULL,
    [ipAddress]         NVARCHAR (255) NULL,
    [subnetMask]        NVARCHAR (255) NULL,
    [tcpIPversion]      NVARCHAR (6)   NULL,
    [recordAddedDate]   DATETIME       NOT NULL,
    [recordChangedDate] DATETIME       NULL
);

