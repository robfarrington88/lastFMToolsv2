import pandas as pd
import os
import datetime
import LastLib as ll

for i in range(2010,2026):
     ll.updateYearCSV(i)
ll.joinAnnualReports()
ll.updateFilesandRefreshReports()
#df=ll.loadDatabase(ll.getFileToUpdate())
#ll.getTracksInAlbums(df)

