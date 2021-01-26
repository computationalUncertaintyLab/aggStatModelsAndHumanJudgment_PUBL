#mcandrew;

PYTHON:=python3 -W ignore

run: pullDataFromServer computeQuantiles
.PHONY: run

pullDataFromServer:
	$(PYTHON) importrawdata.py && \
	echo "Pulled data from server"

computeQuantiles:
	$(PYTHON) predictionsStatsTable.py && \
	echo "Quantiles for predicitve densities computed"

PickleReportData:
	$(PYTHON) programmaticReportData.py && \
	echo "Report data pickled"
