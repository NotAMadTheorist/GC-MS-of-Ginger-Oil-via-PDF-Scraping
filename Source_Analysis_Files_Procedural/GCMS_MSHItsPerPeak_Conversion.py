# This file creates a spreadsheet of all the possible molecule hits and their respective page numbers that were
# ... found to the MS spectra associated with each GCMS peak. It reads data primarily from the file
# .... GCMS_MSHitsPerPeak_Unprocessed.csv, which contains text copied from the printed output of the GCMS instrument.

# The above steps gives you a collection with items for each << Target >> or page.
# Create a reorganized collection with items for each assigned peak number.
# Translate this collection into a Pandas dataframe. Set the number of columns based on max# of compounds assigned to
# ... any single peak.
# Convert the Pandas dataframe into a csv file and save.

import re
import pandas as pd
from Source_GCMS_Analysis.rootDir import (path_GCMS_MSHitsPerPeakUnprocessed, path_GCMS_Peak_Results,
                                          path_GCMS_MSHitsPerPeakSorted, path_GCMS_MSHitsPerPeak)

# Variable for the first organized collection according to << Target >> Sections
dict_TargetSections = {"Target Number":[],
                       "Page Number":[],
                       "Peak Number":[],
                       "Retention Time (min)":[],
                       "Peak Area Percent (%)":[],
                       "MS Base Peak m/z":[],
                       "Molecule Hits from MS":[]}
targetNumber = 0
pageNumber = 3
maxNumberOfMatches = 1

# Read through the peak results file to get the retention times and peak numbers.
resultRetentionTimes = []
resultPeakNumbers = []
resultPeakAreaPercent = []
skipFirstLine = True
with open(path_GCMS_Peak_Results, 'r', encoding='UTF-8') as file:
    for resultsLine in file:
        if skipFirstLine:
            skipFirstLine = False
            continue
        resultsEntries = re.split(",", resultsLine)
        resultPeakNumbers.append(int(resultsEntries[0]))
        resultRetentionTimes.append(float(resultsEntries[1]))
        resultPeakAreaPercent.append(float(resultsEntries[5]))

