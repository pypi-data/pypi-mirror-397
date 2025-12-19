import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from cleaning import clean_results_frame


COUNTRY_TO_CONTINENT = {
    "United States": "North America",
    "Canada": "North America",
    "Mexico": "North America",
    "Puerto Rico": "North America",
    "United Kingdom": "Europe",
    "France": "Europe",
    "Germany": "Europe",
    "Spain": "Europe",
    "Italy": "Europe",
    "Netherlands": "Europe",
    "Belgium": "Europe",
    "Switzerland": "Europe",
    "Austria": "Europe",
    "Sweden": "Europe",
    "Norway": "Europe",
    "Denmark": "Europe",
    "Finland": "Europe",
    "Poland": "Europe",
    "Portugal": "Europe",
    "Greece": "Europe",
    "Brazil": "South America",
    "Argentina": "South America",
    "Chile": "South America",
    "Colombia": "South America",
    "Japan": "Asia",
    "China": "Asia",
    "South Korea": "Asia",
    "India": "Asia",
    "Singapore": "Asia",
    "Hong Kong": "Asia",
    "Taiwan": "Asia",
    "Philippines": "Asia",
    "Thailand": "Asia",
    "Malaysia": "Asia",
    "South Africa": "Africa",
    "Egypt": "Africa",
    "Morocco": "Africa",
    "Kenya": "Africa",
    "Australia": "Oceania",
    "New Zealand": "Oceania",
}

IRONMAN_RUN_MILES = 26.2
IRONMAN_RUN_KM = 42.195


def seconds_to_hhmmss(sec):
    if pd.isna(sec):
        return "—"
    sec = int(round(float(sec)))
    if sec <= 0:
        return "—"
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def map_continent(country):
    if pd.isna(country):
        return "Other"
    return COUNTRY_TO_CONTINENT.get(str(country).strip(), "Other")


def pace_str(seconds_per_unit):
    if pd.isna(seconds_per_unit) or seconds_per_unit <= 0:
        return "—"
    sec = int(round(float(seconds_per_unit)))
    return f"{sec//60}:{sec%60:02d}"



# App starts here ---------------------------------------------------------------------------------------


# cleaning data  ---

st.set_page_config(page_title="Ironman Results Explorer", layout="wide")
st.title("Ironman Results Explorer")

uploaded = st.file_uploader("Upload CSV", type=["csv"])
if not uploaded:
    st.info("Upload a CSV to get started.")
    st.stop()

df = pd.read_csv(uploaded)

modified_dataset = clean_results_frame(df)
fin_df = modified_dataset[modified_dataset.get("Finished", False)].copy()


# SECTION: Participants -------------------------------------------------

st.subheader("Participants")

total = len(modified_dataset)
finishers = int(modified_dataset["Finished"].sum())
dnf = total - finishers

