CREATE TABLE [acq].[locations] (
    [locationSK]        BIGINT         CONSTRAINT [DF_locations_locationSK_1] DEFAULT (NEXT VALUE FOR [dbo].[locationSK]) NOT NULL,
    [locationName]      NVARCHAR (255) NOT NULL,
    [locationFloor]     NVARCHAR (255) NOT NULL,
    [locationRoom]      NVARCHAR (255) NOT NULL,
    [locationAddedDate] DATETIME       CONSTRAINT [DF_locations_locationAddedDate_1] DEFAULT (getdate()) NOT NULL
);



