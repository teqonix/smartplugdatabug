ALTER ROLE [db_ddladmin] ADD MEMBER [wemoSSIS];


GO
ALTER ROLE [db_datareader] ADD MEMBER [ouimeaux];


GO
ALTER ROLE [db_datareader] ADD MEMBER [wemoReporter];


GO
ALTER ROLE [db_datareader] ADD MEMBER [wemoSSIS];


GO
ALTER ROLE [db_datawriter] ADD MEMBER [ouimeaux];


GO
ALTER ROLE [db_datawriter] ADD MEMBER [wemoSSIS];


GO
ALTER ROLE [db_owner] ADD MEMBER [TEQNET\SSIS_SVC];


GO
ALTER ROLE [db_datawriter] ADD MEMBER [TEQNET\SSIS_SVC];


GO
ALTER ROLE [db_datareader] ADD MEMBER [TEQNET\SSIS_SVC];

