import pandas as pd

# 1. LOAD RAW DATA
df = pd.concat(
    pd.read_excel("Data/Raw/online_retail_II.xlsx", sheet_name=None).values(),
    ignore_index=True
)


# 2. INITIAL DATA QUALITY CHECK
print("\n--- INITIAL DATA QUALITY CHECK ---")
print("Shape:", df.shape)
print("\nData types:")
print(df.dtypes)
print("\nMissing values by column:")
print(df.isnull().sum())
print("\nTotal missing cells:", df.isnull().sum().sum())
print("\nDuplicate occurrences:", df.duplicated().sum())
print("\nQuantity and Price summary:")
print(df[["Quantity", "Price"]].describe())
print("\nQuantity and Price values less than or equal to zero:")
print((df[["Quantity", "Price"]] <= 0).sum())
print("\nSample rows:")
print(df[["Invoice", "Customer ID", "Description"]].head())


# 3. SAVE INITIAL MISSING-VALUE AND NEGATIVE-VALUE REPORTS
m = df.isnull().sum()

pd.DataFrame({
    "Count": m,
    "%": (m / len(df) * 100).round(2)
}).to_csv("reports/raw_missing_values_report.csv")

for col in ["Quantity", "Price"]:
    df[df[col] < 0].to_csv(
        f"reports/negative_{col.lower()}.csv",
        index=False
    )

print("\nMissing-value reports saved successfully.")


# 4. INVESTIGATE DUPLICATES
dup = df[df.duplicated(keep=False)]
'''
dup.to_csv("duplicates.csv", index=False)

print("\n--- DEDUPLICATION VERIFICATION ---")
print("Original rows:", len(df))
print("Duplicate occurrences:", df.duplicated().sum())
'''
sample_duplicates = dup.sort_values(
    by=["Invoice", "StockCode"]
).head(20)

print("\nSample duplicate rows:")
print(sample_duplicates.to_string(index=False))


# 5. REMOVE EXACT DUPLICATES
# 5. REMOVE EXACT DUPLICATES
duplicate_rows_removed = len(df) - len(df.drop_duplicates())

df_clean = df.drop_duplicates().copy()
df_final = df_clean.copy()

print("\nCleaned rows:", len(df_clean))
print("Remaining duplicates:", df_clean.duplicated().sum())
print("Rows removed:", len(df) - len(df_clean))

missing_customer = df_final[df_final["Customer ID"].isnull()].copy()
print("\n--- CUSTOMER ID INVESTIGATION ---")

missing_customer = df_final[
    df_final["Customer ID"].isnull()
].copy()

print("\nInvoice examples:")
print(missing_customer["Invoice"].head(10).to_list())

print("\nInvoice prefix counts:")
print(
    missing_customer["Invoice"]
    .astype(str)
    .str[0]
    .value_counts(dropna=False)
)
print("\n--- QUANTITY INVESTIGATION ---")
print("\npostive Quantity:")
print((missing_customer["Quantity"] > 0).sum())

print("\nNegative Quantity:")
print((missing_customer["Quantity"] < 0).sum())

print("\nZero Quantity:")
print((missing_customer["Quantity"] == 0).sum())

positive_sales = missing_customer[
    missing_customer["Quantity"] > 0
]

print("Positive quantity rows:", len(positive_sales))

print(
    "Price is zero:",
    (positive_sales["Price"] == 0).sum()
)

print(
    "Price is positive:",
    (positive_sales["Price"] > 0).sum()
)

print(
    "Price is negative:",
    (positive_sales["Price"] < 0).sum()
)

print("\n--- MISSING CUSTOMER ID BY COUNTRY ---")



print("\nTop 10 countries:")
print(
    missing_customer["Country"]
    .value_counts()
    .head(10)
)

print("\nMissing Customer ID percentage:")
print(
    round(
        df_final["Customer ID"].isnull().mean() * 100,
        2
    ),
    "%"
)
print("\nExamples with zero Price:")
print(
    missing_customer.loc[
        missing_customer["Price"] == 0,
        ["Invoice", "StockCode", "Description", "Quantity", "Price", "Country"]
    ].head(10).to_string(index=False)
)

print("\nExamples with positive Price:")
print(
    missing_customer.loc[
        missing_customer["Price"] > 0,
        ["Invoice", "StockCode", "Description", "Quantity", "Price", "Country"]
    ].head(10).to_string(index=False)
)

print("\n--- MISSING CUSTOMER ID RATE BY COUNTRY ---")

