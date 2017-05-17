CREATE TABLE [acq].[locations] (
    [locationSK]        BIGINT         NOT NULL,
    [locationName]      NVARCHAR (255) NOT NULL,
    [locationFloor]     NVARCHAR (255) NOT NULL,
    [locationRoom]      NVARCHAR (255) NOT NULL,
    [locationAddedDate] DATETIME       NOT NULL
);

