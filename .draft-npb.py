import random
import time
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="NPB ドラフトシミュレーター",
    page_icon="⚾",
    layout="centered"
)

# --- 1. スタイル定義（横スクロール対応 & コントラスト固定） ---
st.markdown("""<style>
/* ベース背景 */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #f6f5f1 !important;
    color: #111827 !important;
}

/* 見出しと通常テキスト固定 */
h1, h2, h3, h4, h5, h6,
.stMarkdown p, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span {
    color: #111827 !important;
}

/* プライマリボタン（赤） */
button[kind="primary"], button[data-testid="baseButton-primary"] {
    background-color: #a91e2c !important;
    border-color: #a91e2c !important;
}
button[kind="primary"] *, button[data-testid="baseButton-primary"] * {
    color: #ffffff !important;
    font-weight: 700 !important;
}

/* セカンダリボタン（白） */
button[kind="secondary"], button[data-testid="baseButton-secondary"] {
    background-color: #ffffff !important;
    border: 1px solid #d1d5db !important;
}
button[kind="secondary"] *, button[data-testid="baseButton-secondary"] * {
    color: #111827 !important;
    font-weight: 700 !important;
}

/* スライダー */
[data-testid="stSlider"] label, [data-testid="stSlider"] div {
    color: #111827 !important;
}

/* 上部カード */
.otc-container {
    background-color: #ffffff !important;
    border-radius: 16px !important;
    border-top: 5px solid #a91e2c !important;
    border-left: 1px solid #e5e0d8 !important;
    border-right: 1px solid #e5e0d8 !important;
    border-bottom: 1px solid #e5e0d8 !important;
    padding: 16px 20px !important;
    margin-bottom: 16px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
}
.otc-flex {
    display: flex !important;
    align-items: center !important;
    gap: 16px !important;
}
.otc-icon {
    background-color: #fdf2f2 !important;
    color: #a91e2c !important;
    border-radius: 12px !important;
    width: 48px !important;
    height: 48px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 24px !important;
    flex-shrink: 0 !important;
}
.otc-top-row {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    margin-bottom: 4px !important;
}
.otc-tag-title {
    color: #a91e2c !important;
    font-weight: 800 !important;
    font-size: 13px !important;
    letter-spacing: 0.5px !important;
}
.otc-pill-badge {
    background-color: #ffffff !important;
    border: 1px solid #dcd7ce !important;
    color: #4b5563 !important;
    font-size: 11px !important;
    padding: 2px 10px !important;
    border-radius: 20px !important;
    font-weight: 600 !important;
}
.otc-heading {
    color: #111827 !important;
    font-size: 18px !important;
    font-weight: 800 !important;
    margin: 0 !important;
    line-height: 1.3 !important;
}

/* ステータスバー */
.status-container {
    background-color: #172a3a !important;
    border-radius: 10px !important;
    padding: 14px 20px !important;
    margin-bottom: 16px !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
}
.status-left {
    display: flex !important;
    gap: 36px !important;
    align-items: center !important;
}
.status-label {
    font-size: 11px !important;
    letter-spacing: 1px !important;
    color: #8da2b5 !important;
    font-weight: 700 !important;
    margin-bottom: 2px !important;
}
.status-value {
    font-size: 24px !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    line-height: 1 !important;
}

/* 12球団 全指名ボード */
.board-header {
    background-color: #172a3a !important;
    color: #ffffff !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 10px 16px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    font-weight: 700 !important;
    font-size: 14px !important;
}
.board-header * {
    color: #ffffff !important;
}

/* 横スクロールラッパー */
.table-scroll-container {
    width: 100% !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    border-left: 1px solid #e5e0d8 !important;
    border-right: 1px solid #e5e0d8 !important;
    border-bottom: 1px solid #e5e0d8 !important;
    border-radius: 0 0 8px 8px !important;
    background: #ffffff !important;
    margin-bottom: 16px !important;
}

.board-table {
    width: 100% !important;
    border-collapse: collapse !important;
    background: #ffffff !important;
}
.board-table th {
    background-color: #ede9e1 !important;
    color: #374151 !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    padding: 9px 12px !important;
    text-align: left !important;
    border-bottom: 1px solid #ded9ce !important;
    white-space: nowrap !important;
}
.board-table td {
    padding: 10px 12px !important;
    font-size: 13px !important;
    color: #111827 !important;
    border-bottom: 1px solid #f2eee6 !important;
    background-color: #ffffff !important;
    vertical-align: middle !important;
    white-space: nowrap !important;
}
.board-table tr.user-row td {
    background-color: #fbf5e6 !important;
}
.board-table tr.user-row td.team-col {
    color: #b45309 !important;
    font-weight: 800 !important;
}
.team-name {
    font-weight: 700 !important;
    color: #111827 !important;
}
.team-cnt {
    color: #6b7280 !important;
    font-size: 11px !important;
    padding-left: 6px !important;
    font-weight: normal !important;
}
.val-empty {
    color: #c5c0b5 !important;
}
.val-picked {
    font-weight: 700 !important;
    color: #111827 !important;
    display: block !important;
}
.val-temp {
    font-weight: 700 !important;
    color: #2563eb !important;
    display: block !important;
}
.val-sub {
    font-size: 10.5px !important;
    color: #6b7280 !important;
    font-weight: normal !important;
    display: block !important;
    margin-top: 1px !important;
}

.card-competing {
    background-color: #fefce8 !important;
    border: 1.5px solid #facc15 !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    margin-bottom: 10px !important;
    color: #854d0e !important;
    font-weight: 800 !important;
    font-size: 14.5px !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
}
.card-single {
    background-color: #f0fdf4 !important;
    border: 1.5px solid #86efac !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    margin-bottom: 10px !important;
    color: #166534 !important;
    font-weight: 800 !important;
    font-size: 14.5px !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
}
</style>""", unsafe_allow_html=True)

