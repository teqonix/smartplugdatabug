﻿
/****** Script for SelectTopNRows command from SSMS  ******/
CREATE VIEW [dw].[DimDateHourOnly] WITH SCHEMABINDING AS (
SELECT MAX([dateTimeIK]) AS dateTimeIK
      ,[dateTimeHour]
      ,[DateTime]
      ,[DateString]
      ,[HourOfDay]
      ,[Date]
      ,[Day]
      ,[DayofYear]
      ,[DayofWeek]
      ,[DayofWeekName]
      ,[Week]
      ,[Month]
      ,[MonthName]
      ,[Quarter]
      ,[Year]
      ,[IsWeekend]
      ,[IsLeapYear]
  FROM [dw].[dimDateQuarterHour]
  GROUP BY [dateTimeHour]
      ,[DateTime]
      ,[DateString]
      ,[HourOfDay]
      ,[Date]
      ,[Day]
      ,[DayofYear]
      ,[DayofWeek]
      ,[DayofWeekName]
      ,[Week]
      ,[Month]
      ,[MonthName]
      ,[Quarter]
      ,[Year]
      ,[IsWeekend]
      ,[IsLeapYear]
)