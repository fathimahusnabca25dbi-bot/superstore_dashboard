import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Superstore Dashboard",page_icon="📊",layout="wide",initial_sidebar_state="expanded")

@st.cache_data
def load_data():
    df=pd.read_csv(r"C:\Users\admin\OneDrive\Desktop\superstore\output\Superstar_Clean",parse_dates=["Order Date","Ship Date"])

    return df


df=load_data()

st.title("Superstore Sales Dashboard")

with st.sidebar:
    st.header("Filters")
    regions = st.multiselect("Region", options=df["Region"].unique(), default=df["Region"].unique())
    
    years= st.multiselect("Order Year", options=df["Order Year"].unique(), default=df["Order Year"].unique())

    with st.form("date_filters"):
        st.write("Date range" )
        start=st.date_input("Start date", value=df["Order Date"].min().date())
        end=st.date_input("End date", value=df["Order Date"].max().date())
        submitted=st.form_submit_button("Apply")
    if st.button("Refresh data"):
      st.cache_data.clear()
      st.rerun()

filtered = df[df["Region"].isin(regions) & df["Order Year"].isin(years)]   
if submitted:
    filtered=df[df["Order Date"].dt.date.between(start,end)]


disc_arr= filtered["Discount"].values
sales_arr= filtered["Sales"].values
high_disc_pct= np.percentile(disc_arr, 75) if len(disc_arr) else 0
high_disc_n= int(np.sum(disc_arr > high_disc_pct)) if len(disc_arr) else 0
z_score= (sales_arr - np.mean(sales_arr)) / np.std(sales_arr) if len(sales_arr) else np.array([])
outliers_n= int(np.sum(np.abs(z_score) > 3)) if len(z_score) else 0
mean_margin= filtered["Profit Margin"].mean() if len(filtered) else 0

st.write(f"showing {len(filtered):,} rows")


c1,c2,c3=st.columns(3)
c1.metric("Total Sales",f"${filtered.Sales.sum():,.0f}")
c2.metric("Total Profit",f"${filtered.Profit.sum():,.0f}")
c3.metric("Average Discount",f"{filtered.Discount.mean()*100:.1f}%")

tab1,tab2,tab3,tab4=st.tabs(["Overview","By category","Region","Quality Alert"])
with tab1:
   st.write("Filtered data- first 20 rows")
   st.dataframe(filtered.head(20),use_container_width=True,hide_index=True)
   st.header("Monthly Sales Trend")
   monthly=filtered.set_index("Order Date").resample("ME")["Sales"].sum()
   st.line_chart(monthly)
with tab2:
    st.subheader("Sales by Category")
    monthly_sales=filtered.groupby("Category")["Sales"].sum().sort_values(ascending=False)
    st.bar_chart(monthly_sales)

    st.subheader("Sub-Category Breakdown")
    summary=filtered.groupby("Sub_Category").agg(
        Sales=("Sales","sum"),
        Profit=("Profit","sum")).sort_values("Sales", ascending=False)
    st.dataframe(summary.style.format("${:,.0f}"),use_container_width=True)

with tab3:
        st.subheader("Profit by Region")
        reg=filtered.groupby("Region")["Profit"].sum().sort_values(ascending=False)
        st.area_chart(reg)

with tab4:
    st.subheader("Alert Banners")

    mean_margin = filtered["Profit Margin"].mean()

    if mean_margin < 10:
        st.error(f"Lower profit: {mean_margin:.1f}% - investigate discounts and product mix")
    elif mean_margin < 20:
        st.warning(f"Moderate profit: {mean_margin:.1f}% - room to improve")
    else:
        st.success(f"Healthy profit: {mean_margin:.1f}% - pricing strategy is working")

    if outliers_n > 0:
        st.warning(f"{outliers_n} Sales outliers detected (|z_score| > 3)")
    else:
        st.success("No sales outliers detected")

    with st.expander("View outlier rows"):
        outliers_mask = np.abs(z_score) > 3 if len(z_score) else np.array([])
        
        outliers = filtered[outliers_mask] if len(outliers_mask) else pd.DataFrame()

        st.dataframe(
            outliers[["Order ID","Order Date","Sales","Profit","Region"]],
            use_container_width=True
        )

     
st.markdown("---")  


min_year=filtered["Order Year"].min()
max_year=filtered["Order Year"].max()
st.caption(f"Showing {len(filtered):,} rows. {min_year}-{max_year}. Built by OJT. DBI Skill Park")
