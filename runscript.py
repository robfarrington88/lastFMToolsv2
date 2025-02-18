import LastLib2 as ll
import time

print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
ll.createDatabase()
for i in range(2010,2026):
    ll.getAnnualScrobblesToDB(i)
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))