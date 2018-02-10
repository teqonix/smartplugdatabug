CREATE VIEW dw.dimLocationCurrent AS (
SELECT LocationIK, locationNaturalKey, locationName, locationFloor, locationRoom, locationFirstSeenDate, recordEffectiveDate, recordExpirationDate, isCurrent
FROM dw.dimLocation dl
WHERE dl.recordExpirationDate IS NULL 
)
;