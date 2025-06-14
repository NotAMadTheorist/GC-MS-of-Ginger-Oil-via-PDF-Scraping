from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
path_GCMS_Peak_ResultsUnprocessed = ROOT_DIR / "Instrument Output Files" / "GCMS_Peak_ResultsUnprocessed.csv"
path_GCMS_Peak_Results = ROOT_DIR / "Program Output Files" / "Unsorted Files" / "GCMS_Peak_Results.csv"
path_GCMS_Peak_ResultsSorted = ROOT_DIR / "Program Output Files" / "Sorted Files" / "GCMS_Peak_ResultsSorted.csv"
path_GCMS_MSHitsPerPeakUnprocessed = ROOT_DIR / "Instrument Output Files" / "GCMS_MSHitsPerPeak_Unprocessed.csv"
path_GCMS_MSHitsPerPeak = ROOT_DIR / "Program Output Files" / "Unsorted Files" / "GCMS_MSHitsPerPeak.csv"
path_GCMS_MSHitsPerPeakSorted = ROOT_DIR / "Program Output Files" / "Sorted Files" / "GCMS_MSHitsPerPeakSorted.csv"