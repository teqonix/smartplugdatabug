CREATE VIEW dw.dimPowerScalesCurrent AS (
SELECT powerScaleIK, unitOfPower, scaleAddedDate, recordEffectiveDate, recordExpirationDate, isCurrent, powerScaleNaturalKey
FROM dw.dimPowerScales dps
WHERE dps.recordExpirationDate IS NULL
);