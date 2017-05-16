CREATE FUNCTION [dw].[IntKeyForYYMMDDHH] 
(
 -- Add the parameters for the function here
 @dateTime dateTime
)
RETURNS int
AS
BEGIN
 -- Declare the return variable here
 DECLARE @sYYYYMMDD nchar(8)
 declare @iHour int
 declare @sHour nchar(2)
 declare @sYYYYMMDDHH nchar(10)
 declare @iReturn int -- Add the T-SQL statements to compute the return value here

 select @sYYYYMMDD = convert(nchar,@dateTime,112)
 select @iHour = datepart(hour, @dateTime)
 if (@iHour < 10)
 Begin
 select @sHour = '0' + convert(nchar,@iHour)
 End
 else
 Begin
 select @sHour = convert(nchar,@iHour)
 End
 select @sYYYYMMDDHH = @sYYYYMMDD + @sHour 
 select @iReturn = convert(int,@sYYYYMMDDHH) -- Return the result of the function
 RETURN @iReturn 
END
GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = N'This function is used to generate the integer key used to join fact tables to the dateTime dimension with hourly granularity.', @level0type = N'SCHEMA', @level0name = N'dw', @level1type = N'FUNCTION', @level1name = N'IntKeyForYYMMDDHH';

