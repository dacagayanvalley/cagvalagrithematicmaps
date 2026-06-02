# Power BI PAGASA Extraction

Source resource key: 92d7e825-aa57-4708-a137-00bb4666beec
Tenant ID: bd03a735-2aa3-4cca-9722-2ae4929ab3ec
Report/model: PAGASA EASi Tool public Power BI report
FetchedAtUtc: 2026-06-02T04:36:29+00:00
Stations: Aparri, Tuguegarao, Casiguran, Calayan, Basco, Itbayat
Period: 1991-2020

Extracted 1935 station-month rows and 976 station-season rows.

App-ready outputs:

- `data/pagasa_station_monthly_1991_2020.csv`
- `data/pagasa_station_seasonal_1991_2020.csv`
- `data/pagasa_powerbi_climate_extract.csv`

Refresh command:

```powershell
python scripts\fetch_pagasa_powerbi.py
```
