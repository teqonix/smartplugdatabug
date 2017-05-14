CREATE TABLE [dbo].[locations] (
    [locationSK]        BIGINT         CONSTRAINT [DF_locations_locationSK] DEFAULT (NEXT VALUE FOR [dbo].[locationSK]) NOT NULL,
    [locationName]      NVARCHAR (255) NOT NULL,
    [locationFloor]     NVARCHAR (255) NOT NULL,
    [locationRoom]      NVARCHAR (255) NOT NULL,
    [locationAddedDate] DATETIME       CONSTRAINT [DF_locations_locationAddedDate] DEFAULT (getdate()) NOT NULL,
    CONSTRAINT [PK_locations] PRIMARY KEY CLUSTERED ([locationSK] ASC)
);

