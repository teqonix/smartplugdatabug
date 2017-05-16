CREATE TABLE [dw].[dimDateHour] (
    [dateTimeIK]    BIGINT       NOT NULL,
    [DateTime]      DATETIME     NULL,
    [DateString]    VARCHAR (10) NULL,
    [HourOfDay]     INT          NULL,
    [Date]          DATE         NULL,
    [Day]           INT          NULL,
    [DayofYear]     INT          NULL,
    [DayofWeek]     INT          NULL,
    [DayofWeekName] VARCHAR (10) NULL,
    [Week]          INT          NULL,
    [Month]         INT          NULL,
    [MonthName]     VARCHAR (10) NULL,
    [Quarter]       INT          NULL,
    [Year]          INT          NULL,
    [IsWeekend]     BIT          NULL,
    [IsLeapYear]    BIT          NULL,
    CONSTRAINT [PK_dimDateHour] PRIMARY KEY CLUSTERED ([dateTimeIK] ASC)
);

