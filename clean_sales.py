import pandas as pd
import re
from datetime import datetime

# ----------------------------
# 1) Load raw data
# ----------------------------
df = pd.read_csv("urbankart_sales_messy.csv", dtype=str)
raw_rows = len(df)

# ----------------------------
# 2) Remove exact duplicates
# ----------------------------
before_dedup = len(df)
df = df.drop_duplicates(keep="first")
dupes_removed = before_dedup - len(df)

# ----------------------------
# 3) Standardize dates to YYYY-MM-DD
# ----------------------------
def parse_date(val):
    if pd.isna(val) or str(val).strip() == "":
        return pd.NA
    s = str(val).strip()

    # Already ISO: 2026-03-08
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return s

    # dd/mm/yyyy or dd-mm-yyyy
    m = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", s)
    if m:
        d, mo, y = m.groups()
        return f"{y}-{int(mo):02d}-{int(d):02d}"

    # dd-mm-yy (2026 context)
    m = re.fullmatch(r"(\d{1,2})-(\d{1,2})-(\d{2})", s)
    if m:
        d, mo, y2 = m.groups()
        y = "20" + y2
        return f"{y}-{int(mo):02d}-{int(d):02d}"

    # "Mar 8, 2026"
    try:
        dt = datetime.strptime(s, "%b %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass

    # Fallback
    try:
        dt = pd.to_datetime(s, dayfirst=True)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return pd.NA

df["order_date"] = df["order_date"].apply(parse_date)

# ----------------------------
# 4) Standardize city names
# ----------------------------
city_map = {
    "gurgaon": "Gurugram",
    "ggn": "Gurugram",
    "bangalore": "Bengaluru",
    "blr": "Bengaluru",
    "bombay": "Mumbai",
    "calcutta": "Kolkata",
    "madras": "Chennai",
    "cochin": "Kochi",
    "new delhi": "Delhi",
}

def standardize_city(val):
    if pd.isna(val) or str(val).strip() == "":
        return val
    s = str(val).strip().lower()
    return city_map.get(s, s.title())

df["city"] = df["city"].apply(standardize_city)

# ----------------------------
# 5) Standardize product names
# ----------------------------
official_products = [
    "43-inch Smart TV",
    "Bluetooth Speaker Mini",
    "Mirrorless Camera Lite",
    "Noise-Cancelling Headphones",
    "Power Bank 20000mAh",
    "Smart Watch X2",
    "Ultrabook Air 14",
    "Wireless Earbuds Pro",
    "Cotton Kurta Set",
    "Denim Jacket",
    "Ethnic Dupatta",
    "Formal Shirt",
    "Leather Wallet",
    "Running Sneakers",
    "Silk Saree",
    "Slim Fit Jeans",
    "Air Fryer 5L",
    "Cotton Bedsheet Set",
    "Dinner Set 24pc",
    "Electric Kettle 1.5L",
    "Mixer Grinder 750W",
    "Modern Wall Clock",
    "Non-Stick Cookware Set",
    "Robot Vacuum R7",
    "Beard Grooming Kit",
    "Eau de Parfum 100ml",
    "Face Wash Combo",
    "Ionic Hair Dryer",
    "Makeup Brush Set",
    "Matte Lipstick Set",
    "Sunscreen SPF50",
    "Vitamin C Serum",
    "Adjustable Dumbbells 15kg",
    "Badminton Racket Set",
    "Cricket Bat English Willow",
    "Cycling Helmet",
    "Foldable Treadmill T2",
    "Football Size 5",
    "Gym Gloves",
    "Yoga Mat Pro",
]

product_lookup = {p.lower().strip(): p for p in official_products}

def standardize_product(val):
    if pd.isna(val) or str(val).strip() == "":
        return val
    s = str(val).strip()
    key = s.lower()
    return product_lookup.get(key, s)

df["product_name"] = df["product_name"].apply(standardize_product)

# ----------------------------
# 6) Clean total_revenue (text → number)
# ----------------------------
def clean_revenue(val):
    if pd.isna(val) or str(val).strip() == "":
        return pd.NA
    s = str(val).strip()
    s = re.sub(r"[₹,]", "", s)
    s = re.sub(r"\s*INR\s*", "", s, flags=re.IGNORECASE).strip()
    try:
        num = float(s)
        return int(num) if num.is_integer() else num
    except ValueError:
        return pd.NA

df["total_revenue"] = df["total_revenue"].apply(clean_revenue)

# ----------------------------
# 7) Clean quantity
# ----------------------------
def clean_quantity(val):
    if pd.isna(val) or str(val).strip() == "":
        return pd.NA
    try:
        q = float(str(val).strip())
        return int(q) if q.is_integer() else q
    except ValueError:
        return pd.NA

df["quantity"] = df["quantity"].apply(clean_quantity)

# ----------------------------
# 8) Drop rows with missing quantity or total_revenue
# ----------------------------
drop_missing_count = int((df["quantity"].isna() | df["total_revenue"].isna()).sum())
df = df[df["quantity"].notna() & df["total_revenue"].notna()].copy()

# ----------------------------
# 9) Fill blank region from city
# ----------------------------
region_by_city = {
    "Delhi": "North",
    "Gurugram": "North",
    "Noida": "North",
    "Chandigarh": "North",
    "Bengaluru": "South",
    "Chennai": "South",
    "Hyderabad": "South",
    "Kochi": "South",
    "Mumbai": "West",
    "Pune": "West",
    "Ahmedabad": "West",
    "Surat": "West",
    "Kolkata": "East",
    "Bhubaneswar": "East",
    "Guwahati": "East",
    "Patna": "East",
    "Indore": "Central",
    "Bhopal": "Central",
    "Nagpur": "Central",
    "Raipur": "Central",
}

def fill_region(row):
    if pd.notna(row["region"]) and str(row["region"]).strip() != "":
        return str(row["region"]).strip()
    city = row["city"]
    if pd.isna(city):
        return pd.NA
    return region_by_city.get(city, pd.NA)

df["region"] = df.apply(fill_region, axis=1)

# ----------------------------
# 10) Drop rows with quantity <= 0
# ----------------------------
drop_invalid_qty_count = int((df["quantity"] <= 0).sum())
df = df[df["quantity"] > 0].copy()

# ----------------------------
# 11) Tidy text fields
# ----------------------------
str_cols = ["order_id", "region", "city", "product_name", "category", "customer_id", "sales_channel"]

for col in str_cols:
    df[col] = df[col].astype(str).replace("nan", pd.NA)
    df[col] = df[col].apply(lambda x: x.strip() if pd.notna(x) and isinstance(x, str) else x)

region_std = {"north": "North", "south": "South", "east": "East", "west": "West", "central": "Central"}
df["region"] = df["region"].apply(lambda x: region_std.get(str(x).lower(), x) if pd.notna(x) else x)

# ----------------------------
# 12) Clean unit_price
# ----------------------------
def clean_price(val):
    if pd.isna(val) or str(val).strip() == "":
        return pd.NA
    s = str(val).strip()
    s = re.sub(r"[₹,]", "", s)
    s = re.sub(r"\s*INR\s*", "", s, flags=re.IGNORECASE).strip()
    try:
        return float(s)
    except ValueError:
        return pd.NA

df["unit_price"] = df["unit_price"].apply(clean_price)

# ----------------------------
# 13) Validate quantity * unit_price = total_revenue
# ----------------------------
df["expected_revenue"] = df["quantity"] * df["unit_price"]
df["revenue_diff"] = (df["total_revenue"] - df["expected_revenue"]).abs()

bad_rows = df[df["revenue_diff"] > 0.01]
if len(bad_rows) > 0:
    print("WARNING: Some rows fail the revenue check. Inspect 'bad_rows' before proceeding.")
    # For debugging, you can uncomment:
    # print(bad_rows.head(20))

df = df.drop(columns=["expected_revenue", "revenue_diff"])

# ----------------------------
# 14) Finalize columns and types
# ----------------------------
cols = [
    "order_id", "order_date", "region", "city", "product_name",
    "category", "quantity", "unit_price", "total_revenue",
    "customer_id", "sales_channel"
]

df = df[cols]

df["quantity"] = df["quantity"].astype(int)
if (df["total_revenue"] % 1 == 0).all():
    df["total_revenue"] = df["total_revenue"].astype(int)

# ----------------------------
# 15) Save cleaned CSV
# ----------------------------
df.to_csv("urbankart_sales_clean.csv", index=False)

clean_rows = len(df)

print("Raw rows:", raw_rows)
print("Duplicates removed:", dupes_removed)
print("Dropped (missing qty/revenue):", drop_missing_count)
print("Dropped (qty ≤ 0):", drop_invalid_qty_count)
print("Clean rows:", clean_rows)