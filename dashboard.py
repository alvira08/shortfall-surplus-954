import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Shortfall Surplus KPP Pratama Biak", layout="wide")
st.title("📊 Shortfall Surplus KPP 954")
st.markdown("sumber: MPN Info last updated on April, 30 2025")

# Load the Excel file directly from your local directory
# Update this with the correct file path if needed
df = pd.read_excel("shortfall_surplus.xlsx", dtype={"NPWP FULL": str})

# Rename headers
df.columns = ["Tax ID", "Name", "Type of Tax",
              "Sum 2024", "Sum 2025", "Difference", "Account Representative"]

# Create Change Type column
df["Change Type"] = df["Difference"].apply(
    lambda x: "Shortfall" if x < 0 else "Surplus")

# Sidebar Filters
st.sidebar.header("🔍 Filters")

# Filter by Surplus or Shortfall
change_option = st.sidebar.selectbox(
    "Select Change Type", ["Surplus", "Shortfall"])

# 1. Group by taxpayer and calculate total difference
taxpayer_totals = (
    df.groupby("Name")["Difference"]
    .sum()
    .reset_index()
    .rename(columns={"Difference": "Total Difference"})
)

# 2. Filter taxpayer names based on their total change type
if change_option == "Shortfall":
    filtered_names = taxpayer_totals[taxpayer_totals["Total Difference"] < 0]["Name"]
else:
    filtered_names = taxpayer_totals[taxpayer_totals["Total Difference"] >= 0]["Name"]

# 3. Keep all tax rows for those filtered names, alurnya grouping > condition > execution, kalau ga ada .isin dan stop di if aja maka ga bisa menampilkan semua row datanya (cuma dapat nama aja)
filtered_df = df[df["Name"].isin(filtered_names)]

# Filter by Tax Type (multi-select) so basically ambil kodeMAP dan hapus yg N/A dan yg duplicate dropna unique
available_types = filtered_df["Type of Tax"].dropna().unique()
selected_types = st.sidebar.multiselect(
    "Select Tax Type(s)", available_types, default=available_types)
# updated version of the previous one before, it's like the old one get the code and the this one appear
filtered_df = filtered_df[filtered_df["Type of Tax"].isin(selected_types)]

# Sort option this one doesn't need the filtered_df updated cause besically not updating data and just sort it
sort_option = st.sidebar.radio(
    "Sort Top Taxpayers By:",
    ["2025 Total", "Difference (Change)"],
    index=0
)

# Display Top Taxpayers Grouped by Name
st.subheader(
    f"💰 Top Taxpayers with a {change_option} in Selected Tax Types (2025)")
top_n = st.slider("How many top taxpayers to show?",
                  min_value=5, max_value=100, value=10)

# Get top taxpayer names based on sorting option ascending=False is biggest to lowest
if sort_option == "2025 Total":
    top_names = (
        filtered_df.groupby("Name")["Sum 2025"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .index
    )
else:  # Sort by Difference why we use index instead of reset_index? cause we only filter name her not a whole data frame
    top_names = (
        filtered_df.groupby("Name")["Difference"]
        .sum()
        .abs()
        .sort_values(ascending=False)
        .head(top_n)
        .index
    )

# Expander for each taxpayer
for name in top_names:
    taxpayer_data = filtered_df[filtered_df["Name"] == name]
    total_2024 = taxpayer_data["Sum 2024"].sum()
    total_2025 = taxpayer_data["Sum 2025"].sum()
    # Total Difference for this taxpayer
    diff_total = taxpayer_data["Difference"].sum()

    with st.expander(f"{name} — Total 2025: {total_2025:,.2f}"):
        # Display the total difference
        st.write(f"📉 Total Difference: {diff_total:,.2f}")
        st.write(
            taxpayer_data[["Type of Tax", "Sum 2024", "Sum 2025", "Difference", "Account Representative"]].reset_index(drop=True))

# Charts (based on full filtered_df still)
st.subheader("📊 Bar Chart: 2024 vs 2025 (Top Taxpayers Combined)")
chart_df = (
    filtered_df.groupby("Name")[["Sum 2024", "Sum 2025"]]
    .sum()
    .loc[top_names]
    .sort_values("Sum 2025", ascending=False)
)
st.bar_chart(chart_df)


# Download filtered data
st.subheader("⬇️ Download Filtered Data")
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="filtered_tax_data.csv",
    mime="text/csv",
)

# Option to show raw filtered data
if st.checkbox("Show Raw Filtered Data"):
    st.subheader("📄 Raw Filtered Data")
    st.write(filtered_df.reset_index(drop=True))
