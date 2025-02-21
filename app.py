import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="Personal Finance Dashboard", layout="wide")

# Title and description
st.title("Personal Finance Dashboard")
st.write("Upload your transaction CSV file to monitor income, expenses, and savings.")
st.write("Your CSV file should have columns such as:")
st.markdown("""
| Date       | Description | Category | Amount |
|------------|-------------|----------|--------|
| 2025-01-01 | Salary      | Income   | 5000   |
| 2025-01-05 | Groceries   | Food     | -150   |
| 2025-01-10 | Rent        | Living   | -1200  |
""")

# Function to load data with caching for performance
@st.cache_data
def load_data(file):
    df = pd.read_csv(file, parse_dates=['Date'])
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    return df

# File uploader widget
uploaded_file = st.file_uploader("Upload your finance CSV", type=["csv"])

if uploaded_file is not None:
    # Load and display data 
    data = load_data(uploaded_file)
    st.subheader("Data Preview")
    st.dataframe(data.head())

    # Sidebar filters
    st.sidebar.header("Filters")

    # Date filter
    min_date = data['Date'].min().date()
    max_date = data['Date'].max().date()
    start_date, end_date = st.sidebar.date_input("Select date range", [min_date, max_date])
    
    if isinstance(start_date, tuple):
        start_date, end_date = start_date  # Unpack if tuple

    # Apply date filter
    mask_date = (data['Date'] >= pd.to_datetime(start_date)) & (data['Date'] <= pd.to_datetime(end_date))
    filtered_data = data.loc[mask_date]

    # Category filter
    all_categories = filtered_data['Category'].unique().tolist()
    selected_categories = st.sidebar.multiselect("Select categories", options=all_categories, default=all_categories)
    filtered_data = filtered_data[filtered_data['Category'].isin(selected_categories)]

    # Summary Statistics
    income = filtered_data[filtered_data['Amount'] > 0]['Amount'].sum()
    expenses = filtered_data[filtered_data['Amount'] < 0]['Amount'].sum()
    net_savings = income + expenses

    st.subheader("Summary Statistics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"${income:,.2f}")
    col2.metric("Total Expenses", f"${abs(expenses):,.2f}")
    col3.metric("Net Savings", f"${net_savings:,.2f}")

    # Visualization: Cash Flow Over Time
    st.subheader("Cash Flow Over Time")
    cash_flow = filtered_data.groupby('Date')['Amount'].sum().reset_index()
    fig_line = px.line(cash_flow, x='Date', y='Amount', title="Daily Cash Flow", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

    # Visualization: Spending Distribution (Pie Chart)
    st.subheader("Spending Distribution by Category")
    # Only consider expenses for the pie chart (make amounts positive)
    expense_data = filtered_data[filtered_data['Amount'] < 0].copy()
    expense_data['Absolute Amount'] = expense_data['Amount'].abs()
    expense_summary = expense_data.groupby('Category')['Absolute Amount'].sum().reset_index()
    fig_pie = px.pie(expense_summary, names='Category', values='Absolute Amount', title="Expenses by Category")
    st.plotly_chart(fig_pie, use_container_width=True)

    # Visualization: Income/Expenses by Category (Bar Chart)
    st.subheader("Income and Expenses by Category")
    category_summary = filtered_data.groupby('Category')['Amount'].sum().reset_index()
    fig_bar = px.bar(category_summary, x='Category', y='Amount', title="Net Amount by Category",
                     color='Amount', color_continuous_scale=['red', 'green'])
    st.plotly_chart(fig_bar, use_container_width=True)

    st.write("Adjust the filters in the sidebar to explore your data further.")
else:
    st.info("Awaiting CSV file upload. Please upload a CSV file with your finance data.")
