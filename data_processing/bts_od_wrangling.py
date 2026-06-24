# import cudf.pandas
# cudf.pandas.install()

import requests
import io
import zipfile
import pandas as pd
import time

od_url = "https://ostrapeispubdownloadprod.blob.core.windows.net/ostrapeis-pub-download-prod/ond40/products/db1c_public/DB1C.TICKET.202603.11JUN2026.zip"

response = requests.get(od_url)
response.raise_for_status()
zip_buffer = io.BytesIO(response.content)


with zipfile.ZipFile(zip_buffer) as zf:
    parquet_file = [n for n in zf.namelist() if n.endswith(".parquet")]
    parquet_bytes = zf.read(parquet_file[0])

dtype_dict = {
    "issuing_carrier": "category",
    "total_amount": "float32"
}

start_time = time.perf_counter()

od_df = (pd.read_parquet(io.BytesIO(parquet_bytes), columns=["IssuingCarrier", "TotalAmount"])
    .rename(columns={"IssuingCarrier": "issuing_carrier", "TotalAmount": "total_amount"}))

od_df = od_df.astype(dtype_dict)

tickets_issued_by_t10_carriers = (od_df.groupby("issuing_carrier")
    .size()
    .astype("int32")
    .reset_index(name="tickets_issued")
    .sort_values(by="tickets_issued", ascending=False)
    .head(10))

median_ticket_price_by_t10_carrier = (od_df
    .loc[od_df["issuing_carrier"].isin(tickets_issued_by_t10_carriers["issuing_carrier"])]
    .groupby("issuing_carrier")["total_amount"]
    .median()
    .round(2)
    .reset_index(name="median_ticket_price"))

tickets_by_t10_carrier = tickets_issued_by_t10_carriers.merge(median_ticket_price_by_t10_carrier,
    on="issuing_carrier",
    how="inner")


tickets_by_t10_carrier.to_parquet("tickets_by_t10_carrier.parquet")

end_time = time.perf_counter()
execution_time = end_time - start_time
print(f"Process finished in {execution_time:.4f} seconds.")