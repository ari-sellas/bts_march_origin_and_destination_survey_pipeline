# Visualizes the data produced by bts_od_wrangling.py.

library(tidyverse)
library(arrow)
library(scales)


tickets_by_t10_carrier_df <- read_parquet(
  "data_processing/tickets_by_t10_carrier.parquet"
  )


ggplot(tickets_by_t10_carrier_df, aes(
  x = fct_reorder(issuing_carrier, median_ticket_price),
  y = median_ticket_price
  )) +
  geom_point(aes(color = tickets_issued), size = 5) + 
  scale_color_viridis_c(labels = label_comma()) +
  scale_x_discrete(labels = c(
    "Frontier", 
    "Allegiant", 
    "Breeze", 
    "JetBlue", 
    "Sun Country", 
    "Southwest", 
    "Alaska", 
    "United", 
    "American", 
    "Delta"
    )) +
  scale_y_continuous(
    breaks = breaks_pretty(n = 10), 
    expand = expansion(mult = c(0.05, 0.04))) +
  labs(
    title = "Median ticket prices for top 10 ticket-issuing carriers",
    x = "Issuing Carrier", y = "Median Ticket Price",
    color = "Tickets Issued"
  ) +
  theme(
    text = element_text(family = "Helvetica"),
    plot.title = element_text(face = "bold"),
    axis.title.x = element_text(margin = margin(t = 10)),
    axis.title.y = element_text(margin = margin(r = 10)),
    axis.text.x = element_text(size = 7),
    panel.background = element_rect(fill = "white", color = "black", size = 0.5),
    panel.grid.major = element_line(color = "black",linewidth = 0.1)
    )
ggsave(file.path(
  "data_visualization", "median-ticket-prices-by-top-10-carriers.pdf"
  ))