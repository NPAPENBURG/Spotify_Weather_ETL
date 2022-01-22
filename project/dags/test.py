from datetime import datetime

string = 'test'
now = datetime.now().replace(microsecond=0)

print(now)