country_missing_rate = (
    df_final["Customer ID"].isna()
    .groupby(df_final["Country"])
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

print(country_missing_rate.head(10).round(2))

print("\n--- COUNTRY CUSTOMER ID QUALITY REPORT ---")
country_report = df_final.groupby("Country").agg(
    Total_Rows=("Customer ID", "size"),
    Missing_Customer_ID=("Customer ID", lambda x: x.isnull().sum())
)
country_report["Missing_Percentage"] = (
    country_report["Missing_Customer_ID"]
    / country_report["Total_Rows"]
    * 100
)

country_report = country_report.sort_values(
    "Missing_Percentage",
    ascending=False
)

print(country_report.head(15).round(2).to_string())
print("\n--- STOCKCODE CUSTOMER ID INVESTIGATION ---")

missing_customer = df_final[
    df_final["Customer ID"].isnull()
]

invoice_report = missing_customer.groupby("Invoice").agg(
    Rows=("Invoice", "size"),
    Unique_Products=("StockCode", "nunique"),
    Positive_Quantity=("Quantity", lambda x: (x > 0).sum()),
    Negative_Quantity=("Quantity", lambda x: (x < 0).sum())
)
print("\n--- MISSING CUSTOMER ID BY INVOICE ---")

print("Unique invoices:", len(invoice_report))

print("\nInvoices with the most missing-ID rows:")
print(
    invoice_report.sort_values(
        "Rows", ascending=False
    ).head(15).to_string()
)

print("\n--- MISSING CUSTOMER ID BY YEAR ---")

year_report = missing_customer.groupby(
    missing_customer["InvoiceDate"].dt.year
).agg(
    Missing_Customer_ID=("Invoice", "size"),
    Unique_Invoices=("Invoice", "nunique")
)
print(year_report.to_string())


print("\n--- YEAR-WISE CUSTOMER ID QUALITY ---")

year_quality = df_final.groupby(
    df_final["InvoiceDate"].dt.year
).agg(
    Total_Rows=("Invoice", "size"),
    Missing_Customer_ID=("Customer ID", "count")
)

year_quality["Missing_Customer_ID"] = (
    year_quality["Total_Rows"]
    - year_quality["Missing_Customer_ID"]
)

year_quality["Missing_Percentage"] = (
    year_quality["Missing_Customer_ID"]
    / year_quality["Total_Rows"] * 100
).round(2)

print(year_quality.to_string())


known_customer = df_final[
    df_final["Customer ID"].notna()
]

missing_stockcodes = missing_customer["StockCode"].unique()

related_rows = known_customer[
    known_customer["StockCode"].isin(missing_stockcodes)
]

print("Rows with missing Customer ID:", len(missing_customer))

print(
    "Unique StockCodes in missing-ID rows:",
    missing_customer["StockCode"].nunique()
)

print(
    "Known-ID rows with matching StockCodes:",
    len(related_rows)
)

print(
    "Unique matching StockCodes:",
    related_rows["StockCode"].nunique()
)

print("\nExamples of matching rows:")

print(
    related_rows[
        ["StockCode", "Description", "Customer ID", "Country"]
    ].head(10).to_string(index=False)
)
print("\n--- STOCKCODE CUSTOMER UNIQUENESS ---")

known_customer = df_final[
    df_final["Customer ID"].notna()
]

stockcode_customer_count = (
    known_customer.groupby("StockCode")["Customer ID"]
    .nunique()
)

print(
    "StockCodes with only 1 known customer:",
    (stockcode_customer_count == 1).sum()
)

print(
    "StockCodes with multiple known customers:",
    (stockcode_customer_count > 1).sum()
)

print(
    "StockCodes with no known customer:",
    df_final["StockCode"].nunique()
    - stockcode_customer_count.index.nunique()
)
print("\n--- STOCKCODE AND COUNTRY INVESTIGATION ---")

missing_customer = df_final[
    df_final["Customer ID"].isnull()
]

known_customer = df_final[
    df_final["Customer ID"].notna()
]

missing_combinations = missing_customer[
    ["StockCode", "Country"]
].drop_duplicates()

known_combinations = known_customer[
    ["StockCode", "Country", "Customer ID"]
].drop_duplicates()

matching_combinations = missing_combinations.merge(
    known_combinations,
    on=["StockCode", "Country"],
    how="inner"
)

print(
    "Unique missing StockCode-Country combinations:",
    len(missing_combinations)
)

print(
    "Combinations with known customer IDs:",
    len(matching_combinations[["StockCode", "Country"]].drop_duplicates())
)

print(
    "Different known Customer IDs in matching combinations:",
    matching_combinations["Customer ID"].nunique()
)

print("\nExamples:")
print(
    matching_combinations.head(10).to_string(index=False)
)

missing_customer_report = df_final[
    df_final["Customer ID"].isnull()
]

missing_customer_report.to_csv(
    "Reports/missing_customer_id.csv",
    index=False
)

print("Missing Customer ID report saved successfully.")



invoice_ids = missing_customer["Invoice"].unique()
related_rows = df_final[df_final["Invoice"].isin(invoice_ids) & df_final["Customer ID"].notna()]

print("Missing-ID rows:", len(missing_customer))
print("Related rows with known Customer ID:", len(related_rows))
print(
    "Unique invoices with a known Customer ID:",
    related_rows["Invoice"].nunique()
)

print("Rows with missing Customer ID:", len(missing_customer))

print("\nMissing Customer ID by Country:")
print(missing_customer["Country"].value_counts().head(10))

print("\nMissing Customer ID by Quantity:")
print(missing_customer["Quantity"].describe())


pd.DataFrame({
    "Rows": [len(df)],
    "Columns": [len(df.columns)],
    "Missing": [m.sum()],
    "Duplicates": [df.duplicated().sum()],
    "Duplicate_Row": [len(dup)],
    "Negative_Quntity": [(df.Quantity < 0).sum()],
    "Negative_Price": [(df.Price < 0).sum()],
    "Rows after deduplication": [len(df_clean)]
}).to_csv("reports/raw_data_summary.csv", index=False)

df_clean.to_csv(
    "Data/Cleaned/online_retail_deduplicated.csv",
    index=False
)


# 6. MISSING-VALUE REPORT AFTER DEDUPLICATION
missing_count = df_clean.isnull().sum()

missing_report = pd.DataFrame({
    "Count": missing_count,
    "Percentage": (missing_count / len(df_clean) * 100).round(2)
})

missing_report.to_csv(
    "reports/missing_values_after_dedup.csv",
    index=True,
    index_label="Column"
)

missing_customer = df_clean[df_clean["Customer ID"].isnull()]
print("\nRows with missing Customer ID:", len(missing_customer))

missing_des = df_clean[df_clean["Description"].isnull()]
print("Rows with missing Description:", len(missing_des))

missing_customer.to_csv("reports/missing_customer.csv", index=False)
missing_des.to_csv("reports/missing_Description.csv", index=False)


# 7. INVESTIGATE AND RECOVER MISSING DESCRIPTIONS
missing_codes = missing_des["StockCode"].unique()

related_rows = df_clean[
    df_clean["StockCode"].isin(missing_codes)
    & df_clean["Description"].notna()
]

description_counts = related_rows.groupby("StockCode")["Description"].nunique()

safe_codes = description_counts[
    description_counts == 1
].index

description_map = related_rows.groupby(
    "StockCode"
)["Description"].unique().apply(list)

safe_map = {
    stock_code: descriptions[0]
    for stock_code, descriptions in description_map.items()
    if len(descriptions) == 1
}

md = pd.read_csv("reports/missing_Description.csv")
print("\nRepeated StockCodes in missing-description report:", md.StockCode.duplicated().sum())

print("StockCodes with a known description:", len(description_counts))
print("StockCodes with exactly one known description:", len(safe_codes))

related_rows.to_csv(
    "reports/related_description_rows.csv",
    index=False
)

before = df_final["Description"].isna().sum()

df_final["Description"] = df_final["Description"].fillna(
    df_final["StockCode"].map(safe_map)
)

after = df_final["Description"].isna().sum()

print("Missing descriptions before:", before)
print("Missing descriptions after:", after)
print("Descriptions recovered:", before - after)


# 8. SAVE CLEANED DATASET
df_final.to_csv(
    "Data/Cleaned/online_retail_cleaned.csv",
    index=False
)

print("Cleaned dataset saved successfully.")


# 9. FINAL DATA QUALITY VALIDATION
print("\n--- FINAL DATA QUALITY REPORT ---")
print("Original rows:", len(df))
print("Cleaned rows:", len(df_final))
print("Duplicate rows remaining:", df_final.duplicated().sum())

print("\nMissing values by column:")
print(df_final.isnull().sum())

print("\nTotal missing cells:", df_final.isnull().sum().sum())

print("\nNegative Quantity rows:")
print((df_final["Quantity"] < 0).sum())

print("\nNegative Price rows:")
print((df_final["Price"] < 0).sum())


# 10. INVESTIGATE NEGATIVE PRICES
negative_prices = df_final[df_final["Price"] < 0]

print("\nNegative Price rows:", len(negative_prices))

print(
    negative_prices[
        ["Invoice", "StockCode", "Description", "Quantity", "Price", "Customer ID"]
    ].to_string(index=False)
)

negative_prices.to_csv(
    "reports/negative_price_investigation.csv",
    index=False
)

print("Negative Price report saved.")


# 11. INVESTIGATE NEGATIVE QUANTITIES
print("\n--- NEGATIVE QUANTITY INVESTIGATION ---")

negative_qty = df_final[df_final["Quantity"] < 0].copy()

print("Negative Quantity rows:", len(negative_qty))
print("\nSample negative Quantity rows:")

print(
    negative_qty[
        ["Invoice", "StockCode", "Description", "Quantity", "Price", "Customer ID"]
    ].head(20).to_string(index=False)
)

print("\nNegative Quantity by Description:")
print(
    negative_qty["Description"]
    .value_counts(dropna=False)
    .head(15)
)

negative_qty.to_csv(
    "reports/negative_quantity_investigation.csv",
    index=False
)

print("\nNegative Quantity report saved.")


# 12. CLASSIFY NEGATIVE QUANTITIES
negative_qty["Invoice"] = negative_qty["Invoice"].astype(str)

negative_qty["Transaction_Type"] = "Other Negative Quantity"

print("\nInvoice examples:")
print("\nInvoice starts with C:")
negative_qty.loc[
    negative_qty["Invoice"].str.startswith("C"),
    "Transaction_Type"
] = "Cancellation / Credit Indicator"

negative_qty.loc[
    negative_qty["Description"].isin(
        ["Manual", "Discount", "POSTAGE", "check", "SAMPLES"]
    ),
    "Transaction_Type"
] = "Special Transaction"

print(negative_qty["Transaction_Type"].value_counts())

negative_qty.to_csv(
    "reports/negative_quantity_classified.csv",
    index=False
)

print("\nClassified report saved.")

print(
    negative_qty.groupby("Transaction_Type").agg(
        Rows=("Invoice", "size"),
        Unique_Invoices=("Invoice", "nunique"),
        Missing_Descriptions=("Description", lambda x: x.isna().sum())
    )
)


# 13. INVESTIGATE OTHER NEGATIVE QUANTITIES
other_negative_qty = negative_qty[
    negative_qty["Transaction_Type"] == "Other Negative Quantity"
].copy()

print("\nOther Negative Quantity rows:", len(other_negative_qty))
print("\nSample rows:")

print(
    other_negative_qty[
        ["Invoice", "StockCode", "Description", "Quantity", "Price", "Customer ID"]
    ].head(20).to_string(index=False)
)

print("\nInvoice prefix counts:")
print(other_negative_qty["Invoice"].str[0].value_counts(dropna=False))

print("\nMissing Description count:")
print(other_negative_qty["Description"].isna().sum())

other_negative_qty.to_csv(
    "reports/other_negative_quantity.csv",
    index=False
)

print("\nOther negative quantity report saved.")


# 14. CHECK NEGATIVE QUANTITY PATTERNS
print("\n--- NEGATIVE QUANTITY PATTERNS ---")

print("\nPrice distribution:")
print(other_negative_qty["Price"].value_counts(dropna=False).head(10))

print("\nQuantity summary:")
print(other_negative_qty["Quantity"].describe())

print("\nDescriptions containing stock issue terms:")

issue_terms = (
    r"lost|damage|mixed|invcd|sold as|short|"
    r"missing|broken|adjust"
)

issue_rows = other_negative_qty[
    other_negative_qty["Description"].str.contains(
        issue_terms,
        case=False,
        na=False
    )
]

print("Matching rows:", len(issue_rows))

print(
    issue_rows[
        [
            "Invoice",
            "StockCode",
            "Description",
            "Quantity",
            "Price",
            "Customer ID"
        ]
    ].head(30).to_string(index=False)
)

print("\nPrice equal to zero:", (other_negative_qty["Price"] == 0).sum())
print("\nPrice greater than zero:", (other_negative_qty["Price"] > 0).sum())
print("Price is negative:", (other_negative_qty["Price"] < 0).sum())


# 15. CLASSIFY STOCK ADJUSTMENT CATEGORIES
print("\n--- STOCK ADJUSTMENT CATEGORIES ---")

other_negative_qty["Description_Text"] = (
    other_negative_qty["Description"]
    .fillna("")
    .str.lower()
)

other_negative_qty["Adjustment_Type"] = "Unclassified Adjustment"

other_negative_qty.loc[
    other_negative_qty["Description_Text"].str.contains(
        r"damage|damages|damaged|broken",
        na=False
    ),
    "Adjustment_Type"
] = "Damaged Stock Indicator"

other_negative_qty.loc[
    other_negative_qty["Description_Text"].str.contains(
        r"lost|missing",
        na=False
    ),
    "Adjustment_Type"
] = "Lost or Missing Stock Indicator"

other_negative_qty.loc[
    other_negative_qty["Description_Text"].str.contains(
        r"mixed|short|invcd|sold as",
        na=False
    ),
    "Adjustment_Type"
] = "Stock Correction Indicator"

other_negative_qty.loc[
    other_negative_qty["Description"].isna(),
    "Adjustment_Type"
] = "Missing Description"

print(other_negative_qty["Adjustment_Type"].value_counts())

other_negative_qty.to_csv(
    "reports/stock_adjustment_categories.csv",
    index=False
)

print("\nStock adjustment categories saved.")


# 16. CREATE DATA QUALITY AUDIT LOG
print("\n--- DATA QUALITY AUDIT LOG ---")

audit_log = [
    {
        "Action": "Remove Exact Duplicates",
        "Reason": "Duplicate records can affect analysis",
        "Rows_Affected": len(df) - len(df_clean)
    },
    {
        "Action": "Recover Missing Descriptions",
        "Reason": "Use a unique known description for the same StockCode",
        "Rows_Affected": before - after
    },
    {
        "Action": "Classify Negative Quantities",
        "Reason": "Identify possible cancellations and stock adjustments",
        "Rows_Affected": len(negative_qty)
    },
    {
        "Action": "Investigate Negative Prices",
        "Reason": "Identify unusual accounting adjustments",
        "Rows_Affected": (df_final["Price"] < 0).sum()
    }
]

audit_df = pd.DataFrame(audit_log)

print(audit_df.to_string(index=False))

audit_df.to_csv(
    "reports/data_quality_audit_log.csv",
    index=False
)

saved_df = pd.read_csv(
    "Data/Cleaned/online_retail_cleaned.csv"
)

print("Saved file shape:", saved_df.shape)
print(
    "Missing descriptions:",
    saved_df["Description"].isnull().sum()
)
print(
    "Duplicate rows:",
    saved_df.duplicated().sum()
)

comparison_report = {
    "Metric": [
        "Total Rows",
        "Duplicate Rows",
        "Missing Descriptions",
        "Missing Customer ID"
    ],
    "Before_Cleaning": [
        len(df),
        df.duplicated().sum(),
        df["Description"].isnull().sum(),
        df["Customer ID"].isnull().sum()
    ],
   "After_Cleaning": [
    len(df_final),
    df_final.duplicated().sum(),
    df_final["Description"].isnull().sum(),
    df_final["Customer ID"].isnull().sum()
]
}

comparison_df = pd.DataFrame(comparison_report)

print("\n--- BEFORE VS AFTER CLEANING ---")
print(comparison_df.to_string(index=False))

comparison_df.to_csv(
    "reports/before_after_comparison.csv",
    index=False
)

print("\nComparison report saved successfully!")

print("\n--- DATA VALIDATION ---")

if df_clean.duplicated().sum() == 0:
    print("PASS: No duplicate rows")
else:
    print("FAIL: Duplicate rows found")

missing_descriptions = df_final["Description"].isnull().sum()
missing_descriptions_before = df_clean["Description"].isnull().sum()

if missing_descriptions <= missing_descriptions_before:
    print("PASS: Missing descriptions did not increase")
else:
    print("FAIL: Missing descriptions increased")

expected_rows = len(df) - duplicate_rows_removed

if len(df_clean) == expected_rows:
    print("PASS: Row count is correct")
else:
    print("FAIL: Row count does not match expected value")

validation_report = {
    "Check": [
        "Duplicate Rows",
        "Missing Descriptions",
        "Cleaned Rows"
    ],
    "Result": [
        "PASS" if df_final.duplicated().sum() == 0 else "FAIL",
        "PASS" if df_final["Description"].isnull().sum() <= 1301 else "CHECK",
        "PASS" if len(df_final) == 1033036 else "CHECK"
    ]
}

validation_df = pd.DataFrame(validation_report)

validation_df.to_csv(
    "reports/data_validation_report.csv",
    index=False
)

print("\nValidation report saved successfully!")