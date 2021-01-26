#mcandrew;
PYTHON:=python3 -W ignore

buildreport01:
	cd ../ && mkdir -p summaryreports && cd summaryreports && mkdir -p summaryReport01 && cd ../automateReport && \
	$(PYTHON) autoReport.py && cd ../summaryreports/summaryReport01 && latexmk -pvc -pdf autorReport01.tex && cd ../../automateReport && \
	echo "Report01 built"
