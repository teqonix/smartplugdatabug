CREATE PROCEDURE acq.truncateAcq
AS
BEGIN

	TRUNCATE TABLE acq.deviceTypes;
	TRUNCATE TABLE acq.locations;
	TRUNCATE TABLE acq.networkMetadata;
	TRUNCATE TABLE acq.powerScales;
	TRUNCATE TABLE acq.deviceTypes;
	TRUNCATE TABLE acq.statusList;
	TRUNCATE TABLE acq.deviceFirmware;
	TRUNCATE TABLE acq.IoTDevice;
	TRUNCATE TABLE acq.deviceUsageData;

END
