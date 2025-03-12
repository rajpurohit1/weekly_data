import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta
 
# 🔹 Load Excel file
df_MAIN = pd.read_excel('input_other work.xlsm')
df = df_MAIN[['Key', 'Summary', 'Assignee', 'Customer Request Type', 'Created', 'Root Cause for PBSD', 'Total Hrs']].copy()
df['Created'] = pd.to_datetime(df['Created'])
 
# 🔹 Round "Total Hrs" to 1 decimal place
df['Total Hrs'] = df['Total Hrs'].round(1)
 
# 🔹 Find Latest Date from Data
latest_date = df['Created'].max()
 
# 🔹 Function to filter data based on latest date
def filter_data(days):
    start_date = latest_date - timedelta(days=days)
    return df[df['Created'] >= start_date]
 
# 🔹 Streamlit UI
st.title("POWER BI SUPPORT KPI")
 
# 🔹 Sidebar Filters
st.sidebar.header("🔍 Filter Options")
filter_option = st.sidebar.radio("Select Date Range:", ["7 Days", "15 Days", "Last Month"])
days_map = {"7 Days": 7, "15 Days": 15, "Last Month": 30}
filtered_df = filter_data(days_map[filter_option])
 
# 🔹 Table Display with Filters
st.write("Filtered Ticket Data")
 
if not filtered_df.empty:
    # 🔹 Clickable Ticket Number
    filtered_df["Ticket Number"] = filtered_df["Key"]  
    filtered_df["JIRA Link"] = "https://adlm.nielseniq.com/jira/browse/" + filtered_df["Key"]  
 
    # 🔹 Display Table
    st.data_editor(
        filtered_df[["Ticket Number", "Summary", "Assignee", "Customer Request Type", "Created", "Root Cause for PBSD", "Total Hrs", "JIRA Link"]],
        column_config={
            "JIRA Link": st.column_config.LinkColumn("Open Ticket"),
            "Ticket Number": st.column_config.TextColumn("Ticket Number"),
            "Total Hrs": st.column_config.NumberColumn("Total Hrs", format="%.1f")  # 1 Decimal place in Table
        },
        height=400
    )
 
else:
    st.warning("⚠ No tickets found for the selected date range.")
 
# 🔹 Buttons for Graph Selection
st.write("Select Graph to Display")
selected_graph = st.radio("Choose a Graph:", ["Existing Resolution Time Graph", "Tickets by Root Cause", "Average Hours to Resolve"])
 
# 🔹 Graph 1: Existing Resolution Time Graph (This will be the one that was already there)
if selected_graph == "Existing Resolution Time Graph":
    st.write("Resolution Time Analysis")
    if not filtered_df.empty:
        fig1 = px.bar(filtered_df, x="Key", y="Total Hrs", color="Assignee", text_auto=".1f",  # 1 Decimal place
                      title="Resolution Time Analysis")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.warning("⚠ Not enough data for Resolution Time graph.")
 
# 🔹 Graph 2: Ticket Count by Root Cause per Assignee
elif selected_graph == "Tickets by Root Cause":
    st.write("Tickets by Root Cause")
    if not filtered_df.empty:
        ticket_count = filtered_df.groupby(["Assignee", "Root Cause for PBSD"]).size().reset_index(name="Ticket Count")
        total_created = filtered_df.groupby("Assignee").size().reset_index(name="Total Created")
 
        fig2 = px.bar(ticket_count, x="Assignee", y="Ticket Count", color="Root Cause for PBSD",
                      title="Tickets by Root Cause", barmode="stack", text_auto=".1f")  # 1 Decimal place
 
        fig2.add_scatter(x=total_created["Assignee"], y=total_created["Total Created"], mode="lines+markers",
                         name="Total Created", line=dict(color="red", width=2))
 
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("⚠ Not enough data for Ticket Count graph.")
 
# 🔹 Graph 3: Average Resolution Time by Root Cause per Assignee
elif selected_graph == "Average Hours to Resolve":
    st.write("Average Hours to Resolve")
    if not filtered_df.empty:
        avg_hours = filtered_df.groupby(["Assignee", "Root Cause for PBSD"])["Total Hrs"].mean().reset_index()
        overall_avg = filtered_df.groupby("Assignee")["Total Hrs"].mean().reset_index()
 
        # 🔹 Round values to 1 decimal place
        avg_hours["Total Hrs"] = avg_hours["Total Hrs"].round(1)
        overall_avg["Total Hrs"] = overall_avg["Total Hrs"].round(1)
 
        fig3 = px.bar(avg_hours, x="Assignee", y="Total Hrs", color="Root Cause for PBSD",
                      title="Average Hours to Resolve", barmode="stack", text_auto=".1f")  # 1 Decimal place
 
        fig3.add_scatter(x=overall_avg["Assignee"], y=overall_avg["Total Hrs"], mode="lines+markers",
                         name="Average of Total Hrs", line=dict(color="gold", width=2))
 
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("⚠ Not enough data for Resolution Time graph.")
 