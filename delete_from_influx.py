from uuid import UUID

s = """
66b849cc-b9af-4573-98ce-448332065d6e
44545488-50d1-4310-8178-d51280979c1d
6313d2dc-306d-41f2-99e1-d6263e1f276c
794e7a72-0158-4875-ac55-a6d497a0ec33
ac745017-84d9-4600-b686-7955ca30deeb
8c18522c-4c3e-4a4d-9a59-27b0a9f30d4c
d4bcb1fe-cbfe-4c60-8c65-d5d8b9291e56
775d6100-f5eb-42fd-b015-616869066a6c
8b75649a-1f15-4623-a2b7-9f0dfe850bfc
83b027bb-c5dc-4c19-80da-2d004619676a
"""

l = s.split()
for u in l:
    print(UUID(u))

chunk_size = 500
num_chunks = int(len(l) / 500)+1


strings = []
# 20.07.22 00:00:00 bis 21.07.22 23:59:00
import requests
from datetime import datetime
import pytz
localtime = pytz.timezone("Europe/Berlin")

start = localtime.localize(datetime(2023,1,3,0,0,0,0,))
end = localtime.localize(datetime(2023,1,6,0,0,0,0,))

start_ts = int(start.timestamp() * 1_000_000_000)
end_ts = int(end.timestamp()  * 1_000_000_000)


for i in range(num_chunks):
    chunk = l[i*chunk_size:(i+1)*chunk_size]
    chunk_string = " OR ".join([f"uuid='{u}'" for u in chunk])
    s = requests.session()
    token = ""
    s.headers = {
        "Authorization": f"Token nidi:{token}"
    }

    query = f"SELECT * from power WHERE time<{end_ts} AND time>={start_ts} AND ({chunk_string})"

    print(query)
    response = s.post("http://influxdb1:8086/query", params={
        "db": "nx_portfolio",
        "q": query,
    })

    print(response.text[:150])
    values = response.json()["results"][0]["series"][0]["values"]
    uuids_found = set()
    for ts, uuid, value in values:
        uuids_found.add(uuid)
    print(len(uuids_found), len(l))
    print(len(values))
    print(values[0], values[-1])


#n = ','.join([f"'{u}'" for u in l])

#print(r)
