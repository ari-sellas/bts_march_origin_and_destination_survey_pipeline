"""Compares data wrangling speeds between cuDF and pandas.

The data is sourced from the Bureau of Transportation Statistics'
Origin and Destination Survey. This is a 40% sample of airline tickets
collected from reporting carriers; it is currently collected monthly.
It includes quite a bit of information, but for our purposes,
we will keep things simple: find the top 10 ticket-issuing airlines,
and the median price of their tickets.
"""

# Uncomment the lines below to switch to using cuDF instead of base pandas.
# import cudf.pandas
# cudf.pandas.install()

import requests
import io
import zipfile
import time

import pandas as pd
import requests

# This is the link for March's reported ticket data. Note that the end of the link
# says "11JUN2026". I believe this is the date that the data was added to the BTS website,
# and is not indicative of when the data was reported.
od_url = "https://ostrapeispubdownloadprod.blob.core.windows.net/ostrapeis-pub-download-prod/ond40/products/db1c_public/DB1C.TICKET.202603.11JUN2026.zip"

# Sends a request to access the BTS data.
# The server responds by giving us data and metadata,
# which we convert to bytes, and then to a
# zip file-like object in memory.
response = requests.get(od_url)
response.raise_for_status()
zip_buffer = io.BytesIO(response.content)

# This opens the zip file that we made,
# and extracts the parquet file.
with zipfile.ZipFile(zip_buffer) as zf:
    parquet_file = [n for n in zf.namelist() if n.endswith(".parquet")]
    parquet_bytes = zf.read(parquet_file[0])

# We will use this to optimize memory usage.
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

# Median ticket price is used since ticket price is often right-skewed;
# thus, a mean calculation may be misrepresentative.
median_ticket_price_by_t10_carrier = (od_df
    .loc[od_df["issuing_carrier"].isin(tickets_issued_by_t10_carriers["issuing_carrier"])]
    .groupby("issuing_carrier")["total_amount"]
    .median()
    .round(2)
    .reset_index(name="median_ticket_price"))

tickets_by_t10_carrier = tickets_issued_by_t10_carriers.merge(median_ticket_price_by_t10_carrier,
    on="issuing_carrier",
    how="inner")

# Saves a parquet with all the data we will need to visualize.
# I will be using ggplot2 in R, as it is my preferred data visualization tool,
# but feel free to use whatever you are comfortable with.
tickets_by_t10_carrier.to_parquet("tickets_by_t10_carrier.parquet")

end_time = time.perf_counter()
execution_time = end_time - start_time
print(f"Process finished in {execution_time:.4f} seconds.")