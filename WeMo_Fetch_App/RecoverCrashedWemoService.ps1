#This didn't work because powershell's default starting path is System32
#$currentPath = (Get-Item -Path ".\" -Verbose).FullName
#$configFile = $currentPath.ToString() + "\" + "config.cfg"

$configFile = "C:\Users\LOCAL_ADMIN\Documents\Visual Studio 2017\Projects\WeMo_Fetch_App\WeMo_Fetch_App\config.cfg"

$configProperties = ConvertFrom-StringData (Get-Content $configFile -raw)

$wemoServiceID = (get-wmiobject win32_service | where { $_.name -eq $configProperties.serviceName}).processID

$SSISErrorCountQuery = "
SELECT 
	COUNT(0) AS ERR_COUNT
FROM [SSISDB].[catalog].[executions]
WHERE 1=1
	AND start_time >= DATEADD(hour,-2,SYSDATETIMEOFFSET())
	AND package_name = '" + $configProperties.ssisPackageName + "'
	AND status = 4
;
"
$errCount = Invoke-Sqlcmd -Password $configProperties.password -Username ouimeaux -Query $SSISErrorCountQuery -ServerInstance $configProperties.serverIP

If($errCount.ERR_COUNT -eq 0){
    echo "No errors found!"
    echo "We would have killed this PID: $wemoServiceID"
    #debug event log writes:
    $eventLogMessage = "Config file path: " + $configFile + ". No problems here.  The wemo app has not had any SSIS failures in the past 2 hours. The SQL query used to check this was: " + $SSISErrorCountQuery
    Write-EventLog -LogName Application -Source "Powershell Wemo Recovery Script" -EntryType Information -EventId 255 -Message $eventLogMessage
}
ElseIf($errCount.ERR_COUNT -ne 0){
    $errorMessage = "THE PYTHON WEMO APP STOPPED RESPONDING...  Config file path: " + $configFile + ". PID " + $wemoServiceID + " was killed because it was attached to service " + $configProperties.serviceName + ".  This was the query used to detect SSIS errors: " + $SSISErrorCountQuery + ". This many errors were returned: " + $errCount.ERR_COUNT
    
    Write-EventLog -LogName Application -Source "Powershell Wemo Recovery Script" -EntryType Error -EventId 255 -Message $errorMessage
    
    "Killing PID $wemoServiceID"

    Stop-Process -id $wemoServiceID -Force
}