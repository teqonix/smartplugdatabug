/****** Script for SelectTopNRows command from SSMS  ******/
SELECT TOP (1000) [iDateTime]
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
  FROM [Sandbox].[dw].[dimDatetimeHour]