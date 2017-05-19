CREATE VIEW dw.dimStatusListCurrent AS (
SELECT statusIK, statusNaturalKey, statusLabel, statusNumberRepresentation, statusAddedDate, recordEffectiveDate, recordExpirationDate, isCurrent
FROM dw.dimStatusList dsl
WHERE recordExpirationDate IS NULL
)
;