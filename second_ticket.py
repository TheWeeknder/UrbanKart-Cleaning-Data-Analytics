import pandas as pd

# 1. Load the cleaned dataset
file_path = r"C:\JP\Developer\PERSONAL\Data-Analytics-Job-Simulation\urbankart_cleaning\urbankart_sales_clean.csv"

df = pd.read_csv(file_path)

# 2. Prepare the columns
df["order_date"] = pd.to_datetime(df["order_date"])
df["total_revenue"] = pd.to_numeric(df["total_revenue"], errors="coerce")

# 3. Keep January through June 2026
period = df[
    (df["order_date"] >= "2026-01-01") &
    (df["order_date"] < "2026-07-01")
].copy()

# 4. Q1: Total revenue by region
region_revenue = (
    period.groupby("region")["total_revenue"]
    .sum()
    .sort_values(ascending=False)
)

print("\nQ1 - Revenue by region")
print(region_revenue)

# 5. Q2: Monthly revenue
period["month"] = period["order_date"].dt.to_period("M")

monthly_revenue = (
    period.groupby("month")["total_revenue"]
    .sum()
    .sort_index()
)

april = monthly_revenue[pd.Period("2026-04")]
may = monthly_revenue[pd.Period("2026-05")]
june = monthly_revenue[pd.Period("2026-06")]

april_to_may = (may - april) / april * 100
may_to_june = (june - may) / may * 100

if april_to_may > 0 and may_to_june > 0:
    direction = "Growing"
elif april_to_may < 0 and may_to_june < 0:
    direction = "Declining"
else:
    direction = "Mixed"

print("\nQ2 - Monthly revenue")
print(monthly_revenue)
print(f"April to May: {april_to_may:+.1f}%")
print(f"May to June: {may_to_june:+.1f}%")
print(f"Direction: {direction}")

# 6. Q3: Total revenue by sales channel
channel_revenue = (
    period.groupby("sales_channel")["total_revenue"]
    .sum()
    .sort_values()
)

total_revenue = period["total_revenue"].sum()
weakest_channel = channel_revenue.index[0]
weakest_revenue = channel_revenue.iloc[0]
weakest_share = weakest_revenue / total_revenue * 100

print("\nQ3 - Revenue by channel")
print(channel_revenue)
print(f"Weakest channel: {weakest_channel}")
print(f"Weakest channel revenue: {weakest_revenue}")
print(f"Weakest channel share: {weakest_share:.1f}%")

# 7. Supporting metrics for the recommendation
channel_monthly = (
    period.groupby(["month", "sales_channel"])["total_revenue"]
    .sum()
    .unstack(fill_value=0)
)

channel_aov = (
    period.groupby("sales_channel")["total_revenue"]
    .mean()
    .sort_values()
)

channel_orders = (
    period.groupby("sales_channel")["order_id"]
    .nunique()
    .sort_values()
)

print("\nSupporting metrics")
print("\nMonthly revenue by channel:")
print(channel_monthly)

print("\nAverage order value by channel:")
print(channel_aov)

print("\nOrders by channel:")
print(channel_orders)