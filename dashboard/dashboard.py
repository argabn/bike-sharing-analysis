from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

BASE_DIR = Path(__file__).parent
DAY_TYPES = ["Hari Kerja", "Akhir Pekan/Libur"]
WEATHER_ORDER = ["Cerah", "Berkabut", "Hujan/Salju Ringan"]
SEASON_ORDER = ["Dingin", "Semi", "Panas", "Gugur"]
MONTH_ORDER = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
PALETTE = {"Hari Kerja": "#1f4e79", "Akhir Pekan/Libur": "#e07b00"}
PEAK_WINDOWS = {"Hari Kerja": [(0, 11), (12, 23)], "Akhir Pekan/Libur": [(0, 23)]}

st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")
sns.set_theme(style="white", font_scale=1.0)


@st.cache_data
def load_data():
    day_df = pd.read_csv(BASE_DIR / "day_clean.csv", parse_dates=["dteday"])
    hour_df = pd.read_csv(BASE_DIR / "main_data.csv", parse_dates=["dteday"])
    return day_df, hour_df


def filter_data(df, start_date, end_date, seasons):
    mask = df["dteday"].between(start_date, end_date) & df["season"].isin(seasons)
    return df[mask]


def plot_hourly_pattern(hour_df):
    hourly = hour_df.groupby(["hr", "day_type"])["cnt"].mean().reset_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=hourly, x="hr", y="cnt", hue="day_type", hue_order=DAY_TYPES,
                 palette=PALETTE, linewidth=3, ax=ax)
    for day_type, windows in PEAK_WINDOWS.items():
        subset = hourly[hourly["day_type"] == day_type]
        for start, end in windows:
            window = subset[subset["hr"].between(start, end)]
            if window.empty:
                continue
            peak = window.loc[window["cnt"].idxmax()]
            ax.scatter(peak["hr"], peak["cnt"], color=PALETTE[day_type], s=60, zorder=3)
            ax.annotate(f"{int(peak['hr']):02d}.00: {peak['cnt']:.0f}", (peak["hr"], peak["cnt"]),
                        textcoords="offset points", xytext=(0, 10), ha="center",
                        color=PALETTE[day_type], fontweight="bold")
    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels([f"{h:02d}.00" for h in range(0, 24, 2)])
    ax.set_xlabel("Jam")
    ax.set_ylabel("Rata-rata sewa per jam")
    ax.legend(title=None, frameon=False)
    sns.despine()
    fig.tight_layout()
    return fig, hourly


def summarize_drop(day_df, column, order):
    summary = day_df.groupby(column)["cnt"].mean().reindex(order).dropna().to_frame("rata_rata_sewa")
    summary["penurunan_pct"] = (1 - summary["rata_rata_sewa"] / summary["rata_rata_sewa"].max()) * 100
    return summary


def plot_drop_bars(ax, summary, title, xlabel):
    values = summary["rata_rata_sewa"]
    baseline = values.idxmax()
    worst = values.idxmin()
    colors = ["#1f4e79" if name == baseline else "#c0392b" if name == worst else "#9aa5b1"
              for name in values.index]
    bars = ax.bar(values.index, values.values, color=colors, width=0.65)
    for bar, name in zip(bars, values.index):
        label = f"{values[name]:,.0f}"
        if name != baseline:
            label += f"\n(-{summary.loc[name, 'penurunan_pct']:.1f}%)"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + values.max() * 0.015, label,
                ha="center", va="bottom", fontweight="bold")
    ax.set_ylim(0, values.max() * 1.2)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Rata-rata sewa harian")
    sns.despine(ax=ax)


def plot_weather_season(day_df):
    weather_summary = summarize_drop(day_df, "weathersit", WEATHER_ORDER)
    season_summary = summarize_drop(day_df, "season", SEASON_ORDER)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    plot_drop_bars(axes[0], weather_summary, "Rata-rata sewa per kondisi cuaca", "Kondisi cuaca")
    plot_drop_bars(axes[1], season_summary, "Rata-rata sewa per musim", "Musim")
    fig.tight_layout()
    return fig, weather_summary, season_summary


