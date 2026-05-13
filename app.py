# ============================================================
# NETFLIX TOP 500 MOVIES 2025-2026 - DASHBOARD STREAMLIT
# Visualisasi Data Premium | Python + Pandas + Plotly + Streamlit
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import os

# ─────────────────────────────────────────────
# KONFIGURASI HALAMAN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Netflix Top 500 Movies Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS KUSTOM UNTUK TAMPILAN PREMIUM
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .main-header {
        background: linear-gradient(135deg, #E50914 0%, #831010 50%, #1a1a2e 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(229,9,20,0.3);
    }
    .main-header h1 { color: white; font-size: 2.4rem; font-weight: 700; margin: 0 0 0.3rem 0; }
    .main-header p  { color: rgba(255,255,255,0.82); font-size: 1rem; margin: 0; }

    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid rgba(229,9,20,0.25);
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-3px); }
    .metric-label {
        color: rgba(255,255,255,0.6); font-size: 0.78rem; font-weight: 500;
        text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;
    }
    .metric-value { color: #E50914; font-size: 2rem; font-weight: 700; margin-bottom: 0.2rem; }
    .metric-sub   { color: rgba(255,255,255,0.45); font-size: 0.75rem; }

    .section-title {
        color: white; font-size: 1.05rem; font-weight: 600;
        margin: 1.2rem 0 0.6rem 0;
        border-left: 4px solid #E50914; padding-left: 0.7rem;
    }
    .chart-caption {
        color: rgba(255,255,255,0.5); font-size: 0.78rem;
        margin: -0.3rem 0 0.8rem 0.7rem; font-style: italic;
    }

    .footer {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid rgba(229,9,20,0.2);
        border-radius: 12px; padding: 1.2rem; text-align: center;
        color: rgba(255,255,255,0.5); font-size: 0.8rem; margin-top: 2rem;
    }
    .footer span { color: #E50914; }

    .insight-box {
        background: linear-gradient(135deg, #16213e, #0f3460);
        border: 1px solid rgba(229,9,20,0.3);
        border-radius: 12px; padding: 1.2rem 1.6rem; margin-bottom: 1rem;
    }
    .insight-box h4 { color: #E50914; margin: 0 0 0.5rem 0; font-size: 0.95rem; }
    .insight-box p  { color: rgba(255,255,255,0.8); margin: 0; font-size: 0.88rem; line-height: 1.6; }

    .filter-info {
        background: rgba(229,9,20,0.1); border: 1px solid rgba(229,9,20,0.3);
        border-radius: 8px; padding: 0.6rem 1rem; margin-bottom: 1rem;
        color: rgba(255,255,255,0.8); font-size: 0.82rem;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD DATA — path relatif aman pakai __file__
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Coba di folder 'data/' dulu, lalu di folder yang sama
    for path in [
        os.path.join(base_dir, "data", "netflix_top500_global_movies_2025_2026.csv"),
        os.path.join(base_dir, "netflix_top500_global_movies_2025_2026.csv"),
    ]:
        if os.path.exists(path):
            df = pd.read_csv(path)
            df["first_appeared"]      = pd.to_datetime(df["first_appeared"], errors="coerce")
            df["last_appeared"]       = pd.to_datetime(df["last_appeared"],  errors="coerce")
            df["total_hours_viewed_M"] = df["total_hours_viewed"] / 1_000_000
            return df
    raise FileNotFoundError("CSV tidak ditemukan")

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ File `netflix_top500_global_movies_2025_2026.csv` tidak ditemukan. "
             "Taruh file CSV di folder `data/` atau di folder yang sama dengan `app.py`.")
    st.stop()

# Konstanta data (tidak berubah oleh filter)
TOTAL_DATA      = len(df)               # 500
MAX_RANK_GLOBAL = int(df["best_rank"].max())   # 10
MIN_WEEKS_DATA  = int(df["weeks_in_top10"].min())  # 1
MAX_WEEKS_DATA  = int(df["weeks_in_top10"].max())  # 41

# ─────────────────────────────────────────────
# HEADER UTAMA
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🎬 Netflix Top 500 Global Movies</h1>
    <p>Dashboard Visualisasi Data Interaktif · 2025 – 2026</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR FILTER
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Filter & Pencarian")
    st.markdown("---")

    # ── Filter 1: Jumlah top N film (default = SEMUA = 500) ──────
    top_n = st.slider(
        "📊 Tampilkan Top N Film",
        min_value=10,
        max_value=TOTAL_DATA,        # 500
        value=TOTAL_DATA,            # ← FIX: default 500 bukan 50
        step=10,
        help="Pilih berapa film teratas berdasarkan overall rank yang ingin ditampilkan"
    )

    # ── Filter 2: Minimal weeks in top 10 (default = 1 = semua) ──
    min_weeks = st.slider(
        "📅 Minimal Weeks in Top 10",
        min_value=MIN_WEEKS_DATA,
        max_value=MAX_WEEKS_DATA,
        value=MIN_WEEKS_DATA,        # default = 1 (tampilkan semua)
        step=1,
        help="Hanya tampilkan film yang bertahan minimal sekian minggu di Top 10"
    )

    # ── Filter 3: Range best rank ─────────────────────────────────
    rank_min, rank_max = st.select_slider(
        "🏆 Range Best Rank",
        options=list(range(1, MAX_RANK_GLOBAL + 1)),
        value=(1, MAX_RANK_GLOBAL),  # default semua rank (1-10)
        help="Filter berdasarkan best rank terbaik yang pernah dicapai film"
    )

    # ── Filter 4: Pencarian judul ─────────────────────────────────
    search_query = st.text_input(
        "🔍 Cari Judul Film",
        placeholder="Contoh: Happy Gilmore...",
        help="Pencarian tidak case-sensitive"
    )

    st.markdown("---")

    st.markdown(
        "<small style='color:rgba(255,255,255,0.4)'>Dataset: Netflix Global Top 10 · 2025–2026<br>"
        f"Total data: {TOTAL_DATA} film</small>",
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────
# FILTERING DATA — urutan aman, semua kondisi dicek
# ─────────────────────────────────────────────
filtered_df = df.copy()

# Step 1: Ambil top N berdasarkan overall_rank (1 s/d top_n)
filtered_df = filtered_df[filtered_df["overall_rank"] <= top_n]

# Step 2: Filter minimal minggu di top 10
filtered_df = filtered_df[filtered_df["weeks_in_top10"] >= min_weeks]

# Step 3: Filter range best rank
filtered_df = filtered_df[
    (filtered_df["best_rank"] >= rank_min) &
    (filtered_df["best_rank"] <= rank_max)
]

# Step 4: Pencarian judul (case-insensitive, strip spasi)
if search_query.strip():
    filtered_df = filtered_df[
        filtered_df["movie_title"].str.contains(
            search_query.strip(), case=False, na=False
        )
    ]

# Reset index setelah filter
filtered_df = filtered_df.reset_index(drop=True)

# ─────────────────────────────────────────────
# INFO FILTER AKTIF
# ─────────────────────────────────────────────
active_filters = []
if top_n < TOTAL_DATA:
    active_filters.append(f"Top {top_n} film")
if min_weeks > MIN_WEEKS_DATA:
    active_filters.append(f"Weeks ≥ {min_weeks}")
if (rank_min, rank_max) != (1, MAX_RANK_GLOBAL):
    active_filters.append(f"Rank #{rank_min}–#{rank_max}")
if search_query.strip():
    active_filters.append(f'Judul mengandung "{search_query.strip()}"')

if active_filters:
    st.markdown(
        f'<div class="filter-info">🔎 Filter aktif: {" · ".join(active_filters)} '
        f'→ menampilkan <strong>{len(filtered_df)}</strong> dari <strong>{TOTAL_DATA}</strong> film</div>',
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────
# METRIC CARDS
# ─────────────────────────────────────────────
st.markdown('<p class="section-title">📌 Ringkasan Data</p>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

if not filtered_df.empty:
    total_movies  = len(filtered_df)
    total_hours   = filtered_df["total_hours_viewed"].sum()
    avg_best_rank = filtered_df["best_rank"].mean()
    avg_weeks     = filtered_df["weeks_in_top10"].mean()
    max_hours_film = filtered_df.loc[filtered_df["total_hours_viewed"].idxmax(), "movie_title"]

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🎬 Total Film</div>
            <div class="metric-value">{total_movies:,}</div>
            <div class="metric-sub">dari {TOTAL_DATA} total film</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        if total_hours >= 1_000_000_000:
            hours_disp = f"{total_hours/1e9:.2f}B"
            hours_sub  = "miliar jam tayang"
        else:
            hours_disp = f"{total_hours/1e6:.1f}M"
            hours_sub  = "juta jam tayang"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⏱️ Total Jam Tayang</div>
            <div class="metric-value">{hours_disp}</div>
            <div class="metric-sub">{hours_sub}</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🏅 Rata-rata Best Rank</div>
            <div class="metric-value">#{avg_best_rank:.1f}</div>
            <div class="metric-sub">dari skala 1–10</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📆 Rata-rata Weeks Top 10</div>
            <div class="metric-value">{avg_weeks:.1f}</div>
            <div class="metric-sub">minggu rata-rata</div>
        </div>""", unsafe_allow_html=True)
else:
    st.warning("⚠️ Tidak ada data yang cocok dengan filter yang dipilih. Coba ubah filter di sidebar.")

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TEMA WARNA PLOTLY
# ─────────────────────────────────────────────
TPL      = "plotly_dark"
C_RED    = "#E50914"
C_SEQ    = px.colors.sequential.Reds_r
C_PAL    = ["#E50914","#FF6B6B","#FF8E8E","#FFB3B3","#FFD6D6",
            "#C0392B","#922B21","#641E16","#4A0E0E","#2D0606"]
LAYOUT   = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=35, b=10),
    font=dict(family="Inter, sans-serif", size=12),
)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_viz, tab_data, tab_insight = st.tabs([
    "📊  Visualisasi",
    "📋  Dataset",
    "💡  Insight",
])

# ══════════════════════════════════════════════
# TAB 1 — VISUALISASI (diperbaiki & diperjelas)
# ══════════════════════════════════════════════
with tab_viz:
    if filtered_df.empty:
        st.warning("⚠️ Data kosong setelah filter diterapkan. Tidak ada grafik yang dapat ditampilkan. "
                   "Coba ubah atau reset filter di sidebar.")
    else:
        # ════════════════════════════════════════
        # BARIS 1: Bar Chart Top 20 Film
        # ════════════════════════════════════════
        st.markdown('<p class="section-title">🎬 Top 20 Film dengan Jam Tayang Terbanyak</p>',
                    unsafe_allow_html=True)
        st.markdown('<p class="chart-caption">Membandingkan film-film paling banyak ditonton '
                    'berdasarkan total jam tayang (dalam juta jam)</p>', unsafe_allow_html=True)
        try:
            bar_df = (filtered_df
                      .sort_values("total_hours_viewed", ascending=False)
                      .head(20)
                      .copy())
            # Potong judul agar tidak terlalu panjang di chart
            bar_df["judul_pendek"] = bar_df["movie_title"].apply(
                lambda x: x if len(x) <= 30 else x[:28] + "…"
            )
            bar_df["label_hover"] = (
                bar_df["movie_title"] + "<br>" +
                "Jam Tayang: " + bar_df["total_hours_viewed_M"].apply(lambda x: f"{x:,.1f}") + " juta jam<br>" +
                "Best Rank: #" + bar_df["best_rank"].astype(str) + "<br>" +
                "Weeks Top 10: " + bar_df["weeks_in_top10"].astype(str) + " minggu"
            )

            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=bar_df["total_hours_viewed_M"],
                y=bar_df["judul_pendek"],
                orientation="h",
                text=bar_df["total_hours_viewed_M"].apply(lambda x: f"{x:,.0f} jt"),
                textposition="outside",
                textfont=dict(size=11, color="white"),
                hovertext=bar_df["label_hover"],
                hoverinfo="text",
                marker=dict(
                    color=bar_df["total_hours_viewed_M"],
                    colorscale="Reds",
                    showscale=True,
                    colorbar=dict(title="Juta Jam", thickness=12, len=0.8),
                    line=dict(color="rgba(0,0,0,0)"),
                ),
            ))
            fig_bar.update_layout(
                **LAYOUT,
                height=520,
                template=TPL,
                xaxis=dict(title="Total Jam Tayang (Juta Jam)", showgrid=True,
                           gridcolor="rgba(255,255,255,0.07)"),
                yaxis=dict(autorange="reversed", title="", tickfont=dict(size=11)),
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        except Exception as e:
            st.error(f"Bar chart gagal: {e}")

        st.markdown("---")

        # ════════════════════════════════════════
        # BARIS 2: Line Chart + Pie Chart
        # ════════════════════════════════════════
        col_line, col_pie = st.columns([3, 2])

        # ── Line Chart: Tren jam tayang per bulan ────────────────
        with col_line:
            st.markdown('<p class="section-title">📈 Tren Kumulatif Jam Tayang per Bulan</p>',
                        unsafe_allow_html=True)
            st.markdown('<p class="chart-caption">Jumlah total jam tayang film yang pertama kali muncul '
                        'di Top 10 setiap bulan</p>', unsafe_allow_html=True)
            try:
                trend_df = (filtered_df
                            .dropna(subset=["first_appeared"])
                            .sort_values("first_appeared")
                            .copy())
                trend_df["bulan"] = trend_df["first_appeared"].dt.to_period("M").astype(str)
                trend_agg = (trend_df.groupby("bulan")
                             .agg(total_jam=("total_hours_viewed_M", "sum"),
                                  jumlah_film=("movie_title", "count"))
                             .reset_index())

                if trend_agg.empty or len(trend_agg) < 2:
                    st.info("ℹ️ Data tidak cukup untuk menampilkan tren bulan.")
                else:
                    fig_line = go.Figure()
                    # Area fill
                    fig_line.add_trace(go.Scatter(
                        x=trend_agg["bulan"],
                        y=trend_agg["total_jam"],
                        mode="lines+markers",
                        name="Total Jam Tayang",
                        line=dict(color=C_RED, width=2.5),
                        marker=dict(color=C_RED, size=7, line=dict(color="white", width=1.5)),
                        fill="tozeroy",
                        fillcolor="rgba(229,9,20,0.12)",
                        hovertemplate=(
                            "<b>%{x}</b><br>"
                            "Total Jam: %{y:,.1f} juta jam<br>"
                            "<extra></extra>"
                        ),
                    ))
                    fig_line.update_layout(
                        **LAYOUT,
                        height=380,
                        template=TPL,
                        xaxis=dict(title="Bulan", tickangle=-40,
                                   showgrid=False, tickfont=dict(size=10)),
                        yaxis=dict(title="Jam Tayang (Juta Jam)",
                                   showgrid=True, gridcolor="rgba(255,255,255,0.07)"),
                        showlegend=False,
                    )
                    st.plotly_chart(fig_line, use_container_width=True)
            except Exception as e:
                st.error(f"Line chart gagal: {e}")

        # ── Pie Chart: Distribusi Best Rank ──────────────────────
        with col_pie:
            st.markdown('<p class="section-title">🥧 Distribusi Best Rank</p>',
                        unsafe_allow_html=True)
            st.markdown('<p class="chart-caption">Seberapa banyak film yang pernah '
                        'mencapai setiap rank teratas</p>', unsafe_allow_html=True)
            try:
                rank_count = (filtered_df["best_rank"]
                              .value_counts()
                              .sort_index()
                              .reset_index())
                rank_count.columns = ["best_rank", "jumlah"]
                rank_count["label"] = "Rank #" + rank_count["best_rank"].astype(str)

                fig_pie = go.Figure(go.Pie(
                    labels=rank_count["label"],
                    values=rank_count["jumlah"],
                    hole=0.45,
                    marker=dict(colors=C_PAL,
                                line=dict(color="#1a1a2e", width=2)),
                    textinfo="label+percent",
                    textposition="outside",
                    hovertemplate="<b>%{label}</b><br>Jumlah Film: %{value}<br>Persentase: %{percent}<extra></extra>",
                    pull=[0.06 if i == 0 else 0 for i in range(len(rank_count))],
                ))
                fig_pie.update_layout(
                    **LAYOUT,
                    height=380,
                    template=TPL,
                    showlegend=False,
                    annotations=[dict(
                        text=f"<b>{len(filtered_df)}</b><br>Film",
                        x=0.5, y=0.5, font_size=14, showarrow=False,
                        font=dict(color="white"),
                    )],
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            except Exception as e:
                st.error(f"Pie chart gagal: {e}")

        st.markdown("---")

        # ════════════════════════════════════════
        # BARIS 3: Scatter Plot (full width)
        # ════════════════════════════════════════
        st.markdown('<p class="section-title">🔵 Hubungan Weeks in Top 10 vs Total Jam Tayang</p>',
                    unsafe_allow_html=True)
        st.markdown('<p class="chart-caption">Setiap titik mewakili satu film. '
                    'Ukuran titik = total jam tayang. Warna = best rank yang dicapai. '
                    'Hover untuk detail lengkap.</p>', unsafe_allow_html=True)
        try:
            fig_sc = px.scatter(
                filtered_df,
                x="weeks_in_top10",
                y="total_hours_viewed_M",
                color="best_rank",
                size="total_hours_viewed_M",
                size_max=40,
                hover_name="movie_title",
                hover_data={
                    "best_rank":             ":.0f",
                    "weeks_in_top10":        ":.0f",
                    "total_hours_viewed_M":  ":.1f",
                    "overall_rank":          ":.0f",
                },
                color_continuous_scale="Reds_r",
                labels={
                    "weeks_in_top10":       "Minggu di Top 10",
                    "total_hours_viewed_M": "Jam Tayang (Juta Jam)",
                    "best_rank":            "Best Rank",
                    "overall_rank":         "Overall Rank",
                },
                template=TPL,
            )
            fig_sc.update_layout(
                **LAYOUT,
                height=430,
                coloraxis_colorbar=dict(title="Best Rank", thickness=12, len=0.7),
                xaxis=dict(title="Berapa Minggu Film Bertahan di Top 10",
                           showgrid=True, gridcolor="rgba(255,255,255,0.07)"),
                yaxis=dict(title="Total Jam Tayang (Juta Jam)",
                           showgrid=True, gridcolor="rgba(255,255,255,0.07)"),
            )
            st.plotly_chart(fig_sc, use_container_width=True)
        except Exception as e:
            st.error(f"Scatter plot gagal: {e}")

        st.markdown("---")

        # ════════════════════════════════════════
        # BARIS 4: Box Plot + Histogram
        # ════════════════════════════════════════
        col_box, col_hist = st.columns(2)

        with col_box:
            st.markdown('<p class="section-title">📦 Sebaran Jam Tayang per Best Rank</p>',
                        unsafe_allow_html=True)
            st.markdown('<p class="chart-caption">Box plot menunjukkan median, '
                        'Q1–Q3, dan outlier untuk setiap rank</p>', unsafe_allow_html=True)
            try:
                fig_box = px.box(
                    filtered_df,
                    x="best_rank",
                    y="total_hours_viewed_M",
                    color_discrete_sequence=[C_RED],
                    labels={"best_rank":            "Best Rank",
                            "total_hours_viewed_M": "Jam Tayang (Juta Jam)"},
                    template=TPL,
                    points="outliers",
                )
                fig_box.update_traces(
                    marker=dict(color=C_RED, size=4, opacity=0.7),
                    line=dict(color=C_RED),
                )
                fig_box.update_layout(
                    **LAYOUT,
                    height=370,
                    xaxis=dict(title="Best Rank yang Pernah Dicapai",
                               showgrid=False),
                    yaxis=dict(title="Jam Tayang (Juta Jam)",
                               showgrid=True, gridcolor="rgba(255,255,255,0.07)"),
                )
                st.plotly_chart(fig_box, use_container_width=True)
            except Exception as e:
                st.error(f"Box plot gagal: {e}")

        with col_hist:
            st.markdown('<p class="section-title">📊 Distribusi Weeks in Top 10</p>',
                        unsafe_allow_html=True)
            st.markdown('<p class="chart-caption">Seberapa banyak film yang bertahan '
                        '1 minggu, 2 minggu, dst di Top 10</p>', unsafe_allow_html=True)
            try:
                fig_hist = px.histogram(
                    filtered_df,
                    x="weeks_in_top10",
                    nbins=min(30, int(filtered_df["weeks_in_top10"].max())),
                    color_discrete_sequence=[C_RED],
                    labels={"weeks_in_top10": "Weeks in Top 10",
                            "count":          "Jumlah Film"},
                    template=TPL,
                )
                fig_hist.update_traces(
                    marker_line_color="rgba(0,0,0,0.3)",
                    marker_line_width=0.5,
                )
                fig_hist.update_layout(
                    **LAYOUT,
                    height=370,
                    bargap=0.08,
                    xaxis=dict(title="Jumlah Minggu Bertahan di Top 10"),
                    yaxis=dict(title="Jumlah Film",
                               showgrid=True, gridcolor="rgba(255,255,255,0.07)"),
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            except Exception as e:
                st.error(f"Histogram gagal: {e}")

# ══════════════════════════════════════════════
# TAB 2 — DATASET
# ══════════════════════════════════════════════
with tab_data:
    st.markdown('<p class="section-title">📋 Tabel Data Film Netflix</p>', unsafe_allow_html=True)

    if filtered_df.empty:
        st.warning("⚠️ Tidak ada data yang cocok dengan filter yang dipilih.")
    else:
        display_df = filtered_df[[
            "overall_rank", "movie_title", "total_hours_viewed",
            "weeks_in_top10", "best_rank", "first_appeared", "last_appeared"
        ]].copy()
        display_df.columns = [
            "Rank", "Judul Film", "Total Jam Tayang",
            "Weeks Top 10", "Best Rank", "Pertama Muncul", "Terakhir Muncul"
        ]
        display_df["Pertama Muncul"]  = pd.to_datetime(display_df["Pertama Muncul"]).dt.strftime("%d %b %Y")
        display_df["Terakhir Muncul"] = pd.to_datetime(display_df["Terakhir Muncul"]).dt.strftime("%d %b %Y")
        display_df["Total Jam Tayang"] = display_df["Total Jam Tayang"].apply(lambda x: f"{x:,.0f}")

        st.dataframe(display_df, use_container_width=True, height=500, hide_index=True)
        st.markdown(f"**Total baris ditampilkan:** {len(display_df):,} film")

        st.markdown('<p class="section-title">⬇️ Unduh Data</p>', unsafe_allow_html=True)
        csv_buf = io.StringIO()
        filtered_df.to_csv(csv_buf, index=False)
        st.download_button(
            label="📥 Download Data Terfilter (.csv)",
            data=csv_buf.getvalue(),
            file_name="netflix_filtered_data.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ══════════════════════════════════════════════
# TAB 3 — INSIGHT OTOMATIS
# ══════════════════════════════════════════════
with tab_insight:
    st.markdown('<p class="section-title">💡 Insight Otomatis Berdasarkan Data Terfilter</p>',
                unsafe_allow_html=True)

    if filtered_df.empty:
        st.warning("⚠️ Tidak ada data untuk dianalisis. Ubah filter di sidebar.")
    else:
        top_movie  = filtered_df.loc[filtered_df["total_hours_viewed"].idxmax()]
        longest    = filtered_df.loc[filtered_df["weeks_in_top10"].idxmax()]
        most_rank  = filtered_df["best_rank"].mode()[0]
        rank_pct   = (filtered_df["best_rank"] == most_rank).sum() / len(filtered_df) * 100

        st.markdown(f"""
        <div class="insight-box">
            <h4>🏆 Film Paling Banyak Ditonton</h4>
            <p><strong>{top_movie['movie_title']}</strong> memimpin dengan total
            <strong>{top_movie['total_hours_viewed']/1e6:,.1f} juta jam tayang</strong>.
            Film ini mencapai best rank #{int(top_movie['best_rank'])} dan bertahan
            <strong>{int(top_movie['weeks_in_top10'])} minggu</strong> di Top 10.</p>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-box">
            <h4>📅 Film Paling Lama di Top 10</h4>
            <p><strong>{longest['movie_title']}</strong> adalah film paling tahan lama,
            bertahan selama <strong>{int(longest['weeks_in_top10'])} minggu</strong> di Top 10.
            Total jam tayangnya <strong>{longest['total_hours_viewed']/1e6:,.1f} juta jam</strong>
            dengan best rank #{int(longest['best_rank'])}.</p>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-box">
            <h4>🥇 Best Rank yang Paling Sering Dicapai</h4>
            <p>Sebanyak <strong>{rank_pct:.1f}%</strong> film dalam data ini pernah mencapai
            <strong>Rank #{int(most_rank)}</strong> — menjadikannya posisi paling kompetitif
            di antara {len(filtered_df)} film yang ditampilkan.</p>
        </div>""", unsafe_allow_html=True)

        avg_by_rank = (filtered_df.groupby("best_rank")["total_hours_viewed_M"]
                       .mean().reset_index())
        best_r = avg_by_rank.loc[avg_by_rank["total_hours_viewed_M"].idxmax()]
        st.markdown(f"""
        <div class="insight-box">
            <h4>📊 Rank dengan Rata-rata Jam Tayang Tertinggi</h4>
            <p>Film yang mencapai Best Rank <strong>#{int(best_r['best_rank'])}</strong>
            rata-rata menghasilkan <strong>{best_r['total_hours_viewed_M']:,.1f} juta jam tayang</strong>
            — tertinggi dibandingkan rank lainnya dalam data terfilter ini.</p>
        </div>""", unsafe_allow_html=True)

        try:
            corr = filtered_df[["weeks_in_top10", "total_hours_viewed"]].corr().iloc[0, 1]
            corr_label = "positif kuat" if corr > 0.6 else ("positif sedang" if corr > 0.3 else
                         ("positif lemah" if corr > 0 else "negatif / tidak berkorelasi"))
            st.markdown(f"""
            <div class="insight-box">
                <h4>🔗 Korelasi: Minggu di Top 10 vs Jam Tayang</h4>
                <p>Nilai korelasi antara <strong>weeks in top 10</strong> dan
                <strong>total jam tayang</strong> adalah <strong>{corr:.2f}</strong> ({corr_label}).
                {"Artinya: film yang lebih lama bertahan di Top 10 cenderung menghasilkan lebih banyak jam tayang." if corr > 0.3 else "Tidak ada hubungan kuat antara durasi di Top 10 dan jumlah jam tayang."}</p>
            </div>""", unsafe_allow_html=True)
        except Exception:
            pass

        st.markdown('<p class="section-title">📊 Rata-rata Jam Tayang per Best Rank</p>',
                    unsafe_allow_html=True)
        try:
            if not avg_by_rank.empty:
                fig_rank = px.bar(
                    avg_by_rank,
                    x="best_rank",
                    y="total_hours_viewed_M",
                    color="total_hours_viewed_M",
                    color_continuous_scale="Reds",
                    text=avg_by_rank["total_hours_viewed_M"].apply(lambda x: f"{x:,.0f}"),
                    labels={"best_rank":            "Best Rank",
                            "total_hours_viewed_M": "Rata-rata Jam Tayang (Juta)"},
                    template=TPL,
                )
                fig_rank.update_traces(textposition="outside", textfont=dict(size=10, color="white"))
                fig_rank.update_layout(
                    **LAYOUT,
                    height=320,
                    coloraxis_showscale=False,
                    xaxis=dict(title="Best Rank", dtick=1),
                    yaxis=dict(title="Rata-rata Jam Tayang (Juta)"),
                )
                st.plotly_chart(fig_rank, use_container_width=True)
        except Exception as e:
            st.error(f"Grafik insight gagal: {e}")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class="footer">
    🎬 <strong>Netflix Top 500 Global Movies Dashboard</strong> · 2025–2026 <br>
</div>
""", unsafe_allow_html=True)