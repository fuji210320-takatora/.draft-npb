import random
import pandas as pd
import streamlit as st

# ページの設定
st.set_page_config(
    page_title="プロ野球ドラフトシミュレーター（競合・抽選あり）",
    page_icon="⚾",
    layout="wide",
)

st.title("⚾ プロ野球ドラフトシミュレーター（完全版）")
st.write(
    "各球団の「補正（好み）」と、自分が担当する球団の設定を行い、1位指名の競合・抽選をシミュレーションします。"
)

# --- 1. データの読み込み ---
SHEET_ID = "1Qd_GNT-V0Ololma_QpIAhgEzLSFXlsv8sMG99espI90"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"


@st.cache_data(ttl=60)
def load_data(url):
  try:
    return pd.read_csv(url)
  except Exception as e:
    st.error(
        f"データの読み込みに失敗しました。スプレッドシートの共有設定を確認してください。\nエラー: {e}"
    )
    return None


df_raw = load_data(csv_url)

if df_raw is not None:
  npb_teams = [
      "阪神",
      "巨人",
      "DeNA",
      "広島",
      "中日",
      "ヤクルト",
      "オリックス",
      "ロッテ",
      "ソフトバンク",
      "楽天",
      "西武",
      "日本ハム",
  ]

  # --- 2. 担当球団の選択 ---
  st.subheader("1. 担当する球団を選ぶ")
  if "user_team" not in st.session_state:
    st.session_state.user_team = "阪神"

  cols = st.columns(6)
  for i, team in enumerate(npb_teams):
    with cols[i % 6]:
      is_selected = st.session_state.user_team == team
      if st.button(
          team,
          key=f"team_sel_{team}",
          use_container_width=True,
          type="primary" if is_selected else "secondary",
      ):
        st.session_state.user_team = team
        st.rerun()

  user_team = st.session_state.user_team
  st.info(f"現在の担当球団: **{user_team}** （あなたの指名は下のセレクトボックスで決定します）")

  st.divider()

  # --- 3. 12球団それぞれの「カテゴリ別補正（好み）」を設定する ---
  st.subheader("2. 12球団の補正（好み）チューニング")
  st.write(
      "各球団がどのような選手層を好むか、倍率（係数）をそれぞれ設定できます。"
  )

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

  # セッション状態で各球団の係数辞書を保持
  if "team_weights" not in st.session_state:
    # 初期値は全チーム一律1.0
    st.session_state.team_weights = {}
    for t in npb_teams:
      st.session_state.team_weights[t] = {cat: 1.0 for cat in categories}

  # タブで球団ごとに切り替えて係数をいじれるようにする
  team_tabs = st.tabs(npb_teams)

  for i, team in enumerate(npb_teams):
    with team_tabs[i]:
      st.write(f"**{team} の補正設定**")
      w = st.session_state.team_weights[team]

      col1, col2, col3, col4 = st.columns(4)
      w["高投"] = col1.slider(
          "高投", 0.0, 2.0, w["高投"], 0.1, key=f"{team}_高投"
      )
      w["高捕"] = col2.slider(
          "高捕", 0.0, 2.0, w["高捕"], 0.1, key=f"{team}_高捕"
      )
      w["高内"] = col3.slider(
          "高内", 0.0, 2.0, w["高内"], 0.1, key=f"{team}_高内"
      )
      w["高外"] = col4.slider(
          "高外", 0.0, 2.0, w["高外"], 0.1, key=f"{team}_高外"
      )

      col5, col6, col7, col8 = st.columns(4)
      w["大投"] = col5.slider(
          "大投", 0.0, 2.0, w["大投"], 0.1, key=f"{team}_大投"
      )
      w["大捕"] = col6.slider(
          "大捕", 0.0, 2.0, w["大捕"], 0.1, key=f"{team}_大捕"
      )
      w["大内"] = col7.slider(
          "大内", 0.0, 2.0, w["大内"], 0.1, key=f"{team}_大内"
      )
      w["大外"] = col8.slider(
          "大外", 0.0, 2.0, w["大外"], 0.1, key=f"{team}_大外"
      )

      col9, col10, col11, col12 = st.columns(4)
      w["社投"] = col9.slider(
          "社投", 0.0, 2.0, w["社投"], 0.1, key=f"{team}_社投"
      )
      w["社捕"] = col10.slider(
          "社捕", 0.0, 2.0, w["社捕"], 0.1, key=f"{team}_社捕"
      )
      w["社内"] = col11.slider(
          "社内", 0.0, 2.0, w["社内"], 0.1, key=f"{team}_社内"
      )
      w["社外"] = col12.slider(
          "社外", 0.0, 2.0, w["社外"], 0.1, key=f"{team}_社外"
      )

  st.divider()

  # --- 4. 基礎データの前処理 ---
  df = df_raw.copy()


  def get_category_key(row):
    kbn = str(row["区分"])
    pos = str(row["守備位置"])
    prefix = "他"
    if "高" in kbn:
      prefix = "高"
    elif "大" in kbn:
      prefix = "大"
    elif "社会人" in kbn or "社" in kbn or "独立" in kbn or "クラブ" in kbn:
      prefix = "社"

    suffix = "他"
    if "投" in pos:
      suffix = "投"
    elif "捕" in pos:
      suffix = "捕"
    elif "内" in pos:
      suffix = "内"
    elif "外" in pos:
      suffix = "外"

    key = prefix + suffix
    return key if key in categories else "他"


  df["カテゴリ"] = df.apply(get_category_key, axis=1)


  def rank_to_score(rank):
    score_map = {
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
    return score_map.get(str(rank).strip(), 45)


  df["基礎スコア"] = df["評価"].apply(rank_to_score)

  # --- 5. あなたの球団の指名選手選択 ---
  st.subheader("3. あなたの球団の1位指名入札")
  # 阪神などの基準スコア順でリストを作る
  default_sorted = df.sort_values(by="基礎スコア", ascending=False)
  user_choice = st.selectbox(
      f"{user_team}で1位入札する選手を選ぶ",
      default_sorted["氏名"].tolist(),
  )

  # --- 6. ドラフト入札・競合抽選シミュレーション実行 ---
  if st.button("ドラフト1位会議（入札・抽選）を実行する", type="primary"):
    # 各球団の1位入札先を決定する
    bids = {}  # {球団名: 選手名}

    for team in npb_teams:
      if team == user_team:
        bids[team] = user_choice
      else:
        # AI球団は「そのチームの補正係数」を掛けた評価スコアが最も高い選手を狙う
        t_weights = st.session_state.team_weights[team]
        temp_df = df.copy()
        temp_df["球団別スコア"] = temp_df["基礎スコア"] * temp_df["カテゴリ"].map(
            t_weights
        )
        best_player = temp_df.sort_values(
            by="球団別スコア", ascending=False
        ).iloc[0]["氏名"]
        bids[team] = best_player

    # 競合（同じ選手を複数球団が指名）の集計
    # {選手名: [指名した球団のリスト]}
    player_bids = {}
    for team, player in bids.items():
      if player not in player_bids:
        player_bids[player] = []
      player_bids[player].append(team)

    # 抽選処理と確定
    confirmed_picks = {}  # {選手名: 獲得球団}
    loser_teams = []  # 抽選に外れた球団のリスト

    st.subheader("🎯 1位入札結果（競合発表）")
    bids_display = []
    for team, player in bids.items():
      bids_display.append({"球団": team, "1位入札選手": player})
    st.dataframe(pd.DataFrame(bids_display), use_container_width=True)

    st.subheader("🎲 抽選結果 ＆ 外れ1位指名")
    lottery_logs = []

    for player, competing_teams in player_bids.items():
      if len(competing_teams) == 1:
        # 競合なし：単独指名成功
        winner = competing_teams[0]
        confirmed_picks[player] = winner
        lottery_logs.append(
            f"✅ **{player}**: **{winner}** が単独指名で交渉権獲得！"
        )
      else:
        # 競合あり：抽選
        winner = random.choice(competing_teams)
        confirmed_picks[player] = winner
        losers = [t for t in competing_teams if t != winner]
        loser_teams.extend(losers)
        losers_str = ", ".join(losers)
        lottery_logs.append(
            f"🔥 **{player}** ({len(competing_teams)}球団競合): 抽選の結果、**{winner}** が交渉権獲得！（外れ: {losers_str}）"
        )

    for log in lottery_logs:
      st.markdown(log)

    # 外れ1位の指名処理（はずれた球団が、残った選手から再指名）
    # 簡易的に、残った選手の中から、各球団の補正スコアが一番高い選手を割り当てる
    remaining_pool = df[~df["氏名"].isin(confirmed_picks.keys())].copy()

    # 外れ1位の指名順は、実際のドラフト制度に沿うか、あるいはシンプルに残った順に処理
    for team in loser_teams:
      if len(remaining_pool) > 0:
        t_weights = st.session_state.team_weights[team]
        remaining_pool["スコア"] = remaining_pool["基礎スコア"] * remaining_pool[
            "カテゴリ"
        ].map(t_weights)
        remaining_pool = remaining_pool.sort_values(
            by="スコア", ascending=False
        ).reset_index(drop=True)

        hature_player = remaining_pool.iloc[0]["氏名"]
        confirmed_picks[hature_player] = team
        # プールから除外
        remaining_pool = remaining_pool[
            remaining_pool["氏名"] != hature_player
        ].reset_index(drop=True)
        lottery_logs.append(
            f"🔄 **{team} (外れ1位)**: **{hature_player}** を指名"
        )

    st.divider()
    st.subheader("🏆 1位指名 最終確定結果")

    final_result_list = []
    for team in npb_teams:
      # どの選手を獲得したか逆引き
      acquired_player = [
          p for p, t in confirmed_picks.items() if t == team
      ]
      p_name = acquired_player[0] if acquired_player else "不明"
      p_row = df[df["氏名"] == p_name].iloc[0] if p_name in df["氏名"].values else None

      final_result_list.append({
          "球団": f"★ {team} (あなた)" if team == user_team else team,
          "獲得選手": p_name,
          "区分": p_row["区分"] if p_row is not None else "",
          "守備": p_row["守備位置"] if p_row is not None else "",
          "評価": p_row["評価"] if p_row is not None else "",
      })

    st.table(pd.DataFrame(final_result_list))