def compute_casual_share(day_df):
    monthly = day_df.groupby(["mnth", "day_type"])[["casual", "registered"]].sum()
    monthly["casual_pct"] = monthly["casual"] / (monthly["casual"] + monthly["registered"]) * 100
    return monthly["casual_pct"].unstack().reindex(MONTH_ORDER)


def plot_user_share(share):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for ax, day_type in zip(axes, DAY_TYPES):
        casual = share[day_type] if day_type in share else pd.Series(index=MONTH_ORDER, dtype=float)
        registered = 100 - casual
        ax.bar(MONTH_ORDER, registered, color="#1f4e79", label="Registered", width=0.7)
        ax.bar(MONTH_ORDER, casual, bottom=registered, color="#e07b00", label="Casual", width=0.7)
        for i, value in enumerate(casual):
            if pd.notna(value):
                ax.text(i, 102, f"{value:.0f}%", ha="center", color="#e07b00", fontweight="bold", fontsize=9)
        ax.set_ylim(0, 112)
        ax.set_title(day_type, loc="left", fontweight="bold")
        ax.set_xlabel("Bulan")
        ax.tick_params(axis="x", labelsize=8)
        sns.despine(ax=ax)
    axes[0].set_ylabel("Proporsi pengguna (%)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right", ncol=2, frameon=False)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    return fig


day_all, hour_all = load_data()

st.sidebar.header("Filter Data")
date_range = st.sidebar.date_input(
    "Rentang tanggal",
    value=(day_all["dteday"].min().date(), day_all["dteday"].max().date()),
    min_value=day_all["dteday"].min().date(),
    max_value=day_all["dteday"].max().date(),
)
selected_seasons = st.sidebar.multiselect("Musim", SEASON_ORDER, default=SEASON_ORDER)

if len(date_range) != 2:
    st.info("Pilih tanggal akhir pada filter rentang tanggal.")
    st.stop()
if not selected_seasons:
    st.warning("Pilih minimal satu musim.")
    st.stop()

start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
day_df = filter_data(day_all, start_date, end_date, selected_seasons)
hour_df = filter_data(hour_all, start_date, end_date, selected_seasons)

if day_df.empty:
    st.warning("Tidak ada data pada filter yang dipilih.")
    st.stop()

st.title("🚲 Dashboard Bike Sharing 2011-2012")
st.caption("Capital Bikeshare, Washington D.C. Gunakan filter di sidebar untuk mengubah periode dan musim.")

total_rentals = day_df["cnt"].sum()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sewa", f"{total_rentals:,.0f}")
col2.metric("Rata-rata Sewa Harian", f"{day_df['cnt'].mean():,.0f}")
col3.metric("Pengguna Casual", f"{day_df['casual'].sum() / total_rentals * 100:.1f}%")
col4.metric("Pengguna Registered", f"{day_df['registered'].sum() / total_rentals * 100:.1f}%")

st.subheader("1. Pola Penyewaan per Jam: Hari Kerja vs Akhir Pekan/Libur")
fig_hourly, hourly = plot_hourly_pattern(hour_df)
st.pyplot(fig_hourly)
peak_rows = hourly.loc[hourly.groupby("day_type")["cnt"].idxmax()]
st.caption(" | ".join(
    f"Puncak {row.day_type}: jam {int(row.hr):02d}.00 ({row.cnt:.0f} sewa)" for row in peak_rows.itertuples()
))

st.subheader("2. Pengaruh Cuaca dan Musim terhadap Penyewaan Harian")
fig_weather, weather_summary, season_summary = plot_weather_season(day_df)
st.pyplot(fig_weather)
st.caption("Persentase pada batang menunjukkan penurunan terhadap kategori dengan rata-rata sewa tertinggi pada filter yang dipilih.")

st.subheader("3. Proporsi Pengguna Casual vs Registered per Bulan")
share = compute_casual_share(day_df)
st.pyplot(plot_user_share(share))
st.caption("Angka oranye menunjukkan persentase pengguna casual pada bulan tersebut.")

with st.expander("Lihat data ringkasan"):
    st.write("Rata-rata sewa per jam")
    st.dataframe(hourly.pivot(index="hr", columns="day_type", values="cnt").round(1))
    st.write("Rata-rata sewa harian per cuaca")
    st.dataframe(weather_summary.round(1))
    st.write("Rata-rata sewa harian per musim")
    st.dataframe(season_summary.round(1))