# --- 2. 12球団の最新初期設定プリセットデータ ---
INITIAL_PRESETS = {
    "阪神": {
        "高投": 1.0, "高捕": 1.05, "高内": 1.2, "高外": 1.05,
        "大投": 1.2, "大捕": 1.4, "大内": 1.2, "大外": 1.05,
        "社投": 0.9, "社捕": 1.0, "社内": 1.05, "社外": 0.85,
        "独投": 0.95, "独捕": 1.1, "独内": 1.0, "独外": 0.85, "他": 1.0
    },
    "DeNA": {
        "高投": 1.25, "高捕": 0.95, "高内": 1.05, "高外": 1.1,
        "大投": 1.25, "大捕": 0.9, "大内": 1.0, "大外": 1.1,
        "社投": 0.95, "社捕": 1.0, "社内": 1.05, "社外": 1.1,
        "独投": 0.9, "独捕": 0.8, "独内": 0.9, "独外": 0.85, "他": 1.0
    },
    "巨人": {
        "高投": 1.2, "高捕": 0.95, "高内": 1.0, "高外": 1.1,
        "大投": 1.2, "大捕": 0.85, "大内": 1.1, "大外": 1.25,
        "社投": 1.05, "社捕": 0.8, "社内": 1.0, "社外": 1.1,
        "独投": 0.85, "独捕": 0.7, "独内": 0.8, "独外": 0.9, "他": 1.0
    },
    "中日": {
        "高投": 1.1, "高捕": 1.05, "高内": 1.05, "高外": 1.1,
        "大投": 1.3, "大捕": 0.8, "大内": 0.95, "大外": 1.2,
        "社投": 1.1, "社捕": 0.6, "社内": 0.9, "社外": 1.1,
        "独投": 1.0, "独捕": 0.8, "独内": 0.8, "独外": 1.0, "他": 1.0
    },
    "広島": {
        "高投": 0.85, "高捕": 1.0, "高内": 1.0, "高外": 0.95,
        "大投": 1.28, "大捕": 1.3, "大内": 1.15, "大外": 1.2,
        "社投": 1.0, "社捕": 1.05, "社内": 1.0, "社外": 1.15,
        "独投": 0.9, "独捕": 0.9, "独内": 1.0, "独外": 1.05, "他": 1.0
    },
    "ヤクルト": {
        "高投": 1.05, "高捕": 0.9, "高内": 1.2, "高外": 1.2,
        "大投": 1.35, "大捕": 0.9, "大内": 1.15, "大外": 1.15,
        "社投": 1.2, "社捕": 0.7, "社内": 1.05, "社外": 1.1,
        "独投": 1.0, "独捕": 0.6, "独内": 0.85, "独外": 0.95, "他": 1.0
    },
    "ソフトバンク": {
        "高投": 1.3, "高捕": 1.05, "高内": 1.1, "高外": 1.1,
        "大投": 1.1, "大捕": 0.8, "大内": 0.8, "大外": 0.95,
        "社投": 0.8, "社捕": 0.75, "社内": 0.75, "社外": 0.8,
        "独投": 0.95, "独捕": 0.7, "独内": 0.7, "独外": 0.8, "他": 1.0
    },
    "日本ハム": {
        "高投": 1.15, "高捕": 1.1, "高内": 1.0, "高外": 1.0,
        "大投": 1.25, "大捕": 0.9, "大内": 1.15, "大外": 1.1,
        "社投": 1.0, "社捕": 0.85, "社内": 1.0, "社外": 1.0,
        "独投": 0.9, "独捕": 0.8, "独内": 1.0, "独外": 1.0, "他": 1.0
    },
    "オリックス": {
        "高投": 1.25, "高捕": 1.0, "高内": 1.1, "高外": 1.1,
        "大投": 1.25, "大捕": 1.1, "大内": 1.0, "大外": 1.0,
        "社投": 1.15, "社捕": 0.8, "社内": 0.9, "社外": 0.9,
        "独投": 1.1, "独捕": 0.7, "独内": 0.8, "独外": 0.85, "他": 1.0
    },
    "楽天": {
        "高投": 1.15, "高捕": 1.0, "高内": 1.2, "高外": 1.1,
        "大投": 1.2, "大捕": 0.85, "大内": 1.1, "大外": 1.05,
        "社投": 1.1, "社捕": 0.85, "社内": 1.05, "社外": 1.0,
        "独投": 1.05, "独捕": 0.8, "独内": 0.9, "独外": 0.85, "他": 1.0
    },
    "西武": {
        "高投": 1.3, "高捕": 0.9, "高内": 1.1, "高外": 1.15,
        "大投": 1.2, "大捕": 0.8, "大内": 1.05, "大外": 1.05,
        "社投": 1.1, "社捕": 0.8, "社内": 1.0, "社外": 1.0,
        "独投": 1.05, "独捕": 0.7, "独内": 0.8, "独外": 0.9, "他": 1.0
    },
    "ロッテ": {
        "高投": 1.2, "高捕": 1.05, "高内": 1.1, "高外": 1.1,
        "大投": 1.2, "大捕": 0.9, "大内": 0.85, "大外": 1.0,
        "社投": 0.95, "社捕": 0.85, "社内": 1.0, "社外": 0.8,
        "独投": 1.0, "独捕": 0.75, "独内": 0.85, "独外": 0.85, "他": 1.0
    }
}

