import random
import pandas as pd
import streamlit as st

# ページ基本設定
st.set_page_config(
    page_title="NPB ドラフトシミュレーター", page_icon="⚾", layout="centered"
)

# --- 1. CSSによるデザイン完全再現 ---
st.markdown(
    """
<style>
    /* 全体背景とフォントの引き締め */
    .stApp {
        background-color: #f6f5f1;
        font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'BIZ UDPGothic', sans-serif;
    }
    
    /* 上部カードバナー */
    .on-the-clock-card {
        background-color: #ffffff;
        border-radius: 14px;
        border-top: 5px solid #a91e2c;
        border-left: 1px solid #e2ded8;
        border-right: 1px solid #e2ded8;
        border-bottom: 1px solid #e2ded8;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .otc-icon-box {
        background-color: #fdf2f2;
        color: #a91e2c;
        border-radius: 10px;
        width: 46px;
        height: 46px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        flex-shrink: 0;
    }
    .otc-label-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 4px;
    }
    .otc-title {
        color: #a91e2c;
        font-weight: 800;
        font-size: 13px;
        letter-spacing: 0.8px;
    }
    .otc-badge {
        background-color: #ffffff;
        border: 1px solid #d4cece;
        color: #4a4a4a;
        font-size: 11px;
        padding: 2px 10px;
        border-radius: 20px;
        font-weight: 600;
    }
    .otc-main-text {
        color: #1a1a1a;
        font-size: 17px;
        font-weight: 700;
        margin: 0;
    }

    /* ネイビーのステータスバー */
    .status-bar {
        background-color: #172a3a;
        border-radius: 10px;
        padding: 14px 20px;
        color: #ffffff;
        margin-bottom: 16px;
    }
    .status-header-text {
        font-size: 11px;
        letter-spacing: 1px;
        color: #8da2b5;
        font-weight: 700;
    }
    .status-val-team {
        font-size: 24px;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.1;
    }
    .status-val-count {
        font-size: 24px;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.1;
    }
    
    /* 12球団 全指名ボード */
    .board-header {
        background-color: #172a3a;
        color: #ffffff;
        border-radius: 8px 8px 0 0;
        padding: 10px 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-weight: 700;
        font-size: 14px;
    }
    .live-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        background-color: #ef4444;
        border-radius: 50%;
        margin-right: 4px;
    }
    .live-badge {
        color: #f87171;
        font-size: 11px;
        font-weight: 800;
        display: flex;
        align-items: center;
    }

    /* 指名ボードのテーブル */
    .draft-table {
        width: 100%;
        border-collapse: collapse;
        background: #ffffff;
        border-left: 1px solid #e2ded8;
        border-right: 1px solid #e2ded8;
        border-bottom: 1px solid #e2ded8;
        border-radius: 0 0 8px 8px;
        overflow: hidden;
    }
    .draft-table th {
        background-color: #ebe7df;
        color: #2b2b2b;
        font-size: 12px;
        font-weight: 700;
        padding: 8px 12px;
        text-align: left;
        border-bottom: 1px solid #d9d4cc;
    }
    .draft-table td {
        padding: 10px 12px;
        font-size: 13px;
        color: #1a1a1a;
        border-bottom: 1px solid #f0ede6;
        vertical-align: middle;
    }
    .draft-table tr.user-row {
        background-color: #fbf5e6 !important;
    }
    .draft-table tr.user-row td.team-name-cell {
        color: #a86c0c;
        font-weight: 800;
    }
    .team-name-cell {
        font-weight: 700;
    }
    .team-count-cell {
        color: #888888;
        font-size: 11px;
        padding-left: 8px;
    }
    .empty-cell {
        color: #c0bcb4;
    }
    .picked-cell {
        font-weight: 600;
        color: #111827;
    }
</style>
""",
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
  # 球団リスト（画像の並び順）
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

  # セッション状態初期化
  if "team_weights" not in st.session_state:
    st.session_state.team_weights = {
        t: {cat: round(random.uniform(0.8, 1.3), 1) for cat in categories}
        for t in npb_teams
    }

  if "user_team" not in st.session_state:
    st.session_state.user_team = "阪神"

  if "draft_phase" not in st.session_state:
    # ステージ管理:
    # "r1_input" -> "r1_confirm_bids" -> "r1_lottery" -> "r1_hature_user" (外れた場合) -> "round_progress"
    st.session_state.draft_phase = "r1_input"
    st.session_state.draft_picks = {t: {} for t in npb_teams}
    st.session_state.already_drafted = set()
    st.session_state.r1_bids = {}
    st.session_state.r1_competing = {}
    st.session_state.loser_teams = []
    st.session_state.current_round = 1
    st.session_state.weber_index = 0

  # データ前処理
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

  # --- 3. 画面上部：モード切り替え（設定タブ / 会場） ---
  mode = st.sidebar.radio(
      "画面ナビゲーション", ["🏟️ ドラフト会場", "🎛️ 各球団の係数設定"]
  )

  if mode == "🎛️ 各球団の係数設定":
    st.subheader("🎛️ 12球団のカテゴリ別補正スライダー")
    st.sidebar.write("各球団の好みを微調整できます。")
    t_tabs = st.tabs(npb_teams)
    for i, t in enumerate(npb_teams):
      with t_tabs[i]:
        st.write(f"**{t} の補正設定**")
        w = st.session_state.team_weights[t]
        c1, c2, c3, c4 = st.columns(4)
        w["高投"] = c1.slider("高投", 0.0, 2.0, w["高投"], 0.1, key=f"{t}_高投")
        w["高捕"] = c2.slider("高捕", 0.0, 2.0, w["高捕"], 0.1, key=f"{t}_高捕")
        w["高内"] = c3.slider("高内", 0.0, 2.0, w["高内"], 0.1, key=f"{t}_高内")
        w["高外"] = c4.slider("高外", 0.0, 2.0, w["高外"], 0.1, key=f"{t}_高外")

        c5, c6, c7, c8 = st.columns(4)
        w["大投"] = c5.slider("大投", 0.0, 2.0, w["大投"], 0.1, key=f"{t}_大投")
        w["大捕"] = c6.slider("大捕", 0.0, 2.0, w["大捕"], 0.1, key=f"{t}_大捕")
        w["大内"] = c7.slider("大内", 0.0, 2.0, w["大内"], 0.1, key=f"{t}_大内")
        w["大外"] = c8.slider("大外", 0.0, 2.0, w["大外"], 0.1, key=f"{t}_大外")

        c9, c10, c11, c12 = st.columns(4)
        w["社投"] = c9.slider("社投", 0.0, 2.0, w["社投"], 0.1, key=f"{t}_社投")
        w["社捕"] = c10.slider("社捕", 0.0, 2.0, w["社捕"], 0.1, key=f"{t}_社捕")
        w["社内"] = c11.slider("社内", 0.0, 2.0, w["社内"], 0.1, key=f"{t}_社内")
        w["社外"] = c12.slider("社外", 0.0, 2.0, w["社外"], 0.1, key=f"{t}_社外")
    st.stop()

  # ==========================================
  # ドラフト会場メイン画面
  # ==========================================
  user_team = st.session_state.user_team
  phase = st.session_state.draft_phase

  # ステータスメッセージの作成
  if phase == "r1_input":
    header_badge = "1位・第1回入札"
    header_msg = f"1位・第1回入札。{user_team}の候補を選んでください"
  elif phase == "r1_confirm_bids":
    header_badge = "1位・入札確定"
    header_msg = "全球団の入札が揃いました。競合抽選を行ってください"
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

  # --- A. ON THE CLOCK バナー ---
  st.markdown(
      f"""
    <div class="on-the-clock-card">
        <div class="otc-icon-box">✦</div>
        <div>
            <div class="otc-label-row">
                <span class="otc-title">ON THE CLOCK</span>
                <span class="otc-badge">{header_badge}</span>
            </div>
            <h2 class="otc-main-text">{header_msg}</h2>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # --- B. ネイビーのステータスバー ---
  picked_count = len(st.session_state.draft_picks[user_team])
  st.markdown(
      f"""
    <div class="status-bar">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; gap: 32px;">
                <div>
                    <div class="status-header-text">YOUR TEAM</div>
                    <div class="status-val-team">{user_team}</div>
                </div>
                <div>
                    <div class="status-header-text">SELECTED</div>
                    <div class="status-val-count">{picked_count} / 7</div>
                </div>
            </div>
            <div>
                <div class="status-header-text" style="margin-bottom: 4px;">⏱ 進行速度</div>
                <div style="background: rgba(255,255,255,0.08); padding: 3px; border-radius: 6px; display: flex; gap: 4px; font-size: 12px;">
                    <span style="padding: 3px 8px; color: #8da2b5;">じっくり</span>
                    <span style="background: #eab308; color: #172a3a; font-weight: 700; padding: 3px 8px; border-radius: 4px;">標準</span>
                    <span style="padding: 3px 8px; color: #8da2b5;">高速</span>
                    <span style="padding: 3px 8px; color: #8da2b5;">自分まで</span>
                </div>
            </div>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # --- C. 12球団・全指名ボード ---
  st.markdown(
      """
    <div class="board-header">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span>👁 12球団・全指名ボード</span>
        </div>
        <div class="live-badge">
            <span class="live-dot"></span>LIVE
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # テーブルHTMLの生成（画像どおりのスタイル）
  table_rows_html = ""
  for t in npb_teams:
    is_u = t == user_team
    row_cls = ' class="user-row"' if is_u else ""
    t_picks = st.session_state.draft_picks[t]
    cnt = len(t_picks)

    p1 = t_picks.get(1, "—")
    p2 = t_picks.get(2, "—")

    p1_cls = "picked-cell" if p1 != "—" else "empty-cell"
    p2_cls = "picked-cell" if p2 != "—" else "empty-cell"

    table_rows_html += f"""
    <tr{row_cls}>
        <td style="width: 30%;">
            <span class="team-name-cell">{t}</span>
            <span class="team-count-cell">{cnt}/7</span>
        </td>
        <td style="width: 35%;" class="{p1_cls}">{p1}</td>
        <td style="width: 35%;" class="{p2_cls}">{p2}</td>
    </tr>
    """

  st.markdown(
      f"""
    <table class="draft-table">
        <thead>
            <tr>
                <th>球団</th>
                <th>1位</th>
                <th>2位</th>
            </tr>
        </thead>
        <tbody>
            {table_rows_html}
        </tbody>
    </table>
    """,
      unsafe_allow_html=True,
  )

  st.write("")

  # ==========================================
  # D. 進行・操作コントロール部
  # ==========================================
  avail_pool = df[~df["氏名"].isin(st.session_state.already_drafted)]
  sorted_pool = avail_pool.sort_values(by="基礎スコア", ascending=False)

  # 1. 1位入札フェーズ
  if phase == "r1_input":
    st.markdown("#### 🎯 1位入札選手の選択")
    user_pick = st.selectbox(
        f"{user_team}の1位入札選手を選択",
        sorted_pool["氏名"].tolist(),
        key="sel_r1",
    )

    if st.button("この選手を1位入札する", type="primary", use_container_width=True):
      # AI球団の入札決定（上位5名からランダム）
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

      # 競合チェック
      p_bids = {}
      for t, p in bids.items():
        p_bids.setdefault(p, []).append(t)

      st.session_state.r1_bids = bids
      st.session_state.r1_competing = p_bids
      st.session_state.draft_phase = "r1_confirm_bids"
      st.rerun()

  # 2. 入札結果発表 & 抽選実行
  elif phase == "r1_confirm_bids":
    st.markdown("#### 📢 1位入札の競合状況")
    comp_found = False
    for p, teams in st.session_state.r1_competing.items():
      if len(teams) > 1:
        comp_found = True
        t_str = "、".join(teams)
        st.warning(f"🔥 **{p}** に {len(teams)}球団が競合！（{t_str}）")
      else:
        st.success(f"✅ **{p}**: **{teams[0]}** が単独指名！")

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

      # ユーザー球団が外れたら外れ1位選択へ、当たっていればAIの外れ1位を自動処理して2巡目へ
      if user_team in losers:
        st.session_state.draft_phase = "r1_hature_user"
      else:
        # AIの外れ1位処理
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
        st.session_state.draft_phase = "round_progress"
        st.session_state.current_round = 2
        st.session_state.weber_index = 0
      st.rerun()

  # 3. ユーザー球団の外れ1位選択
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

    if st.button("外れ1位指名を確定する", type="primary", use_container_width=True):
      st.session_state.draft_picks[user_team][1] = hature_pick
      st.session_state.already_drafted.add(hature_pick)
      st.session_state.loser_teams.remove(user_team)

      # 残りAIチームの外れ1位処理
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

      st.session_state.draft_phase = "round_progress"
      st.session_state.current_round = 2
      st.session_state.weber_index = 0
      st.rerun()

  # 4. 2巡目以降（ウェーバー指名）
  elif phase == "round_progress":
    c_rnd = st.session_state.current_round
    # 偶数巡目は逆順、奇数巡目は正順
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
      c1, c2 = st.columns(2)
      with c1:
        if st.button(
            f"➡️ 第{c_rnd+1}巡目へ進む", type="primary", use_container_width=True
        ):
          st.session_state.current_round += 1
          st.session_state.weber_index = 0
          st.rerun()
      with c2:
        if st.button("🏁 ドラフト終了", use_container_width=True):
          st.session_state.draft_phase = "finished"
          st.rerun()

  # リセット
  st.write("---")
  if st.button("🔄 ドラフトをやり直す", use_container_width=True):
    st.session_state.draft_phase = "r1_input"
    st.session_state.draft_picks = {t: {} for t in npb_teams}
    st.session_state.already_drafted = set()
    st.rerun()
