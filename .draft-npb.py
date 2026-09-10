import random
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="NPB ドラフトシミュレーター", page_icon="⚾", layout="centered"
)

# --- 1. スタイル定義（ダークモードによる白文字化を全滅させる強力CSS） ---
st.markdown(
    """<style>
/* ページ全体：背景と基本文字色の強制固定 */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #f6f5f1 !important;
    color: #111827 !important;
}

/* すべての見出し・テキスト・ラベル・Markdownの文字色を強制的に濃い色に */
h1, h2, h3, h4, h5, h6,
p, span, label, div,
.stMarkdown, [data-testid="stMarkdownContainer"] p,
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span {
    color: #111827 !important;
}

/* スライダーの数字やラベルの視認性確保 */
[data-testid="stSlider"] label,
[data-testid="stSlider"] div {
    color: #111827 !important;
}

/* タブの未選択テキストもグレーで読めるように */
button[data-baseweb="tab"] div {
    color: #4b5563 !important;
    font-weight: 700 !important;
}
button[data-baseweb="tab"][aria-selected="true"] div {
    color: #a91e2c !important;
    font-weight: 800 !important;
}

/* Streamlit標準アラートの文字色 */
div[data-testid="stAlert"] * {
    color: #111827 !important;
    font-weight: 700 !important;
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

/* ステータスバー（ネイビー部分は白文字を維持） */
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
.speed-box {
    display: flex !important;
    gap: 4px !important;
    background: rgba(255,255,255,0.08) !important;
    padding: 3px !important;
    border-radius: 6px !important;
}
.speed-item {
    padding: 3px 8px !important;
    font-size: 12px !important;
    color: #8da2b5 !important;
}
.speed-item.active {
    background: #eab308 !important;
    color: #172a3a !important;
    font-weight: 700 !important;
    border-radius: 4px !important;
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
.board-table {
    width: 100% !important;
    border-collapse: collapse !important;
    background: #ffffff !important;
    border-left: 1px solid #e5e0d8 !important;
    border-right: 1px solid #e5e0d8 !important;
    border-bottom: 1px solid #e5e0d8 !important;
    border-radius: 0 0 8px 8px !important;
    overflow: hidden !important;
}
.board-table th {
    background-color: #ede9e1 !important;
    color: #374151 !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    padding: 9px 14px !important;
    text-align: left !important;
    border-bottom: 1px solid #ded9ce !important;
}
.board-table td {
    padding: 10px 14px !important;
    font-size: 13.5px !important;
    color: #111827 !important;
    border-bottom: 1px solid #f2eee6 !important;
    background-color: #ffffff !important;
}
.board-table tr.user-row td {
    background-color: #fbf5e6 !important;
}
.board-table tr.user-row td.team-name {
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
    padding-left: 8px !important;
    font-weight: normal !important;
}
.val-empty {
    color: #c5c0b5 !important;
}
.val-picked {
    font-weight: 700 !important;
    color: #111827 !important;
}

.card-competing {
    background-color: #fefce8 !important;
    border: 1.5px solid #facc15 !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    margin-bottom: 10px !important;
    color: #854d0e !important;
    font-weight: 800 !important;
    font-size: 15px !important;
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
    font-size: 15px !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
}
</style>""",
    unsafe_allow_html=True,
)