# --- 3. データ読み込み ---
SHEET_ID = "1Qd_GNT-V0Ololma_QpIAhgEzLSFXlsv8sMG99espI90"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=60)
def load_data(url):
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"データ読み込みエラー: {e}")
        return None

df_raw = load_data(csv_url)

if df_raw is not None:
    npb_teams = list(INITIAL_PRESETS.keys())

    if "current_screen" not in st.session_state:
        st.session_state.current_screen = "設定画面"

    if "user_team" not in st.session_state:
        st.session_state.user_team = "阪神"

    if "max_rounds" not in st.session_state:
        st.session_state.max_rounds = 7

    if "sim_speed" not in st.session_state:
        st.session_state.sim_speed = "標準"

    if "team_weights" not in st.session_state:
        st.session_state.team_weights = {
            t: dict(INITIAL_PRESETS[t]) for t in npb_teams
        }

    # ドラフト進行管理ステート
    if "draft_phase" not in st.session_state:
        st.session_state.draft_phase = "r1_input"
        st.session_state.draft_picks = {t: {} for t in npb_teams}
        st.session_state.already_drafted = set()
        
        st.session_state.r1_sub_round = 1
        st.session_state.r1_active_teams = list(npb_teams)
        st.session_state.r1_current_bids = {}
        st.session_state.r1_competitions = {}
        
        st.session_state.r1_reveal_order = []
        st.session_state.r1_reveal_idx = 0
        st.session_state.r1_revealed_bids = {}
        
        st.session_state.current_round = 2
        st.session_state.weber_index = 0

    df = df_raw.copy()

    def get_main_pos(pos_str):
        p = str(pos_str)
        if "投" in p:
            return "投"
        elif "捕" in p:
            return "捕"
        elif "内" in p:
            return "内"
        elif "外" in p:
            return "外"
        return "他"

    def get_cat(row):
        kbn = str(row["区分"])
        if "高" in kbn:
            pfx = "高"
        elif "大" in kbn:
            pfx = "大"
        elif "独立" in kbn or "独" in kbn:
            pfx = "独"
        elif any(x in kbn for x in ["社", "社会人", "クラブ"]):
            pfx = "社"
        else:
            pfx = "他"

        sfx = get_main_pos(row["守備位置"])
        return pfx + sfx

    df["メイン守備"] = df["守備位置"].apply(get_main_pos)
    df["カテゴリ"] = df.apply(get_cat, axis=1)
score_dict = {
    "S": 97,
    "A+": 93,
    "A": 89,
    "A-": 83,
    "B+": 80,
    "B": 73,
    "B-": 69,
    "C+": 64,
    "C": 58,
    "C-": 55,
}


def parse_score(val):
  s = str(val).strip()
  # まず数値（整数・小数）に変換できるか試す
  try:
    return float(s)
  except ValueError:
    # 数値でなければアルファベット換算辞書を参照
    return float(score_dict.get(s, 50.0))


