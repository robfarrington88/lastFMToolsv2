import pandas as pd
yearList=list(range(2010,2024))
for year in yearList:
    infilename=f"AllScrobbles_{year}.csv"
    dateparse = '%Y-%m-%d %H:%M:%S'

    df = pd.read_csv(infilename, date_format=dateparse)
    df['Scrobble Time']=pd.to_datetime(df['Scrobble Time'])
    if year==2010:
        fulldf=df
    else:
        fulldf=pd.concat([fulldf, df])

fulldf=fulldf.sort_values(by="Scrobble Time")   
fulldf.reset_index(drop=True,inplace=True)
fulldf['Year']=fulldf['Scrobble Time'].apply(lambda x: x.year )
lastscrobble=fulldf.at[len(fulldf)-1,'Scrobble Time'].to_pydatetime().strftime("%Y%m%d_%H%M%S")
fulldf.set_index('Scrobble Time',inplace=True)
fulldf.to_csv("AllScrobblesTo_"+lastscrobble+".csv")