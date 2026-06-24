import requests
import io
import zipfile
import pandas as pd

od_url = "https://ostrapeispubdownloadprod.blob.core.windows.net/ostrapeis-pub-download-prod/ond40/products/db1c_public/DB1C.TICKET.202603.11JUN2026.zip"

response = requests.get(od_url)
response.raise_for_status()
zip_buffer = io.BytesIO(response.content)

with zipfile.ZipFile(zip_buffer) as zf:
    parquet_file = [n for n in zf.namelist() if n.endswith(".parquet")]
    parquet_bytes = zf.read(parquet_file[0])

df = pd.read_parquet(io.BytesIO(parquet_bytes))
print(df.head())