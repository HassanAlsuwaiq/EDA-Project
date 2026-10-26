import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sleep & Stress Dashboard", layout="wide")

COLORS = px.colors.qualitative.Vivid

@st.cache_data
def load_data():
    return pd.read_csv("sleep_mobile_stress_dataset_15000_cleaned.csv")

df = load_data()

# ---------------- Sidebar ----------------
st.sidebar.header("About the dataset")
st.sidebar.write(
    "15,000 people (14,415 after cleaning) with their screen time, sleep, "
    "caffeine, activity, stress and mental fatigue. Source: Kaggle."
)

st.sidebar.header("Filters")
gender = st.sidebar.selectbox("Gender", ["All"] + sorted(df["gender"].unique()))
jobs = st.sidebar.multiselect("Occupation", sorted(df["occupation"].unique()),
                              default=sorted(df["occupation"].unique()))
age = st.sidebar.slider("Age range", int(df["age"].min()), int(df["age"].max()), (18, 59))

data = df[df["occupation"].isin(jobs) & df["age"].between(*age)]
if gender != "All":
    data = data[data["gender"] == gender]

if data.empty:
    st.warning("No data for these filters. Please change them.")
    st.stop()

# ---------------- Main page ----------------
st.title("Sleep, Screen Time & Stress Dashboard")

c1, c2, c3, c4 = st.columns(4)
c1.metric("People", f"{len(data):,}")
c2.metric("Avg screen time (h)", f"{data['daily_screen_time_hours'].mean():.1f}")
c3.metric("Avg sleep (h)", f"{data['sleep_duration_hours'].mean():.1f}")
c4.metric("Avg stress (0-10)", f"{data['stress_level'].mean():.1f}")

st.subheader("Data preview")
st.dataframe(data.head(10), use_container_width=True)

st.subheader("Summary statistics")
st.dataframe(data.describe().round(2), use_container_width=True)

st.subheader("Interactive visualizations")
left, right = st.columns(2)

with left:
    sample = data.sample(min(2000, len(data)), random_state=1)
    fig = px.scatter(sample, x="daily_screen_time_hours", y="stress_level",
                     color="occupation", opacity=0.6, color_discrete_sequence=COLORS,
                     title="Screen time vs stress")
    st.plotly_chart(fig, use_container_width=True)

    fig = px.histogram(data, x="stress_level", nbins=20, color="gender",
                       color_discrete_sequence=COLORS, title="Stress level distribution")
    st.plotly_chart(fig, use_container_width=True)

with right:
    avg = data.groupby("occupation")["stress_level"].mean().sort_values().reset_index()
    fig = px.bar(avg, x="stress_level", y="occupation", orientation="h",
                 color="stress_level", color_continuous_scale="Tealgrn",
                 title="Average stress by occupation")
    st.plotly_chart(fig, use_container_width=True)

    num = data.select_dtypes("number").drop(columns="user_id")
    fig = px.imshow(num.corr().round(2), text_auto=True, color_continuous_scale="RdBu_r",
                    zmin=-1, zmax=1, title="Correlation heatmap")
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Insights (calculated from the filtered data) ----------------
st.subheader("Insights")
corr = data.select_dtypes("number").corr()["stress_level"]
top_job = avg.iloc[-1]
st.info(f"**Screen time:** correlation with stress is {corr['daily_screen_time_hours']:.2f}, "
        "so more screen time goes with more stress.")
st.info(f"**Sleep quality:** correlation with stress is {corr['sleep_quality_score']:.2f}, "
        "so better sleep goes with lower stress.")
st.info(f"**Mental fatigue:** correlation with stress is {corr['mental_fatigue_score']:.2f}, "
        "the strongest link of all.")
st.info(f"**Occupation:** {top_job['occupation']} has the highest average stress "
        f"({top_job['stress_level']:.2f}), but the gap between jobs is small.")
st.info("**Caffeine and physical activity:** almost no relationship with stress or sleep.")