# Read through the MS Hits per Peak file:
with open(path_GCMS_MSHitsPerPeakUnprocessed, 'r', encoding='UTF-8') as file:
    namesOfHits = []
    boolFirstTarget = True
    for GCMSLine in file:
        # If << Target >> is found, this indicates a new page. Update the page number.
        # Reset all the names of hit molecules for a new target; set new maximum number of matches
        if GCMSLine == "<< Target >>\n":
            if not boolFirstTarget:
                # Remove repeating entries from the names of hit molecules
                namesOfHitsNew = []
                [namesOfHitsNew.append(item) for item in namesOfHits if item not in namesOfHitsNew]
                namesOfHits = namesOfHitsNew.copy()
                if len(namesOfHits) > maxNumberOfMatches:
                    maxNumberOfMatches = len(namesOfHits)
                namesOfHits = [name.strip() for name in namesOfHits]
                dict_TargetSections["Molecule Hits from MS"].append(namesOfHits)
                namesOfHits = []
            boolFirstTarget = False

            targetNumber += 1
            pageNumber += 1
            dict_TargetSections["Target Number"].append(targetNumber)
            dict_TargetSections["Page Number"].append(pageNumber)

        # Read Line# and match the retention time (R.Time) value to the peak with the closest value in
        # ... GCMS_Peak_Results.csv. Then assign a peak number to which the molecule hits in the page are assigned to.
        elif GCMSLine[:5] == "Line#":
            retentionTime = float(re.split('Scan#:', re.split("R.Time:", GCMSLine)[1])[0][:-1])

            # Assign the peak number based on whatever result entry has the closest retention time
            retentionTimeDifferences = [abs(retentionTime - rtResults) for rtResults in resultRetentionTimes]
            RTDifference = min(retentionTimeDifferences)
            assignedPeakIndex = retentionTimeDifferences.index(min(retentionTimeDifferences))

            # Get assigned peak number, peak area percent, and retention time
            peakNumber = resultPeakNumbers[assignedPeakIndex]
            dict_TargetSections["Peak Number"].append(peakNumber)

            peakAreaPercent = resultPeakAreaPercent[assignedPeakIndex]
            dict_TargetSections["Peak Area Percent (%)"].append(peakAreaPercent)

            dict_TargetSections["Retention Time (min)"].append(retentionTime)

        # Read RawMode line and find the base peak value. Assign base peak to the peak number.
        elif GCMSLine[:8] == "RawMode:":
            basePeak = float(re.split("\\(", re.split("BasePeak", GCMSLine)[1][1:])[0])
            dict_TargetSections["MS Base Peak m/z"].append(basePeak)

        # Read all CompName lines and get the names of the hit compound involved. Use "$$" as a separator. Get the best
        # ... common name by eliminating any IUPAC name and selecting the first remaining non-IUPAC name. Remove any
        # ... repeating entries and add names in order of their similarity indexes.
        elif GCMSLine[:9] == "CompName:":
            # Regex expressions which identify IUPAC names
            regexPatternsIUPAC = [r'cyclo(\[.+\])',  # ex.  Tricyclo[4.4.0.0(2,7)]dec-3-ene
                                  r'\(.+\)',  # ex.  1,5-dimethyl-8-(1-methylethylidene)-, (E,E)-
                                  r'[1-9]-.+yl']  # ex. 2-methyl-1-butene
            # Special Expressions which are allowed in common names
            allowablePattern = r"\([123456789RS,]*\)"

            selectedName = ""
            possibleNames = re.split(" \\$\\$ ", GCMSLine[9:][:-1])
            possibleNames = [re.sub("\\$\\$", "", possibleName) for possibleName in possibleNames]

            commonNames = []
            for name in possibleNames:
                # Detect any IUPAC-name related fragment; do not add those into the list of common names
                boolDetectedIUPAC = False
                for patternIUPAC in regexPatternsIUPAC:
                    detectIUPAC = re.search(patternIUPAC, name)
                    if type(detectIUPAC) != type(None):
                        boolDetectedIUPAC = True
                        break
                if boolDetectedIUPAC:
                    exceptionIUPAC = re.search(allowablePattern, detectIUPAC.group())
                    if type(exceptionIUPAC) == type(None):
                        boolDetectedIUPAC = True
                if not boolDetectedIUPAC:
                    commonNames.append(name)
                boolDetectedIUPAC = False
            bestNames = [commonName for commonName in commonNames if not bool(re.search(r'\d', commonName))]

            # Select the best name for the compound depending on the results of the above filtering
            if len(commonNames) == 0:
                selectedName = possibleNames[0]
            elif len(bestNames) == 0:
                selectedName = commonNames[0]
            else:
                selectedName = bestNames[0]
            namesOfHits.append(selectedName)

    # Code to add the molecule hits for the last target
    namesOfHitsNew = []
    [namesOfHitsNew.append(item) for item in namesOfHits if item not in namesOfHitsNew]
    namesOfHits = namesOfHitsNew.copy()
    if len(namesOfHits) > maxNumberOfMatches:
        maxNumberOfMatches = len(namesOfHits)
    dict_TargetSections["Molecule Hits from MS"].append(namesOfHits)
    namesOfHits = []

# Remove any target from the first collection whose retention times do not correspond to the peak results within
# ... a certain range (~ 0.002 min discrepancy)
indicesToRemove = []

numberOfTargets = len(dict_TargetSections["Target Number"])
for targetIndex in range(numberOfTargets):
    retentionTime = dict_TargetSections["Retention Time (min)"][targetIndex]
    peakNumber = dict_TargetSections["Peak Number"][targetIndex]
    resultRetentionTime = resultRetentionTimes[resultPeakNumbers.index(peakNumber)]
    if abs(retentionTime - resultRetentionTime) > 0.022:
        indicesToRemove.append(targetIndex)
for keyName in dict_TargetSections.keys():
    for indexToRemove in indicesToRemove:
        dict_TargetSections[keyName][indexToRemove] = None
    dict_TargetSections[keyName] = [item for item in dict_TargetSections[keyName] if type(item) != type(None)]


