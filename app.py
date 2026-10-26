import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sleep, Screen Time and Stress", layout="wide")

TEAL, BLUE, ROSE, SAND = "#3E7C7B", "#5B7DB1", "#B9677A", "#D9A566"
SCREEN_LABELS = ["Up to 3 h", "3 to 5 h", "5 to 7 h", "Over 7 h"]


@st.cache_data
def load_data():
    return pd.read_csv("sleep_mobile_stress_dataset_15000_cleaned.csv")


def style(fig, height=380):
    """Same calm look for every chart."""
    fig.update_layout(template="simple_white", height=height,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#2B2F36"), title_font_size=16,
                      margin=dict(l=10, r=10, t=50, b=10))
    return fig


df = load_data()

# ---------------- Sidebar ----------------
st.sidebar.header("About the dataset")
st.sidebar.write(
    "Kaggle dataset with 15,000 people (14,415 after removing invalid gender values). "
    "For each person it records age, gender, occupation, daily screen time, phone use "
    "before sleep, sleep duration and quality, caffeine intake, physical activity, "
    "notifications per day, stress level and mental fatigue."
)

st.sidebar.header("Filters")
gender = st.sidebar.selectbox("Gender", ["All"] + sorted(df["gender"].unique()))
all_jobs = sorted(df["occupation"].unique())
jobs = st.sidebar.multiselect("Occupation", all_jobs, default=all_jobs)
age = st.sidebar.slider("Age range", 18, 59, (18, 59))

data = df[df["occupation"].isin(jobs) & df["age"].between(*age)]
if gender != "All":
    data = data[data["gender"] == gender]

if len(data) < 50:
    st.warning("Too few people match these filters. Please widen them.")
    st.stop()