male = female = 0
if "gender_norm" in modified_dataset.columns:
    male = int((modified_dataset["gender_norm"] == "Male").sum())
    female = int((modified_dataset["gender_norm"] == "Female").sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Participants", f"{total:,}")
c2.metric("Finishers", f"{finishers:,}")
c3.metric("Did not finish", f"{dnf:,}")
c4.metric("Male / Female", f"{male:,} / {female:,}")


# SECTION: Participants by continent -------------------------------------------------

st.write("### Participants by continent")

if "Country" in modified_dataset.columns:
    cont = modified_dataset["Country"].apply(map_continent)
    counts = cont.value_counts()

    pct = counts / counts.sum()
    major = counts[pct >= 0.03]
    small = counts[pct < 0.03].sum()
    if small > 0:
        major["Other"] = major.get("Other", 0) + int(small)

    fig = plt.figure(figsize=(5.2, 3.0))
    plt.pie(major.values, labels=major.index, autopct="%1.1f%%")
    st.pyplot(fig, clear_figure=True)

st.divider()


# SECTION: Key summary stats -------------------------------------------------

st.header("Key summary stats")

st.write("### Top 3 athletes by gender")
st.caption("Shows split and transition times to understand pacing strategies.")

for gender in ["Female", "Male"]:
    #divide by gender
    gender_finishers = fin_df[fin_df["gender_norm"] == gender]
    sub = gender_finishers.nsmallest(3, "Overall Time (sec)")
    st.write(f"**{gender}**")

    out = sub.copy()
    out["Overall"] = out["Overall Time (sec)"].apply(seconds_to_hhmmss)
    out["Swim"] = out["Swim Time (sec)"].apply(seconds_to_hhmmss)
    out["Bike"] = out["Bike Time (sec)"].apply(seconds_to_hhmmss)
    out["Run"] = out["Run Time (sec)"].apply(seconds_to_hhmmss)
    out["Transitions"] = out["Transitions (sec)"].apply(seconds_to_hhmmss)

    show_cols = [c for c in ["Bib", "Name", "Country", "Division"] if c in out.columns]
    show_cols += ["Overall", "Swim", "Bike", "Run", "Transitions"]
    st.dataframe(out[show_cols], use_container_width=True)

st.divider()

# SECTION: Discipline impact -------------------------------------------------

st.write("### Discipline that best predicts finishing time")
st.caption(
    "This measures how strongly each discipline time is related to overall finishing time. "
    "Higher correlation means better prediction of final results."
)

disciplines = {
    "Swim": "Swim Time (sec)",
    "Bike": "Bike Time (sec)",
    "Run": "Run Time (sec)",
    "Transitions": "Transitions (sec)",
}

correlations = {}

for name, col in disciplines.items():
    if col in fin_df.columns:
        valid = fin_df.dropna(subset=[col, "Overall Time (sec)"])
        if len(valid) > 10:
            corr = valid[col].corr(valid["Overall Time (sec)"])
            correlations[name] = corr

best = max(correlations, key=correlations.get)
st.write(
        f"**Best predictor of finishing time:** **{best}** "
        f"(correlation = {correlations[best]:.2f})"
    )

fig = plt.figure(figsize=(5, 2.6))
plt.bar(correlations.keys(), correlations.values())
plt.ylabel("Correlation with overall time")
plt.ylim(0, 1)
st.pyplot(fig, clear_figure=True)

st.divider()


# -----------------------------
# Typical finisher
# -----------------------------
st.subheader("Preparation insights")

st.write("#### Typical finisher (aiming to be average)")
st.caption(
    "This represents a realistic goal for most athletes: finishing comfortably "
    "without racing for the top or barely making the cutoff."
)

median_time = fin_df["Overall Time (sec)"].median()
fin_df["dist"] = (fin_df["Overall Time (sec)"] - median_time).abs()
typical = fin_df.sort_values("dist").head(1)

st.write(f"**Overall Time:** {seconds_to_hhmmss(typical['Overall Time (sec)'].iloc[0])}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Swim", seconds_to_hhmmss(typical["Swim Time (sec)"].iloc[0]))
c2.metric("Bike", seconds_to_hhmmss(typical["Bike Time (sec)"].iloc[0]))
c3.metric("Run", seconds_to_hhmmss(typical["Run Time (sec)"].iloc[0]))
c4.metric("Transitions", seconds_to_hhmmss(typical["Transitions (sec)"].iloc[0]))

# SECTION: min/max effort needed to survive -----------------------------

st.write("Completion threshold")

st.write("#### Minimum effort to still finish (slowest finisher)")
st.caption(
    "This shows the slowest finisher's split profile. "
    "If your training paces are faster than this, finishing is realistic."
)

slowest = fin_df.sort_values("Overall Time (sec)", ascending=False).head(1)

st.write(f"**Overall Time:** {seconds_to_hhmmss(slowest['Overall Time (sec)'].iloc[0])}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Swim", seconds_to_hhmmss(slowest["Swim Time (sec)"].iloc[0]))
c2.metric("Bike", seconds_to_hhmmss(slowest["Bike Time (sec)"].iloc[0]))
c3.metric("Run", seconds_to_hhmmss(slowest["Run Time (sec)"].iloc[0]))
c4.metric("Transitions", seconds_to_hhmmss(slowest["Transitions (sec)"].iloc[0]))

run = slowest["Run Time (sec)"].iloc[0]
st.write(
    f"**Run pace:** {pace_str(run / IRONMAN_RUN_MILES)} /mile  |  "
    f"{pace_str(run / IRONMAN_RUN_KM)} /km"
)

# SECTION:  worried about getting disqualified? -----------------------------

st.write("#### Minimum effort per discipline")
st.caption(
    "These are the **slowest split performances that still finished successfully**. "
    "Each value may come from a different athlete. "
    "This gives a realistic minimum target to aim for if your main goal is to finish."
)

if len(fin_df) == 0:
    st.info("No finishers found.")
else:
    results = []

    for label, col in [
        ("Swim", "Swim Time (sec)"),
        ("Bike", "Bike Time (sec)"),
        ("Run", "Run Time (sec)"),
        ("Transitions", "Transitions (sec)")
    ]:
        if col in fin_df.columns:
            row = fin_df.sort_values(col, ascending=False).head(1)
            results.append({
                "Discipline": label,
                "Slowest time that still finished": seconds_to_hhmmss(row[col].iloc[0]),
                "Athlete": row["Name"].iloc[0] if "Name" in row.columns else "",
                "Division": row["Division"].iloc[0] if "Division" in row.columns else "",
                "Country": row["Country"].iloc[0] if "Country" in row.columns else ""
            })

    out = pd.DataFrame(results)
    st.dataframe(out, use_container_width=True)

    st.caption(
        "Use this as a **confidence check**, not a training goal. "
        "Training close to these limits leaves little margin for heat, nutrition issues, or mechanical problems."
    )

st.divider()


# SECTION: Transitions vs Overall Time -----------------------------

st.write("### Do transitions matter?")
st.caption(
    "This plot shows whether longer transitions are associated with slower overall times. "
    "A weak relationship suggests transitions matter less than swim, bike, or run."
)

t = fin_df.dropna(subset=["Transitions (sec)", "Overall Time (sec)"])
if len(t) > 10:
    r = t["Transitions (sec)"].corr(t["Overall Time (sec)"])

    fig = plt.figure(figsize=(5.6, 3.0))
    plt.scatter(t["Transitions (sec)"] / 60, t["Overall Time (sec)"] / 3600, s=12)
    plt.xlabel("Transitions (minutes)")
    plt.ylabel("Overall Time (hours)")
    plt.title(f"Correlation = {r:.2f}")
    st.pyplot(fig, clear_figure=True)

st.divider()

# SECTION: Age group performance --------------------------------------------

st.write("### Does age matter?")

st.caption(
    "This section compares age groups based on median finishing time. "
    "Only age-based divisions are included."
)

# exclude PRO & PC/ID
age_df = fin_df[
    fin_df["Division"].astype(str).str.match(r"[MF]\d{2}-\d{2}")
].copy()

# get age group (remove gender letter)
age_df["Age Group"] = (
    age_df["Division"]
    .str.replace(r"[MF]", "", regex=True)
)

# Compute median overall time by age group
age_stats = (
    age_df
    .groupby("Age Group")["Overall Time (sec)"]
    .median()
    .dropna()
)

# Sort age groups numerically
age_stats = age_stats.sort_index(
    key=lambda x: x.str.extract(r"(\d+)").astype(int)[0]
)

# show best
best_age = age_stats.idxmin()
best_time = age_stats.min()

st.write(
    f"**Best performing age group:** **{best_age}** "
    f"(median time: {seconds_to_hhmmss(best_time)})"
)

# Plot
fig = plt.figure(figsize=(7, 3.2))
plt.bar(age_stats.index, age_stats.values / 3600)
plt.xticks(rotation=45, ha="right")
plt.ylabel("Median overall time (hours)")
plt.title("Median finishing time by age group")

# Highlight best age group
plt.bar(best_age, best_time / 3600, color="orange")

st.pyplot(fig, clear_figure=True)
