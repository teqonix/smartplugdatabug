CREATE TABLE [dw].[dimDateQuarterHour] (
    [dateTimeIK]    BIGINT       NOT NULL,
    [dateTimeHour]  BIGINT       NOT NULL,
    [DateTime]      DATETIME     NULL,
    [DateString]    VARCHAR (10) NULL,
    [HourOfDay]     INT          NULL,
    [MinuteOfHour]  INT          NOT NULL,
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
    CONSTRAINT [PK_dimDateQuarterHour] PRIMARY KEY CLUSTERED ([dateTimeIK] ASC)
);