# ---------------- Header ----------------
st.title("Sleep, Screen Time and Stress")
st.caption("Use the filters on the left. Every number and chart updates with them.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("People", f"{len(data):,}")
c2.metric("Average screen time", f"{data['daily_screen_time_hours'].mean():.1f} h")
c3.metric("Average sleep", f"{data['sleep_duration_hours'].mean():.1f} h")
c4.metric("Average stress", f"{data['stress_level'].mean():.1f} / 10")

st.divider()

# ---------------- Data ----------------
st.header("The data")
st.dataframe(data.head(10), use_container_width=True)
st.dataframe(data.describe().round(2), use_container_width=True)

st.divider()

# ---------------- Charts ----------------
st.header("What is linked to stress?")

num = data.select_dtypes("number").drop(columns="user_id")
corr = num.corr()["stress_level"].drop("stress_level").sort_values()

left, right = st.columns(2)

# 1. Stress by hours of screen time
with left:
    hours = data.assign(hours=data["daily_screen_time_hours"].round().astype(int))
    by_hours = hours.groupby("hours")["stress_level"].agg(["mean", "count"]).reset_index()
    by_hours = by_hours[by_hours["count"] >= 20]
    fig = px.line(by_hours, x="hours", y="mean", markers=True,
                  title="Average stress by daily screen time",
                  labels={"hours": "Screen time (hours per day)", "mean": "Average stress"})
    fig.update_traces(line_color=TEAL, marker_size=9)
    st.plotly_chart(style(fig), use_container_width=True)
    st.caption(f"Stress climbs from {by_hours['mean'].iloc[0]:.1f} at "
               f"{by_hours['hours'].iloc[0]} h to {by_hours['mean'].iloc[-1]:.1f} at "
               f"{by_hours['hours'].iloc[-1]} h of screen time.")

# 2. Correlation of every variable with stress
with right:
    cdf = corr.reset_index()
    cdf.columns = ["variable", "correlation"]
    cdf["variable"] = cdf["variable"].str.replace("_", " ")
    cdf["direction"] = ["More stress" if v > 0 else "Less stress" for v in cdf["correlation"]]
    fig = px.bar(cdf, x="correlation", y="variable", orientation="h", color="direction",
                 color_discrete_map={"More stress": TEAL, "Less stress": ROSE},
                 title="Correlation of each variable with stress")
    fig.update_layout(legend_title_text="", xaxis_title="Correlation (-1 to 1)", yaxis_title="")
    st.plotly_chart(style(fig), use_container_width=True)
    st.caption(f"Strongest links: {corr.abs().idxmax().replace('_', ' ')} "
               f"({corr[corr.abs().idxmax()]:.2f}). Caffeine and physical activity are close to 0.")

left, right = st.columns(2)

# 3. Mental fatigue and sleep quality by screen time
with left:
    both = hours.groupby("hours")[["mental_fatigue_score", "sleep_quality_score"]].mean().reset_index()
    both = both[both["hours"].isin(by_hours["hours"])]
    both = both.rename(columns={"mental_fatigue_score": "Mental fatigue",
                                "sleep_quality_score": "Sleep quality"})
    long = both.melt("hours", var_name="Measure", value_name="Average score")
    fig = px.line(long, x="hours", y="Average score", color="Measure", markers=True,
                  color_discrete_map={"Mental fatigue": ROSE, "Sleep quality": BLUE},
                  title="Mental fatigue and sleep quality by screen time",
                  labels={"hours": "Screen time (hours per day)"})
    fig.update_yaxes(range=[0, 10])
    fig.update_layout(legend_title_text="")
    st.plotly_chart(style(fig), use_container_width=True)
    st.caption(f"Between {both['hours'].iloc[0]} h and {both['hours'].iloc[-1]} h of screen time, "
               f"mental fatigue rises from {both['Mental fatigue'].iloc[0]:.1f} to "
               f"{both['Mental fatigue'].iloc[-1]:.1f} while sleep quality falls from "
               f"{both['Sleep quality'].iloc[0]:.1f} to {both['Sleep quality'].iloc[-1]:.1f}.")

# 4. Occupation
with right:
    occ = data.groupby("occupation")["stress_level"].mean().sort_values().reset_index()
    overall = data["stress_level"].mean()
    fig = px.bar(occ, x="stress_level", y="occupation", orientation="h", text_auto=".2f",
                 title="Average stress by occupation")
    fig.update_traces(marker_color=BLUE)
    fig.add_vline(x=overall, line_dash="dash", line_color=SAND,
                  annotation_text="all people", annotation_position="top")
    fig.update_layout(xaxis_title="Average stress", yaxis_title="")
    st.plotly_chart(style(fig), use_container_width=True)
    gap = occ["stress_level"].max() - occ["stress_level"].min()
    st.caption(f"{occ['occupation'].iloc[-1]} is highest and {occ['occupation'].iloc[0]} "
               f"is lowest, but the gap is only {gap:.2f} points.")

st.divider()

# ---------------- More charts ----------------
st.header("Habits and groups")

# Helper columns: groups with real ranges
data = data.assign(
    screen_group=pd.cut(data["daily_screen_time_hours"], [0, 3, 5, 7, 10], labels=SCREEN_LABELS),
    age_group=pd.cut(data["age"], [17, 29, 39, 49, 59], labels=["18-29", "30-39", "40-49", "50-59"]),
)

left, right = st.columns(2)

# 5. Sleep quality vs stress, coloured by screen time group
with left:
    sample = data.sample(min(2000, len(data)), random_state=1)
    fig = px.scatter(sample, x="sleep_quality_score", y="stress_level", color="screen_group",
                     opacity=0.7, category_orders={"screen_group": SCREEN_LABELS},
                     color_discrete_sequence=["#A8CBC9", "#5B9E9C", TEAL, "#1F4E4D"],
                     title="Sleep quality vs stress",
                     labels={"sleep_quality_score": "Sleep quality", "stress_level": "Stress",
                             "screen_group": "Screen time"})
    st.plotly_chart(style(fig), use_container_width=True)
    r = data["sleep_quality_score"].corr(data["stress_level"])
    st.caption(f"Correlation is {r:.2f}. People with over 7 hours of screen time (dark dots) "
               "cluster at poor sleep quality and high stress.")

# 6. Mental fatigue vs stress
with right:
    fig = px.scatter(sample, x="mental_fatigue_score", y="stress_level", opacity=0.5,
                     title="Mental fatigue vs stress",
                     labels={"mental_fatigue_score": "Mental fatigue", "stress_level": "Stress"})
    fig.update_traces(marker_color=ROSE)
    st.plotly_chart(style(fig), use_container_width=True)
    r2 = data["mental_fatigue_score"].corr(data["stress_level"])
    st.caption(f"Correlation is {r2:.2f}. The dots follow almost a straight line, so people "
               "with high mental fatigue are almost always highly stressed too.")

left, right = st.columns(2)

# 7. Age group
with left:
    age_df = data.groupby("age_group", observed=True)["stress_level"].mean().reset_index()
    fig = px.bar(age_df, x="age_group", y="stress_level", text_auto=".2f",
                 title="Average stress by age group",
                 labels={"age_group": "Age group", "stress_level": "Average stress"})
    fig.update_traces(marker_color=SAND)
    st.plotly_chart(style(fig), use_container_width=True)
    st.caption("Stress is almost the same in every age group.")

# 8. Caffeine
with right:
    cup = data.assign(cups=data["caffeine_intake_cups"].round().astype(int))
    cup = cup.groupby("cups")["stress_level"].agg(["mean", "count"]).reset_index()
    cup = cup[cup["count"] >= 20]
    fig = px.line(cup, x="cups", y="mean", markers=True, title="Average stress by caffeine intake",
                  labels={"cups": "Cups of caffeine per day", "mean": "Average stress"})
    fig.update_traces(line_color=ROSE, marker_size=9)
    fig.update_yaxes(range=[0, 10])
    st.plotly_chart(style(fig), use_container_width=True)
    st.caption("The line is flat: caffeine does not change stress here. "
               "Compare this with the screen time chart above.")

st.divider()

# ---------------- Insights ----------------
st.header("Key insights")
st.markdown(f"""
- **Screen time and stress move together** (correlation {corr['daily_screen_time_hours']:.2f}).
- **Better sleep quality goes with lower stress** (correlation {corr['sleep_quality_score']:.2f}).
- **Mental fatigue is the closest match to stress** (correlation {corr['mental_fatigue_score']:.2f}).
- **Occupation matters very little.** Averages differ by only {gap:.2f} points.
- **Caffeine ({corr['caffeine_intake_cups']:.2f}) and physical activity ({corr['physical_activity_minutes']:.2f})** show almost no link with stress.
- These are correlations, not proof that one thing causes the other.
""")
