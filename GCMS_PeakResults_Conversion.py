
# This program converts the formatting in "GCMS_Peak_ResultsUnprocessed.csv" by correcting the positions of delimiting commas.
# Step 1. Surround all existing commas (,) with single quotation marks (',')
# Step 2. Replace the first ten spaces of each line with commas (,) without quotation marks

import os
import pandas as pd
import re

# Assign variables to the paths of CSV files to use
path_Source = os.path.dirname(__file__)
path_GCMSPeakResults = os.path.join(path_Source, "GCMS_Peak_ResultsUnprocessed.csv")

# Read through the peak results file
with open(path_GCMSPeakResults, 'r', encoding='UTF-8') as file:
    lines_GCMSPeakResults = file.readlines()

# Perform operations on each read line
newColumns = ["Peak Number", "Retention Time (s)", "Start of Peak (s)", "End of Peak (s)", "Peak Area (A.U.)",
              "Peak Area Percent (%)", "Peak Height (H.U.)", "Peak Height Percent (%)",
              "Area-to-Height Ratio", "Mark", "Currently Assigned Compound", "\n"]
newLine_columns = ','.join(newColumns)
newLines_GCMSPeakResults = [newLine_columns]
for line in lines_GCMSPeakResults[1:]:
    tempLine = line[1:]
    tempLineList = [x for x in tempLine.split(" ") if len(x) != 0]
    tempLine = ','.join(tempLineList[:10])
    if len(tempLineList) > 11:
        tempNameEntry = '"=""' + ' '.join((tempLineList[10:])[:-1]) + '"""' + '\n'
    else:
        tempNameEntry = '"=""' + ' '.join((tempLineList[10])[:-1]) + '"""' + '\n'
    tempLine = tempLine + "," + tempNameEntry

    print(tempLine)
    newLines_GCMSPeakResults.append(tempLine)
newLines_GCMSPeakResults.pop()
print("\n ------------------ \n")

# Create a new CSV file with processed, comma-delimited lines
with open("GCMS_Peak_Results.csv", 'w', encoding='UTF-8') as file:
    file.writelines(newLines_GCMSPeakResults)

# Create another CSV file, this time, the rows are sorted according to area percent (%)
numberOfPeaks = len(newLines_GCMSPeakResults[1:])
listIndexRows = []
listPeakAreaPercent = []

for indexPeak in range(numberOfPeaks):
    resultsEntries = re.split(",", newLines_GCMSPeakResults[indexPeak+1])
    listIndexRows.append(indexPeak+1)
    listPeakAreaPercent.append(float(resultsEntries[5]))
DF_SortRows = pd.DataFrame({"Row Index": listIndexRows, "Peak Area Percent (%)": listPeakAreaPercent})
DF_SortRows = DF_SortRows.sort_values(by="Peak Area Percent (%)", ascending=False)

newSortedLines_GCMSPeakResults = [newLine_columns]
for indexRow in list(DF_SortRows.loc[:,"Row Index"]):
    print(newLines_GCMSPeakResults[indexRow])
    newSortedLines_GCMSPeakResults.append(newLines_GCMSPeakResults[indexRow])

# Create a new CSV file with processed, comma-delimited lines
with open("GCMS_Peak_ResultsSorted.csv", 'w', encoding='UTF-8') as file:
    file.writelines(newSortedLines_GCMSPeakResults)