# Variable for the second organized collection arranged according to Peak Number
dict_PeakNumberNames = {"Peak Number":[],
                        "Page Numbers":[],
                       "Retention Time (min)":[],
                       "Peak Area Percent (%)":[],
                       "MS Base Peak m/z":[],
                       "Molecule Hits from MS":[]}

# Loop through the first organized collection to get data according to each assigned peak. Take all targets corresponding
# ... to the same peak. Compile their page numbers and names of hit molecules.
# Observations: Multiple targets corresponding to the same peak have different names but the same base peaks in MS.
numberOfTargets = len(dict_TargetSections["Target Number"])
numberOfPeaks = len(resultPeakNumbers)
for indexPeak in range(numberOfPeaks):
    peakNumber = resultPeakNumbers[indexPeak]
    dict_PeakNumberNames["Peak Number"].append(peakNumber)
    dict_PeakNumberNames["Retention Time (min)"].append(resultRetentionTimes[indexPeak])
    dict_PeakNumberNames["Peak Area Percent (%)"].append(resultPeakAreaPercent[indexPeak])

    listBasePeaks = []
    listPageNumbers = []
    listMoleculeHits = []
    for indexTarget in range(numberOfTargets):
        if dict_TargetSections["Peak Number"][indexTarget] == peakNumber:
            listBasePeaks.append(dict_TargetSections["MS Base Peak m/z"][indexTarget])
            listPageNumbers.append(dict_TargetSections["Page Number"][indexTarget])
            listMoleculeHits = listMoleculeHits + dict_TargetSections["Molecule Hits from MS"][indexTarget]

    # Remove repeating entries from the list of molecule hits
    listMoleculeHits_new = []
    [listMoleculeHits_new.append(item) for item in listMoleculeHits if item not in listMoleculeHits_new]
    listMoleculeHits = listMoleculeHits_new.copy()

    # Convert page numbers into strings; get the base peak of MS (same for each match of GC peak)
    strPageNumbers = ", ".join([str(pageNumber) for pageNumber in listPageNumbers])
    basePeak = listBasePeaks[0]

    # Update maximum number of matches per peak; important for setting up columns for the dataframe
    if len(listMoleculeHits) > maxNumberOfMatches:
        maxNumberOfMatches = len(listMoleculeHits)

    # Append relevant information to the second collection
    dict_PeakNumberNames["Page Numbers"].append(strPageNumbers)
    dict_PeakNumberNames["MS Base Peak m/z"].append(basePeak)
    dict_PeakNumberNames["Molecule Hits from MS"].append(listMoleculeHits)

# Modify the second organized collection by separating molecule hits into "maxNumberOfMatches" columns.
for indexMoleculeHit in range(maxNumberOfMatches):
    columnName = f"MS Molecule Hit #{indexMoleculeHit+1}"
    columnList = []
    for indexPeak in range(numberOfPeaks):
        listMoleculeHits = dict_PeakNumberNames["Molecule Hits from MS"][indexPeak]
        if indexMoleculeHit < len(listMoleculeHits):
            columnList.append(listMoleculeHits[indexMoleculeHit])
        else:
            columnList.append("")
    dict_PeakNumberNames[columnName] = columnList
del dict_PeakNumberNames["Molecule Hits from MS"]

 # Print the output of the second collection
for key, value in dict_PeakNumberNames.items():
    print(key, value)
    print(len(value))

# Convert the second organized collection into a Pandas DataFrame and save as a CSV file.
DF_PeakNumberNames = pd.DataFrame(dict_PeakNumberNames)
DF_PeakNumberNames.to_csv(path_GCMS_MSHitsPerPeak,index=False)

# Sort the DataFrame according to peak% area and save as another CSV file.
DF_PeakNumberNamesSorted = DF_PeakNumberNames.sort_values(by='Peak Area Percent (%)', ascending=False)
DF_PeakNumberNamesSorted.to_csv(path_GCMS_MSHitsPerPeakSorted, index=False)



# ... more code here ...

# Create another dataframe sorted according to peak area %; then save to a CSV file ...

# ... more code here ...