df["基礎スコア"] = df["評価"].apply(parse_score)

    player_dict = {}
    for _, r in df.iterrows():
        name = str(r["氏名"]).strip()
        player_dict[name] = {
            "team": str(r.get("学校・チーム", "")).strip(),
            "pos": str(r.get("守備位置", "")).strip(),
            "main_pos": str(r.get("メイン守備", "他")).strip(),
            "kbn": str(r.get("区分", "")).strip(),
            "cat": str(r.get("カテゴリ", "他")).strip(),
            "rank": str(r.get("評価", "")).strip(),
            "base_score": float(r.get("基礎スコア", 50))
        }

    def format_player_label(name):
        info = player_dict.get(name)
        if info:
            team_str = f"{info['team']}・" if info['team'] else ""
            return f"{name}（{team_str}{info['pos']}）"
        return name

    # 思考方針アルゴリズム（10点以内6:4、重複回避7:3、2位以下7:3、ポジションバランス、4位以降独立1.1倍）
    def pick_ai_player(team_name, pool_df, round_num=1):
        if len(pool_df) == 0:
            return None
        
        target_pool = pool_df.copy()
        
        if round_num <= 2:
            b_plus_cands = target_pool[target_pool["基礎スコア"] >= 80]
            if len(b_plus_cands) > 0:
                target_pool = b_plus_cands

        w = st.session_state.team_weights[team_name]
        
        already_positions = set()
        if round_num >= 3:
            for r in range(1, round_num):
                picked_p = st.session_state.draft_picks[team_name].get(r)
                if picked_p and picked_p in player_dict:
                    already_positions.add(player_dict[picked_p]["main_pos"])

        def calc_score(row):
            base = row["基礎スコア"] * w.get(row["カテゴリ"], 1.0)
            
            # 3位以降：ポジションバランス（未指名ポジションなら1.05倍）
            if round_num >= 3:
                if row["メイン守備"] in ["投", "捕", "内", "外"] and (row["メイン守備"] not in already_positions):
                    base *= 1.05
                    
            # 4位以降：独立リーグ選手なら1.1倍
            if round_num >= 4:
                if str(row["カテゴリ"]).startswith("独") or ("独" in str(row["区分"])):
                    base *= 1.10
                    
            return base

        target_pool["score"] = target_pool.apply(calc_score, axis=1)
        target_pool = target_pool.sort_values(by="score", ascending=False).reset_index(drop=True)

        top_player = target_pool.iloc[0]["氏名"]
        max_score = target_pool.iloc[0]["score"]

        # 1位指名
        if round_num == 1:
            cands_within_10 = target_pool[(target_pool["score"] >= max_score - 10.0) & (target_pool["氏名"] != top_player)]

            if len(cands_within_10) > 0:
                if random.random() < 0.60:
                    return top_player
                else:
                    return cands_within_10.sample(n=1).iloc[0]["氏名"]
            else:
                if len(target_pool) >= 2:
                    highest_base = pool_df["基礎スコア"].max()
                    top_base = target_pool.iloc[0]["基礎スコア"]
                    
                    if top_base >= highest_base:
                        runner_up = target_pool.iloc[1]["氏名"]
                        if random.random() < 0.30:
                            return runner_up
                return top_player
        # 2位以下
        else:
            sub_cands = target_pool.iloc[1:8]
            if len(sub_cands) > 0:
                if random.random() < 0.70:
                    return top_player
                else:
                    return sub_cands.sample(n=1).iloc[0]["氏名"]
            else:
                return top_player

    speed_map = {
        "じっくり": 2.2,
        "標準": 1.4,
        "高速": 0.6,
        "自分まで": 0.05
    }

    # サイドバー切り替え
    screen_choice = st.sidebar.radio(
        "画面切り替え",
        ["⚙️ 初期設定", "🏟️ ドラフト会場"],
        index=0 if st.session_state.current_screen == "設定画面" else 1
    )
    st.session_state.current_screen = "設定画面" if screen_choice == "⚙️ 初期設定" else "ドラフト会場"

    # =========================================================================
    # 画面1: 初期設定画面
    # =========================================================================
    if st.session_state.current_screen == "設定画面":
        st.markdown("## ⚙️ ドラフト初期設定")
        st.write("操作球団、指名人数、各球団の好みを設定します。")

        # 1. 担当球団の選択
        st.markdown("### 1. 操作する球団を選ぶ")
        selected_user_team = st.selectbox(
            "あなたの担当球団",
            npb_teams,
            index=npb_teams.index(st.session_state.user_team)
        )
        st.session_state.user_team = selected_user_team

        # 2. 指名枠数
        st.markdown("### 2. 指名枠数（巡数）の設定")
        st.session_state.max_rounds = st.slider(
            "各球団の最大指名人数（巡数）",
            min_value=1,
            max_value=10,
            value=st.session_state.max_rounds,
            step=1
        )
        st.caption(f"※ 各球団【最大 {st.session_state.max_rounds} 名】まで指名を行います。")

        st.divider()

        # 3. 12球団の係数設定（プルダウンでスライダーの表示/非表示を切り替え）
        st.markdown("### 3. 各球団のカテゴリ別係数設定")
        
        slider_mode = st.selectbox(
            "球団係数の設定方法",
            ["初期プリセットのまま使用する（推奨）", "手動で調整・確認する"],
            index=0,
            key="slider_mode_select"
        )

        if slider_mode == "手動で調整・確認する":
            edit_team = st.selectbox(
                "係数を調整する球団を選択",
                npb_teams,
                index=npb_teams.index(st.session_state.user_team),
                key="tune_team_select"
            )
            
            st.write(f"**{edit_team} の補正係数** （スライダーで微調整可能）")
            w = st.session_state.team_weights[edit_team]
            
            st.caption("高校生")
            c1, c2, c3, c4 = st.columns(4)
            w["高投"] = c1.slider("高投", 0.0, 2.0, float(w.get("高投", 1.0)), 0.01, key=f"s_{edit_team}_高投")
            w["高捕"] = c2.slider("高捕", 0.0, 2.0, float(w.get("高捕", 1.0)), 0.01, key=f"s_{edit_team}_高捕")
            w["高内"] = c3.slider("高内", 0.0, 2.0, float(w.get("高内", 1.0)), 0.01, key=f"s_{edit_team}_高内")
            w["高外"] = c4.slider("高外", 0.0, 2.0, float(w.get("高外", 1.0)), 0.01, key=f"s_{edit_team}_高外")

            st.caption("大学生")
            c5, c6, c7, c8 = st.columns(4)
            w["大投"] = c5.slider("大投", 0.0, 2.0, float(w.get("大投", 1.0)), 0.01, key=f"s_{edit_team}_大投")
            w["大捕"] = c6.slider("大捕", 0.0, 2.0, float(w.get("大捕", 1.0)), 0.01, key=f"s_{edit_team}_大捕")
            w["大内"] = c7.slider("大内", 0.0, 2.0, float(w.get("大内", 1.0)), 0.01, key=f"s_{edit_team}_大内")
            w["大外"] = c8.slider("大外", 0.0, 2.0, float(w.get("大外", 1.0)), 0.01, key=f"s_{edit_team}_大外")

            st.caption("社会人")
            c9, c10, c11, c12 = st.columns(4)
            w["社投"] = c9.slider("社投", 0.0, 2.0, float(w.get("社投", 1.0)), 0.01, key=f"s_{edit_team}_社投")
            w["社捕"] = c10.slider("社捕", 0.0, 2.0, float(w.get("社捕", 1.0)), 0.01, key=f"s_{edit_team}_社捕")
            w["社内"] = c11.slider("社内", 0.0, 2.0, float(w.get("社内", 1.0)), 0.01, key=f"s_{edit_team}_社内")
            w["社外"] = c12.slider("社外", 0.0, 2.0, float(w.get("社外", 1.0)), 0.01, key=f"s_{edit_team}_社外")

            st.caption("独立リーグ")
            c13, c14, c15, c16 = st.columns(4)
            w["独投"] = c13.slider("独投", 0.0, 2.0, float(w.get("独投", 1.0)), 0.01, key=f"s_{edit_team}_独投")
            w["独捕"] = c14.slider("独捕", 0.0, 2.0, float(w.get("独捕", 1.0)), 0.01, key=f"s_{edit_team}_独捕")
            w["独内"] = c15.slider("独内", 0.0, 2.0, float(w.get("独内", 1.0)), 0.01, key=f"s_{edit_team}_独内")
            w["独外"] = c16.slider("独外", 0.0, 2.0, float(w.get("独外", 1.0)), 0.01, key=f"s_{edit_team}_独外")
        else:
            st.caption("✅ 全12球団の初期設定プリセットが適用されています。")

        st.write("")
        if st.button("🏟️ この設定でドラフト会議会場へ進む", type="primary", use_container_width=True):
            st.session_state.current_screen = "ドラフト会場"
            st.rerun()

    # =========================================================================
    # 画面2: ドラフト会議会場
    # =========================================================================
    elif st.session_state.current_screen == "ドラフト会場":
        user_team = st.session_state.user_team
        phase = st.session_state.draft_phase
        max_r = st.session_state.max_rounds
        s_rnd = st.session_state.r1_sub_round

        if s_rnd == 1:
            r1_title = "1位・第1回入札"
        elif s_rnd == 2:
            r1_title = "外れ1位入札"
        else:
            r1_title = f"{'外れ' * (s_rnd - 1)}1位入札"

        if phase == "r1_input":
            header_badge = r1_title
            if user_team in st.session_state.r1_active_teams:
                header_msg = f"{r1_title}。{user_team}の候補を選んでください"
            else:
                header_msg = f"{r1_title}。他球団の入札を開始します"
        elif phase == "r1_reveal_bids":
            header_badge = f"{r1_title}・開票中"
            header_msg = f"下の球団から順番に{r1_title}選手を開票中……"
        elif phase == "r1_confirm_bids":
            header_badge = f"{r1_title}・開票完了"
            header_msg = f"{r1_title}の結果が出揃いました。抽選を行ってください"
        elif phase == "round_progress":
            c_rnd = st.session_state.current_round
            header_badge = f"{c_rnd}位指名進行中"
            header_msg = f"{c_rnd}巡目の指名をウェーバー順に行っています"
        else:
            header_badge = "ドラフト終了"
            header_msg = "全日程の指名が終了しました"

        # --- A. ON THE CLOCK バナー ---
        st.markdown(f"""<div class="otc-container">
<div class="otc-flex">
<div class="otc-icon">✦</div>
<div>
<div class="otc-top-row">
<span class="otc-tag-title">ON THE CLOCK</span>
<span class="otc-pill-badge">{header_badge}</span>
</div>
<div class="otc-heading">{header_msg}</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

        # --- B. ステータスバー ---
        speed_opts = ["じっくり", "標準", "高速", "自分まで"]
        selected_speed = st.radio(
            "⏱ 進行速度",
            speed_opts,
            index=speed_opts.index(st.session_state.sim_speed),
            horizontal=True,
            key="speed_selector"
        )
        st.session_state.sim_speed = selected_speed

        picked_count = len(st.session_state.draft_picks[user_team])
        st.markdown(f"""<div class="status-container">
<div class="status-left">
<div>
<div class="status-label">YOUR TEAM</div>
<div class="status-value">{user_team}</div>
</div>
<div>
<div class="status-label">SELECTED</div>
<div class="status-value">{picked_count} / {max_r}</div>
</div>
</div>
<div>
<div class="status-label" style="margin-bottom: 4px;">⏱ 現在のフェーズ</div>
<div style="font-size:14px; font-weight:800; color:#eab308;">
{"1位指名 入札・開票・抽選中" if "r1" in phase else (f"第{st.session_state.current_round}巡目 進行中" if phase == "round_progress" else "全日程終了")}
</div>
</div>
</div>""", unsafe_allow_html=True)

        # --- C. 12球団・全指名ボード（横スクロール） ---
        st.markdown(f"""<div class="board-header">
<div>👁 12球団・全指名ボード</div>
<div style="color: #f87171; font-size: 11px; font-weight: 800;"><span style="display:inline-block; width:8px; height:8px; background:#ef4444; border-radius:50%; margin-right:4px;"></span>LIVE</div>
</div>""", unsafe_allow_html=True)

        th_cols = "".join([f"<th style='min-width: 140px;'>{r}位</th>" for r in range(1, max_r + 1)])

        table_rows = []
        for t in npb_teams:
            is_u = (t == user_team)
            tr_class = ' class="user-row"' if is_u else ""
            t_picks = st.session_state.draft_picks[t]
            cnt = len(t_picks)

            cells_html = ""
            for r in range(1, max_r + 1):
                p_name = t_picks.get(r)
                
                if r == 1 and not p_name and t in st.session_state.r1_revealed_bids:
                    temp_p = st.session_state.r1_revealed_bids[t]
                    info = player_dict.get(temp_p, {})
                    t_sub = f"{info.get('team', '')}・{info.get('pos', '')}" if info else ""
                    cells_html += f"<td><span class='val-temp'>入札: {temp_p}</span><span class='val-sub'>{t_sub}</span></td>"
                elif p_name:
                    info = player_dict.get(p_name, {})
                    t_sub = f"{info.get('team', '')}・{info.get('pos', '')}" if info else ""
                    cells_html += f"<td><span class='val-picked'>{p_name}</span><span class='val-sub'>{t_sub}</span></td>"
                else:
                    cells_html += "<td><span class='val-empty'>—</span></td>"

            row_html = f"""<tr{tr_class}>
<td class="team-col" style="min-width: 110px; position: sticky; left: 0; z-index: 1;">
<span class="team-name">{t}</span>
<span class="team-cnt">{cnt}/{max_r}</span>
</td>
{cells_html}
</tr>"""
            table_rows.append(row_html)

        all_rows = "\n".join(table_rows)

        st.markdown(f"""<div class="table-scroll-container">
<table class="board-table">
<thead>
<tr>
<th style="min-width: 110px; position: sticky; left: 0; z-index: 2;">球団</th>
{th_cols}
</tr>
</thead>
<tbody>
{all_rows}
</tbody>
</table>
</div>""", unsafe_allow_html=True)

        # --- D. 操作・進行コントロール ---
        avail_pool = df[~df["氏名"].isin(st.session_state.already_drafted)]
        sorted_pool = avail_pool.sort_values(by="基礎スコア", ascending=False)
        all_kbns = ["すべて"] + sorted(list(df["区分"].dropna().unique()))
        all_poss = ["すべて"] + sorted(list(df["守備位置"].dropna().unique()))

        # ----------------------------------------------------
        # 1位指名フェーズ
        # ----------------------------------------------------
        if phase == "r1_input":
            st.markdown(f"#### 🎯 {r1_title}（未確定: {len(st.session_state.r1_active_teams)}球団）")

            if user_team in st.session_state.r1_active_teams:
                col_f1, col_f2 = st.columns(2)
                sel_kbn = col_f1.selectbox("区分で絞り込み", all_kbns, key=f"f_kbn_r1_{s_rnd}")
                sel_pos = col_f2.selectbox("守備位置で絞り込み", all_poss, key=f"f_pos_r1_{s_rnd}")

                filtered_pool = sorted_pool.copy()
                if sel_kbn != "すべて":
                    filtered_pool = filtered_pool[filtered_pool["区分"] == sel_kbn]
                if sel_pos != "すべて":
                    filtered_pool = filtered_pool[filtered_pool["守備位置"] == sel_pos]

                if len(filtered_pool) == 0:
                    st.warning("条件に該当する選手がいません。条件を変更してください。")
                else:
                    user_pick = st.selectbox(
                        f"{user_team}の{r1_title}選手を選択",
                        filtered_pool["氏名"].tolist(),
                        format_func=format_player_label,
                        key=f"sel_r1_{s_rnd}"
                    )

                    if st.button(f"この選手を{r1_title}する（下の球団から開票へ）", type="primary", use_container_width=True):
                        bids = {user_team: user_pick}
                        for t in st.session_state.r1_active_teams:
                            if t == user_team:
                                continue
                            bids[t] = pick_ai_player(t, avail_pool, round_num=1)

                        st.session_state.r1_current_bids = bids
                        st.session_state.r1_reveal_order = list(reversed(st.session_state.r1_active_teams))
                        st.session_state.r1_reveal_idx = 0
                        st.session_state.r1_revealed_bids = {}
                        st.session_state.draft_phase = "r1_reveal_bids"
                        st.rerun()
            else:
                st.info(f"{user_team}は1位指名獲得済みです。未確定球団による{r1_title}の開票を開始します。")
                if st.button(f"{r1_title}の開票を開始する（下の球団から）", type="primary", use_container_width=True):
                    bids = {}
                    for t in st.session_state.r1_active_teams:
                        bids[t] = pick_ai_player(t, avail_pool, round_num=1)

                    st.session_state.r1_current_bids = bids
                    st.session_state.r1_reveal_order = list(reversed(st.session_state.r1_active_teams))
                    st.session_state.r1_reveal_idx = 0
                    st.session_state.r1_revealed_bids = {}
                    st.session_state.draft_phase = "r1_reveal_bids"
                    st.rerun()

        # 1位の順次開票フェーズ（下の球団から順に開票アナウンス）
        elif phase == "r1_reveal_bids":
            reveal_order = st.session_state.r1_reveal_order
            r_idx = st.session_state.r1_reveal_idx

            if r_idx < len(reveal_order):
                now_team = reveal_order[r_idx]
                p_choice = st.session_state.r1_current_bids[now_team]
                p_label = format_player_label(p_choice)

                st.info(f"🎙️ 第1回選択希望選手…… **{now_team}** ： **{p_label}**")
                
                st.session_state.r1_revealed_bids[now_team] = p_choice
                delay = speed_map.get(st.session_state.sim_speed, 1.4)
                time.sleep(delay)

                st.session_state.r1_reveal_idx += 1
                st.rerun()
            else:
                bids = st.session_state.r1_current_bids
                p_bids = {}
                for t, p in bids.items():
                    p_bids.setdefault(p, []).append(t)

                st.session_state.r1_competitions = p_bids
                st.session_state.draft_phase = "r1_confirm_bids"
                st.rerun()

        # 1位の抽選フェーズ
        elif phase == "r1_confirm_bids":
            st.markdown(f"#### 📢 {r1_title}の開票結果一覧")

            for p, teams in st.session_state.r1_competitions.items():
                p_label = format_player_label(p)
                if len(teams) > 1:
                    t_str = "、".join(teams)
                    st.markdown(f"""<div class="card-competing">
<span>🔥</span>
<div><strong>{p_label}</strong> に {len(teams)}球団が競合！（{t_str}）</div>
</div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class="card-single">
<span>✅</span>
<div><strong>{p_label}</strong>: {teams[0]} が単独指名！</div>
</div>""", unsafe_allow_html=True)

            if st.button("🎲 抽選（くじ引き）を行い結果を確定する", type="primary", use_container_width=True):
                next_losers = []

                for p, teams in st.session_state.r1_competitions.items():
                    if len(teams) == 1:
                        w_team = teams[0]
                        st.session_state.draft_picks[w_team][1] = p
                        st.session_state.already_drafted.add(p)
                    else:
                        winner = random.choice(teams)
                        st.session_state.draft_picks[winner][1] = p
                        st.session_state.already_drafted.add(p)
                        for loser in teams:
                            if loser != winner:
                                next_losers.append(loser)

                st.session_state.r1_revealed_bids = {}

                if len(next_losers) > 0:
                    st.session_state.r1_active_teams = next_losers
                    st.session_state.r1_sub_round += 1
                    st.session_state.draft_phase = "r1_input"
                else:
                    st.session_state.r1_active_teams = []
                    if max_r >= 2:
                        st.session_state.draft_phase = "round_progress"
                        st.session_state.current_round = 2
                        st.session_state.weber_index = 0
                    else:
                        st.session_state.draft_phase = "finished"
                st.rerun()

        # ----------------------------------------------------
        # 2巡目以降（ウェーバー自動シーケンス進行）
        # ----------------------------------------------------
        elif phase == "round_progress":
            c_rnd = st.session_state.current_round
            order = list(reversed(npb_teams)) if c_rnd % 2 == 0 else npb_teams
            w_idx = st.session_state.weber_index

            if w_idx < len(order):
                now_team = order[w_idx]

                if now_team == user_team:
                    st.markdown(f"#### 🎯 選択権： **{now_team}（あなた）** （第{c_rnd}巡目 第{w_idx+1}指名）")
                    rem_pool = df[~df["氏名"].isin(st.session_state.already_drafted)]
                    sorted_rem = rem_pool.sort_values(by="基礎スコア", ascending=False)

                    col_f1, col_f2 = st.columns(2)
                    sel_kbn = col_f1.selectbox("区分で絞り込み", all_kbns, key=f"f_kbn_{c_rnd}_{w_idx}")
                    sel_pos = col_f2.selectbox("守備位置で絞り込み", all_poss, key=f"f_pos_{c_rnd}_{w_idx}")

                    filtered_rem = sorted_rem.copy()
                    if sel_kbn != "すべて":
                        filtered_rem = filtered_rem[filtered_rem["区分"] == sel_kbn]
                    if sel_pos != "すべて":
                        filtered_rem = filtered_rem[filtered_rem["守備位置"] == sel_pos]

                    if len(filtered_rem) == 0:
                        st.warning("条件に該当する指名可能な選手がいません。条件を変更してください。")
                    else:
                        u_choice = st.selectbox(
                            f"{user_team}の第{c_rnd}位指名選手を選択",
                            filtered_rem["氏名"].tolist(),
                            format_func=format_player_label,
                            key=f"rnd_pick_{c_rnd}_{w_idx}"
                        )
                        if st.button("この選手を指名する", type="primary", use_container_width=True):
                            st.session_state.draft_picks[user_team][c_rnd] = u_choice
                            st.session_state.already_drafted.add(u_choice)
                            st.session_state.weber_index += 1
                            st.rerun()

                else:
                    delay = speed_map.get(st.session_state.sim_speed, 1.4)
                    
                    rem_pool = df[~df["氏名"].isin(st.session_state.already_drafted)]
                    ch = pick_ai_player(now_team, rem_pool, round_num=c_rnd)
                    ch_label = format_player_label(ch)

                    st.info(f"🎙️ 第{c_rnd}巡目 第{w_idx+1}指名: **{now_team}** …… **{ch_label}**")
                    time.sleep(delay)

                    st.session_state.draft_picks[now_team][c_rnd] = ch
                    st.session_state.already_drafted.add(ch)
                    st.session_state.weber_index += 1
                    st.rerun()

            else:
                st.success(f"🎉 第{c_rnd}巡目の指名がすべて終了しました！")
                if c_rnd < max_r:
                    if st.button(f"➡️ 第{c_rnd+1}巡目の指名を開始する", type="primary", use_container_width=True):
                        st.session_state.current_round += 1
                        st.session_state.weber_index = 0
                        st.rerun()
                else:
                    st.balloons()
                    st.success("🏆 全指名枠のドラフト会議がすべて終了しました！")

        elif phase == "finished":
            st.balloons()
            st.success("🏆 全日程のドラフト会議が終了しました！お疲れ様でした！")

        st.write("---")
        if st.button("⚙️ 設定画面に戻る（最初からやり直す）", use_container_width=True):
            st.session_state.current_screen = "設定画面"
            st.session_state.draft_phase = "r1_input"
            st.session_state.draft_picks = {t: {} for t in npb_teams}
            st.session_state.already_drafted = set()
            st.session_state.r1_sub_round = 1
            st.session_state.r1_active_teams = list(npb_teams)
            st.session_state.r1_current_bids = {}
            st.session_state.r1_competitions = {}
            st.session_state.r1_reveal_order = []
            st.session_state.r1_reveal_idx = 0
            st.session_state.r1_revealed_bids = {}
            st.rerun()
