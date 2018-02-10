CREATE TABLE [dbo].[networkMetadata] (
    [networkMetadataSK] BIGINT         CONSTRAINT [DF_networkMetadata_networkMetadataSK] DEFAULT (NEXT VALUE FOR [networkMetadataSK]) NOT NULL,
    [ipAddress]         NVARCHAR (255) NULL,
    [subnetMask]        NVARCHAR (255) CONSTRAINT [DF_networkMetadata_subnetMask] DEFAULT (N'255.255.255.0') NULL,
    [tcpIPversion]      NVARCHAR (6)   NULL,
    [recordAddedDate]   DATETIME       CONSTRAINT [DF_networkMetadata_recordAddedDate] DEFAULT (getdate()) NOT NULL,
    [recordChangedDate] DATETIME       NULL,
    CONSTRAINT [PK_networkMetadata] PRIMARY KEY CLUSTERED ([networkMetadataSK] ASC)
);

