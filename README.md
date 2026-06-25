# BTS Origin and Destination Survey Analysis
*An end-to-end pipeline processing 13M BTS airline ticket records*

## Dataset
The data used in this project can be found [here](https://www.bts.gov/topics/airlines-and-airports/origin-and-destination-survey-data-ticket),
specifically, the March 2026 upload. If you choose to run this program
on your own, then you do not have to download it manually; all the data
acquisition will be handled for you.

## Focus
The main focus of this project was benchmarking GPU-accelerated (cuDF) vs. CPU (pandas) data wrangling
with a real-world dataset. I have seen the significant performance improvements that stem
from GPU acceleration firsthand (e.g., in NVIDIA DLI courses), but wanted to try it out on a relatively
simple question that I've had in mind recently: which airlines have the highest median ticket price? For my purposes,
I used the most recently-provided data, and sorted the data based on the top 10 ticket-issuing carriers, since they
dominate the market. Of course, ticket prices vary by season, so it's possible that these ticket prices
might not be similar to annual medians.

## Project Structure
```text
bts_march_origin_and_destination_survey_pipeline/
├── .gitignore  
├── README.md                                    
├── bts_origin_destination_pipeline.Rproj            # RStudio project file
├── data_processing/                                 # All necessary data processing
│   ├── bts_od_wrangling.py                          # Benchmarking and wrangling
│   └── tickets_by_t10_carrier.parquet               # Data ready for visualization
└── data_visualization/                              # Creates and stores graph
    ├── data_vis.R                                   # Creates graph
    └── median-ticket-prices-by-top-10-carriers.png  # Ticket prices vs. carrier
```

## Usage
For the Python portion of the project, I used Google Colab; my Mac does not natively support cuDF,
and Google Colab was a free alternative. For replicability's sake, I suggest you copy-paste the code into
a new notebook there and run it (make sure you use the T4 GPU). Make sure you download the parquet file produced if you'd
like to visualize data later on.

For the R portion of the project, simply clone the repo, make sure you have tidyverse and arrow installed (use `install.packages(c("tidyverse", "arrow"))`),
and run the data_vis.R file. The scatter plot will be made automatically.

## Results
In this particular instance, cuDF actually underperformed relative to pandas. cuDF took 2.8823 seconds to complete 
all the data transformations, which is roughly 9% longer than pandas' 2.6404 seconds to accomplish the
same task. While this might seem surprising given the significant performance boosts often associated with GPU acceleration,
there are a few reasons why this result actually makes sense:
* While there were 13M rows total, which is well beyond the typical 10k-100k row range where performance improvements 
  become very noticeable (according to RAPIDS), only two columns with downcasted values were selected from the get-go.
  This is a small total byte payload.
* The operations used (groupby/size, groupby/median, a small merge) are pretty computationally cheap to begin with.
  Given that pandas handles these well already, it's quite likely that the
  computational overhead from host-to-device transfers (that is, transferring memory from CPU to GPU)
  made up a larger share of the processing time than actual computations did.
* Adding onto computational overhead is the way that cuDF.pandas works. When using `import cudf.pandas` and `cudf.pandas.install()`,
  importing pandas does *not* import the standard CPU-using version of pandas.
  Instead, a slightly different module is imported, which includes proxy functions and proxy types. Operations
  on either of these will execute on the GPU primarily; the CPU is merely a fallback. This overall process
  uses slightly more computational resources, which is a very strong trade-off for massive datasets, but might
  hinder performance for smaller ones, as seen here.

As for the problem I set out to solve, here are the median ticket prices for the top 10 carriers. It's pretty interesting
to see how major carriers cluster at the high-price and high-volume end, while budgets cluster low on both:
![Median ticket prices by top 10 ticket-issuing carriers](/data_visualization/median-ticket-prices-by-top-10-carriers.png)