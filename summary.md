Some summary observations from the conda database and their SQL queries:

- Conda has 20,030 packages in total in the `anaconda` and `conda-forge` channels (`SELECT COUNT(*) FROM conda_packages;"`)
  - `conda_listings.json` had 20,094 packages so 64 are unaccounted for (~0.3%)
- Conda has 8,162 Python packages (`SELECT COUNT(*) FROM conda_packages WHERE packagename LIKE 'r-%';"`)
- Conda has 7,813 R packages (`SELECT COUNT(*) FROM conda_packages WHERE packagename LIKE 'r-%';"`)