# --- 2. データ読み込み ---
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
  npb_teams = [
      "阪神",
      "DeNA",
      "巨人",
      "中日",
      "広島",
      "ヤクルト",
      "ソフトバンク",
      "日本ハム",
      "オリックス",
      "楽天",
      "西武",
      "ロッテ",
  ]
  categories = [
      "高投",
      "高捕",
      "高内",
      "高外",
      "大投",
      "大捕",
      "大内",
      "大外",
      "社投",
      "社捕",
      "社内",
      "社外",
      "他",
  ]

  # セッション初期化（初期画面は設定画面）
  if "current_screen" not in st.session_state:
    st.session_state.current_screen = "設定画面"

  if "user_team" not in st.session_state:
    st.session_state.user_team = "阪神"

  if "max_rounds" not in st.session_state:
    st.session_state.max_rounds = 7

  if "team_weights" not in st.session_state:
    st.session_state.team_weights = {
        t: {cat: 1.0 for cat in categories} for t in npb_teams
    }

  if "draft_phase" not in st.session_state:
    st.session_state.draft_phase = "r1_input"
    st.session_state.draft_picks = {t: {} for t in npb_teams}
    st.session_state.already_drafted = set()
    st.session_state.r1_bids = {}
    st.session_state.r1_competing = {}
    st.session_state.loser_teams = []
    st.session_state.current_round = 1
    st.session_state.weber_index = 0

  df = df_raw.copy()


  def get_cat(row):
    kbn, pos = str(row["区分"]), str(row["守備位置"])
    pfx = (
        "高"
        if "高" in kbn
        else (
            "大"
            if "大" in kbn
            else (
                "社"
                if any(x in kbn for x in ["社", "独立", "クラブ"])
                else "他"
            )
        )
    )
    sfx = (
        "投"
        if "投" in pos
        else (
            "捕"
            if "捕" in pos
            else "内" if "内" in pos else "外" if "外" in pos else "他"
        )
    )
    key = pfx + sfx
    return key if key in categories else "他"


  df["カテゴリ"] = df.apply(get_cat, axis=1)

  score_dict = {
      "S": 97,
      "A": 85,
      "A-": 79,
      "B+": 74,
      "B": 70,
      "B-": 66,
      "C+": 60,
      "C": 55,
      "C-": 50,
  }
  df["基礎スコア"] = (
      df["評価"].astype(str).str.strip().map(score_dict).fillna(45)
  )

  # サイドバー画面切替
  screen_choice = st.sidebar.radio(
      "画面切り替え",
      ["⚙️ 初期設定", "🏟️ ドラフト会場"],
      index=0 if st.session_state.current_screen == "設定画面" else 1,
  )
  st.session_state.current_screen = (
      "設定画面" if screen_choice == "⚙️ 初期設定" else "ドラフト会場"
  )

  # =========================================================================
  # 画面1: 初期設定画面
  # =========================================================================
  if st.session_state.current_screen == "設定画面":
    st.markdown("## ⚙️ ドラフト初期設定")
    st.write(
        "操作する球団、全体の指名巡数（人数枠）、全球団の評価係数を手動で設定します。"
    )

    # 1. 担当球団の選択
    st.markdown("### 1. 操作する球団を選ぶ")
    user_cols = st.columns(6)
    for i, t in enumerate(npb_teams):
      with user_cols[i % 6]:
        is_sel = st.session_state.user_team == t
        if st.button(
            t,
            key=f"btn_team_{t}",
            use_container_width=True,
            type="primary" if is_sel else "secondary",
        ):
          st.session_state.user_team = t
          st.rerun()

    st.info(f"現在の担当球団: **{st.session_state.user_team}**")

    # 2. 指名枠数
    st.markdown("### 2. 指名枠数（巡数）の設定")
    st.session_state.max_rounds = st.slider(
        "各球団の最大指名人数（巡数）",
        min_value=1,
        max_value=10,
        value=st.session_state.max_rounds,
        step=1,
    )
    st.caption(
        f"※ 今回のシミュレーションでは各球団【{st.session_state.max_rounds}名】まで指名を行います。"
    )

    st.divider()

    # 3. 12球団の係数設定
    st.markdown("### 3. 各球団のカテゴリ別係数設定")
    st.write(
        "各球団が好むカテゴリ（高投、大内、社外など）の係数を手動で設定してください。"
    )

    t_tabs = st.tabs(npb_teams)
    for i, t in enumerate(npb_teams):
      with t_tabs[i]:
        st.write(f"**{t} の補正係数**")
        w = st.session_state.team_weights[t]

        c1, c2, c3, c4 = st.columns(4)
        w["高投"] = c1.slider("高投", 0.0, 2.0, w["高投"], 0.1, key=f"s_{t}_高投")
        w["高捕"] = c2.slider("高捕", 0.0, 2.0, w["高捕"], 0.1, key=f"s_{t}_高捕")
        w["高内"] = c3.slider("高内", 0.0, 2.0, w["高内"], 0.1, key=f"s_{t}_高内")
        w["高外"] = c4.slider("高外", 0.0, 2.0, w["高外"], 0.1, key=f"s_{t}_高外")

        c5, c6, c7, c8 = st.columns(4)
        w["大投"] = c5.slider("大投", 0.0, 2.0, w["大投"], 0.1, key=f"s_{t}_大投")
        w["大捕"] = c6.slider("大捕", 0.0, 2.0, w["大捕"], 0.1, key=f"s_{t}_大捕")
        w["大内"] = c7.slider("大内", 0.0, 2.0, w["大内"], 0.1, key=f"s_{t}_大内")
        w["大外"] = c8.slider("大外", 0.0, 2.0, w["大外"], 0.1, key=f"s_{t}_大外")

        c9, c10, c11, c12 = st.columns(4)
        w["社投"] = c9.slider("社投", 0.0, 2.0, w["社投"], 0.1, key=f"s_{t}_社投")
        w["社捕"] = c10.slider(
            "社捕", 0.0, 2.0, w["社捕"], 0.1, key=f"s_{t}_社捕"
        )
        w["社内"] = c11.slider(
            "社内", 0.0, 2.0, w["社内"], 0.1, key=f"s_{t}_社内"
        )
        w["社外"] = c12.slider(
            "社外", 0.0, 2.0, w["社外"], 0.1, key=f"s_{t}_社外"
        )

    st.write("")
    if st.button(
        "🏟️ この設定でドラフト会議会場へ進む",
        type="primary",
        use_container_width=True,
    ):
      st.session_state.current_screen = "ドラフト会場"
      st.rerun()

  # =========================================================================
  # 画面2: ドラフト会議会場
  # =========================================================================
  elif st.session_state.current_screen == "ドラフト会場":
    user_team = st.session_state.user_team
    phase = st.session_state.draft_phase
    max_r = st.session_state.max_rounds

    if phase == "r1_input":
      header_badge = "1位・第1回入札"
      header_msg = f"1位・第1回入札。{user_team}の候補を選んでください"
    elif phase == "r1_confirm_bids":
      header_badge = "1位・入札確定"
      header_msg = "全球団の入札が出揃いました。抽選を行ってください"
    elif phase == "r1_hature_user":
      header_badge = "外れ1位入札"
      header_msg = f"抽選を外れました。{user_team}の外れ1位候補を選んでください"
    elif phase == "round_progress":
      c_rnd = st.session_state.current_round
      header_badge = f"{c_rnd}位指名進行中"
      header_msg = f"{c_rnd}巡目の指名を行っています"
    else:
      header_badge = "ドラフト終了"
      header_msg = "全日程の指名が終了しました"

    # ON THE CLOCK
    st.markdown(
        f"""<div class="otc-container">
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
</div>""",
        unsafe_allow_html=True,
    )

    # ステータスバー
    picked_count = len(st.session_state.draft_picks[user_team])
    st.markdown(
        f"""<div class="status-container">
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
<div class="status-label" style="margin-bottom: 4px;">⏱ 進行速度</div>
<div class="speed-box">
<span class="speed-item">じっくり</span>
<span class="speed-item active">標準</span>
<span class="speed-item">高速</span>
<span class="speed-item">自分まで</span>
</div>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    # ボード
    table_rows = []
    for t in npb_teams:
      is_u = t == user_team
      tr_class = ' class="user-row"' if is_u else ""
      t_picks = st.session_state.draft_picks[t]
      cnt = len(t_picks)

      p1 = t_picks.get(1, "—")
      p2 = t_picks.get(2, "—")

      p1_cls = "val-picked" if p1 != "—" else "val-empty"
      p2_cls = "val-picked" if p2 != "—" else "val-empty"

      row_html = f"""<tr{tr_class}>
<td style="width: 32%;">
<span class="team-name">{t}</span>
<span class="team-cnt">{cnt}/{max_r}</span>
</td>
<td style="width: 34%;" class="{p1_cls}">{p1}</td>
<td style="width: 34%;" class="{p2_cls}">{p2}</td>
</tr>"""
      table_rows.append(row_html)

    all_rows = "\n".join(table_rows)

    st.markdown(
        f"""<div class="board-header">
<div>👁 12球団・全指名ボード</div>
<div style="color: #f87171; font-size: 11px; font-weight: 800;"><span style="display:inline-block; width:8px; height:8px; background:#ef4444; border-radius:50%; margin-right:4px;"></span>LIVE</div>
</div>
<table class="board-table">
<thead>
<tr>
<th>球団</th>
<th>1位</th>
<th>2位</th>
</tr>
</thead>
<tbody>
{all_rows}
</tbody>
</table>""",
        unsafe_allow_html=True,
    )

    st.write("")

    # コントロール
    avail_pool = df[~df["氏名"].isin(st.session_state.already_drafted)]
    sorted_pool = avail_pool.sort_values(by="基礎スコア", ascending=False)

    if phase == "r1_input":
      st.markdown("#### 🎯 1位入札選手の選択")
      user_pick = st.selectbox(
          f"{user_team}の1位入札選手を選択",
          sorted_pool["氏名"].tolist(),
          key="sel_r1",
      )

      if st.button(
          "この選手を1位入札する", type="primary", use_container_width=True
      ):
        bids = {user_team: user_pick}
        for t in npb_teams:
          if t == user_team:
            continue
          w = st.session_state.team_weights[t]
          tdf = avail_pool.copy()
          tdf["score"] = tdf["基礎スコア"] * tdf["カテゴリ"].map(w)
          top_c = tdf.sort_values(by="score", ascending=False).head(5)
          bids[t] = (
              top_c.sample(n=1).iloc[0]["氏名"]
              if len(top_c) > 0
              else avail_pool.iloc[0]["氏名"]
          )

        p_bids = {}
        for t, p in bids.items():
          p_bids.setdefault(p, []).append(t)

        st.session_state.r1_bids = bids
        st.session_state.r1_competing = p_bids
        st.session_state.draft_phase = "r1_confirm_bids"
        st.rerun()

    elif phase == "r1_confirm_bids":
      st.markdown("#### 📢 1位入札の競合状況")
      for p, teams in st.session_state.r1_competing.items():
        if len(teams) > 1:
          t_str = "、".join(teams)
          st.markdown(
              f"""<div class="card-competing">
<span>🔥</span>
<div><strong>{p}</strong> に {len(teams)}球団が競合！（{t_str}）</div>
</div>""",
              unsafe_allow_html=True,
          )
        else:
          st.markdown(
              f"""<div class="card-single">
<span>✅</span>
<div><strong>{p}</strong>: {teams[0]} が単独指名！</div>
</div>""",
              unsafe_allow_html=True,
          )

      if st.button(
          "🎲 運命の抽選くじを引く！", type="primary", use_container_width=True
      ):
        confirmed_1st = {}
        losers = []
        for p, teams in st.session_state.r1_competing.items():
          if len(teams) == 1:
            confirmed_1st[teams[0]] = p
            st.session_state.already_drafted.add(p)
          else:
            winner = random.choice(teams)
            confirmed_1st[winner] = p
            st.session_state.already_drafted.add(p)
            for loser in teams:
              if loser != winner:
                losers.append(loser)

        for t, p in confirmed_1st.items():
          st.session_state.draft_picks[t][1] = p

        st.session_state.loser_teams = losers

        if user_team in losers:
          st.session_state.draft_phase = "r1_hature_user"
        else:
          rem = df[~df["氏名"].isin(st.session_state.already_drafted)].copy()
          for lt in losers:
            if len(rem) > 0:
              w = st.session_state.team_weights[lt]
              rem["score"] = rem["基礎スコア"] * rem["カテゴリ"].map(w)
              top_c = rem.sort_values(by="score", ascending=False).head(5)
              ch = top_c.sample(n=1).iloc[0]["氏名"]
              st.session_state.draft_picks[lt][1] = ch
              st.session_state.already_drafted.add(ch)
              rem = rem[rem["氏名"] != ch]

          if max_r >= 2:
            st.session_state.draft_phase = "round_progress"
            st.session_state.current_round = 2
            st.session_state.weber_index = 0
          else:
            st.session_state.draft_phase = "finished"
        st.rerun()

    elif phase == "r1_hature_user":
      st.error(
          f"抽選の結果、{user_team}は外れました。外れ1位の指名選手を選択してください。"
      )
      rem_pool = df[~df["氏名"].isin(st.session_state.already_drafted)]
      hature_pick = st.selectbox(
          f"{user_team}の外れ1位指名",
          rem_pool.sort_values(by="基礎スコア", ascending=False)["氏名"].tolist(),
          key="sel_hature",
      )

      if st.button(
          "外れ1位指名を確定する", type="primary", use_container_width=True
      ):
        st.session_state.draft_picks[user_team][1] = hature_pick
        st.session_state.already_drafted.add(hature_pick)
        st.session_state.loser_teams.remove(user_team)

        rem = df[~df["氏名"].isin(st.session_state.already_drafted)].copy()
        for lt in st.session_state.loser_teams:
          if len(rem) > 0:
            w = st.session_state.team_weights[lt]
            rem["score"] = rem["基礎スコア"] * rem["カテゴリ"].map(w)
            top_c = rem.sort_values(by="score", ascending=False).head(5)
            ch = top_c.sample(n=1).iloc[0]["氏名"]
            st.session_state.draft_picks[lt][1] = ch
            st.session_state.already_drafted.add(ch)
            rem = rem[rem["氏名"] != ch]

        if max_r >= 2:
          st.session_state.draft_phase = "round_progress"
          st.session_state.current_round = 2
          st.session_state.weber_index = 0
        else:
          st.session_state.draft_phase = "finished"
        st.rerun()

    elif phase == "round_progress":
      c_rnd = st.session_state.current_round
      order = list(reversed(npb_teams)) if c_rnd % 2 == 0 else npb_teams
      w_idx = st.session_state.weber_index

      if w_idx < len(order):
        now_team = order[w_idx]
        st.markdown(
            f"#### 選択権： **{now_team}** （第{c_rnd}巡目 第{w_idx+1}指名）"
        )

        rem_pool = df[~df["氏名"].isin(st.session_state.already_drafted)]
        sorted_rem = rem_pool.sort_values(by="基礎スコア", ascending=False)

        if now_team == user_team:
          u_choice = st.selectbox(
              f"{user_team}の第{c_rnd}位指名選手を選択",
              sorted_rem["氏名"].tolist(),
              key=f"rnd_pick_{c_rnd}_{w_idx}",
          )
          if st.button(
              "この選手を指名する", type="primary", use_container_width=True
          ):
            st.session_state.draft_picks[user_team][c_rnd] = u_choice
            st.session_state.already_drafted.add(u_choice)
            st.session_state.weber_index += 1
            st.rerun()
        else:
          st.write(f"{now_team}の指名番です。")
          if st.button(
              f"{now_team} の指名を行う（次へ）",
              type="secondary",
              use_container_width=True,
          ):
            w = st.session_state.team_weights[now_team]
            tdf = rem_pool.copy()
            tdf["score"] = tdf["基礎スコア"] * tdf["カテゴリ"].map(w)
            top_c = tdf.sort_values(by="score", ascending=False).head(3)
            ch = (
                top_c.sample(n=1).iloc[0]["氏名"]
                if len(top_c) > 0
                else rem_pool.iloc[0]["氏名"]
            )
            st.session_state.draft_picks[now_team][c_rnd] = ch
            st.session_state.already_drafted.add(ch)
            st.session_state.weber_index += 1
            st.rerun()
      else:
        st.success(f"🎉 第{c_rnd}巡目の指名が完了しました！")
        if c_rnd < max_r:
          if st.button(
              f"➡️ 第{c_rnd+1}巡目へ進む",
              type="primary",
              use_container_width=True,
          ):
            st.session_state.current_round += 1
            st.session_state.weber_index = 0
            st.rerun()
        else:
          st.balloons()
          st.success("🏆 全指名枠のドラフト会議がすべて終了しました！")

    st.write("---")
    if st.button("⚙️ 設定画面に戻る（やり直す）", use_container_width=True):
      st.session_state.current_screen = "設定画面"
      st.session_state.draft_phase = "r1_input"
      st.session_state.draft_picks = {t: {} for t in npb_teams}
      st.session_state.already_drafted = set()
      st.rerun()
