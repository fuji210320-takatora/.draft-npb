import random
import pandas as pd
import streamlit as st

# ページの設定
st.set_page_config(
    page_title="プロ野球ドラフト会議シミュレーター", page_icon="⚾", layout="wide"
)

st.title("⚾ プロ野球ドラフト会議シミュレーター（完全対話型）")

# --- 1. データの読み込み ---
SHEET_ID = "1Qd_GNT-V0Ololma_QpIAhgEzLSFXlsv8sMG99espI90"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"


@st.cache_data(ttl=60)
def load_data(url):
  try:
    return pd.read_csv(url)
  except Exception as e:
    st.error(f"データの読み込みに失敗しました。エラー: {e}")
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

  # セッションステートの初期化
  if "team_weights" not in st.session_state:
    st.session_state.team_weights = {}
    for t in npb_teams:
      st.session_state.team_weights[t] = {
          cat: round(random.uniform(0.8, 1.3), 1) for cat in categories
      }

  if "user_team" not in st.session_state:
    st.session_state.user_team = "阪神"

  # ドラフト進行管理の状態変数
  if "draft_state" not in st.session_state:
    st.session_state.draft_state = "config"
    st.session_state.draft_results = {}  # {球団名: {1: 選手名, 2: 選手名...}}
    st.session_state.already_drafted = set()
    st.session_state.current_round = 1
    st.session_state.bids_cache = {}
    st.session_state.player_bids_cache = {}
    st.session_state.pending_losers = []
    st.session_state.temp_r1_picks = {}

  # --- データの基礎加工 ---
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

  # --- 画面切り替え ---
  app_mode = st.radio(
      "画面を選択",
      ["📋 1. 各球団の設定・チューニング", "🏟️ 2. ドラフト会議会場"],
      horizontal=True,
  )

  # ==========================================
  # 【画面1】設定・チューニング画面
  # ==========================================
  if app_mode == "📋 1. 各球団の設定・チューニング":
    st.subheader("📋 担当球団 & 12球団の補正（好み）設定")

    st.markdown("#### 👤 自分の担当球団を選ぶ")
    user_cols = st.columns(6)
    for i, team in enumerate(npb_teams):
      with user_cols[i % 6]:
        if st.button(
            team,
            key=f"cfg_user_{team}",
            use_container_width=True,
            type="primary" if st.session_state.user_team == team else "secondary",
        ):
          st.session_state.user_team = team
          st.success(f"担当を「{team}」に変更しました！")

    st.divider()
    st.markdown("#### 🎛️ 12球団のカテゴリ別補正スライダー")
    team_tabs = st.tabs(npb_teams)

    for i, team in enumerate(npb_teams):
      with team_tabs[i]:
        st.write(f"**{team} の好み設定**")
        w = st.session_state.team_weights[team]

        col1, col2, col3, col4 = st.columns(4)
        w["高投"] = col1.slider(
            "高投", 0.0, 2.0, w["高投"], 0.1, key=f"s_{team}_高投"
        )
        w["高捕"] = col2.slider(
            "高捕", 0.0, 2.0, w["高捕"], 0.1, key=f"s_{team}_高捕"
        )
        w["高内"] = col3.slider(
            "高内", 0.0, 2.0, w["高内"], 0.1, key=f"s_{team}_高内"
        )
        w["高外"] = col4.slider(
            "高外", 0.0, 2.0, w["高外"], 0.1, key=f"s_{team}_高外"
        )

        col5, col6, col7, col8 = st.columns(4)
        w["大投"] = col5.slider(
            "大投", 0.0, 2.0, w["大投"], 0.1, key=f"s_{team}_大投"
        )
        w["大捕"] = col6.slider(
            "大捕", 0.0, 2.0, w["大捕"], 0.1, key=f"s_{team}_大捕"
        )
        w["大内"] = col7.slider(
            "大内", 0.0, 2.0, w["大内"], 0.1, key=f"s_{team}_大内"
        )
        w["大外"] = col8.slider(
            "大外", 0.0, 2.0, w["大外"], 0.1, key=f"s_{team}_大外"
        )

        col9, col10, col11, col12 = st.columns(4)
        w["社投"] = col9.slider(
            "社投", 0.0, 2.0, w["社投"], 0.1, key=f"s_{team}_社投"
        )
        w["社捕"] = col10.slider(
            "社捕", 0.0, 2.0, w["社捕"], 0.1, key=f"s_{team}_社捕"
        )
        w["社内"] = col11.slider(
            "社内", 0.0, 2.0, w["社内"], 0.1, key=f"s_{team}_社内"
        )
        w["社外"] = col12.slider(
            "社外", 0.0, 2.0, w["社外"], 0.1, key=f"s_{team}_社外"
        )

  # ==========================================
  # 【画面2】ドラフト会議会場
  # ==========================================
  elif app_mode == "🏟️ 2. ドラフト会議会場":
    user_team = st.session_state.user_team
    st.info(
        f"現在の担当球団: **{user_team}** （設定画面からいつでも変更できます）"
    )

    if st.button("🔄 ドラフトを最初からやり直す"):
      st.session_state.draft_state = "config"
      st.session_state.draft_results = {}
      st.session_state.already_drafted = set()
      st.session_state.current_round = 1
      st.session_state.bids_cache = {}
      st.session_state.player_bids_cache = {}
      st.session_state.pending_losers = []
      st.session_state.temp_r1_picks = {}
      st.rerun()

    st.divider()

    # ------------------------------------------
    # ステップ A: 1位指名 入札
    # ------------------------------------------
    if st.session_state.draft_state == "config":
      st.subheader("📝 ドラフト 1位指名入札")
      st.write("あなたが操作する球団の1位入札選手を選んでください。")

      available_df = df[~df["氏名"].isin(st.session_state.already_drafted)]
      default_sorted = available_df.sort_values(by="基礎スコア", ascending=False)

      user_choice = st.selectbox(
          f"{user_team}の1位入札選手", default_sorted["氏名"].tolist()
      )

      if st.button("🔔 1位入札を確定して競合を確認する", type="primary"):
        # AI球団の入札先決定
        bids = {user_team: user_choice}
        for team in npb_teams:
          if team == user_team:
            continue
          t_weights = st.session_state.team_weights[team]
          temp_df = available_df.copy()
          temp_df["球団別スコア"] = temp_df["基礎スコア"] * temp_df[
              "カテゴリ"
          ].map(t_weights)
          top_cands = temp_df.sort_values(by="球団別スコア", ascending=False).head(
              5
          )
          if len(top_cands) > 0:
            bids[team] = top_cands.sample(n=1).iloc[0]["氏名"]
          else:
            bids[team] = available_df.iloc[0]["氏名"]

        # 競合集計
        player_bids = {}
        for team, player in bids.items():
          if player not in player_bids:
            player_bids[player] = []
          player_bids[player].append(team)

        st.session_state.bids_cache = bids
        st.session_state.player_bids_cache = player_bids
        st.session_state.draft_state = "r1_check_bids"
        st.rerun()

    # ------------------------------------------
    # ステップ B: 1位入札の競合確認 ＆ 抽選フェーズ
    # ------------------------------------------
    elif st.session_state.draft_state == "r1_check_bids":
      st.subheader("🎯 第1回選択希望選手（1位入札結果）")
      st.write(
          "全球団の1位入札が出揃いました。競合している選手を確認し、抽選を行ってください。"
      )

      # 一覧表示
      bids_list = []
      for t, p in st.session_state.bids_cache.items():
        bids_list.append({"球団": t, "入札選手": p})
      st.dataframe(
          pd.DataFrame(bids_list), use_container_width=True, hide_index=True
      )

      st.divider()
      st.markdown("#### 🔥 競合状況の発表")
      has_competition = False
      for player, teams in st.session_state.player_bids_cache.items():
        if len(teams) > 1:
          has_competition = True
          teams_str = ", ".join(teams)
          st.warning(
              f"**{player}** に **{len(teams)}球団** が競合しています！（入札球団: {teams_str}）"
          )
        else:
          st.success(f"**{player}**: **{teams[0]}** が単独指名です！")

      if st.button("🎲 運命の抽選（くじ引き）を実行する", type="primary"):
        confirmed_1st = {}
        loser_teams = []
        lottery_logs = []

        for player, competing_teams in st.session_state.player_bids_cache.items():
          if len(competing_teams) == 1:
            winner = competing_teams[0]
            confirmed_1st[player] = winner
            lottery_logs.append(
                f"- **{player}**: **{winner}** が単独指名で交渉権獲得！"
            )
          else:
            winner = random.choice(competing_teams)
            confirmed_1st[player] = winner
            losers = [t for t in competing_teams if t != winner]
            loser_teams.extend(losers)
            losers_str = ", ".join(losers)
            lottery_logs.append(
                f"- 🔥 **{player}** ({len(competing_teams)}球団競合): 抽選の結果、**{winner}** が交渉権獲得！（外れ: {losers_str}）"
            )

        st.session_state.temp_r1_picks = confirmed_1st
        st.session_state.pending_losers = loser_teams
        st.session_state.r1_logs = lottery_logs

        # もし自チームが抽選を外れていた場合、プレイヤーに外れ1位を選ばせる
        if user_team in loser_teams:
          st.session_state.draft_state = "r1_hature_user"
        else:
          # 自チームが当たりを引いた場合、AIの外れ1位を自動処理
          process_ai_hature_1st(df, npb_teams)
          st.session_state.draft_state = "r1_result_view"
        st.rerun()

    # ------------------------------------------
    # ステップ C: プレイヤーの外れ1位選択
    # ------------------------------------------
    elif st.session_state.draft_state == "r1_hature_user":
      st.subheader("🔄 1位指名 抽選外れ（外れ1位指名）")
      st.warning(
          f"残念ながら **{user_team}** は1位入札の抽選を外れました。外れ1位指名する選手を自分で選んでください。"
      )

      already_taken = list(st.session_state.temp_r1_picks.keys())
      rem_df = df[~df["氏名"].isin(already_taken)]
      rem_sorted = rem_df.sort_values(by="基礎スコア", ascending=False)

      user_hature_choice = st.selectbox(
          f"{user_team}の外れ1位指名選手", rem_sorted["氏名"].tolist()
      )

      if st.button("外れ1位指名を確定する", type="primary"):
        st.session_state.temp_r1_picks[user_hature_choice] = user_team
        st.session_state.pending_losers.remove(user_team)

        # 残りのAIチームの外れ1位を自動処理
        rem_pool = df[~df["氏名"].isin(st.session_state.temp_r1_picks.keys())].copy()
        for team in st.session_state.pending_losers:
          if len(rem_pool) > 0:
            t_weights = st.session_state.team_weights[team]
            rem_pool["スコア"] = rem_pool["基礎スコア"] * rem_pool["カテゴリ"].map(
                t_weights
            )
            rem_pool = rem_pool.sort_values(
                by="スコア", ascending=False
            ).reset_index(drop=True)
            top_n = rem_pool.head(5)
            chosen = top_n.sample(n=1).iloc[0]["氏名"]
            st.session_state.temp_r1_picks[chosen] = team
            rem_pool = rem_pool[rem_pool["氏名"] != chosen].reset_index(drop=True)

        for p, t in st.session_state.temp_r1_picks.items():
          if t not in st.session_state.draft_results:
            st.session_state.draft_results[t] = {}
          st.session_state.draft_results[t][1] = p
          st.session_state.already_drafted.add(p)

        st.session_state.draft_state = "r1_result_view"
        st.rerun()

    # ------------------------------------------
    # ステップ D: 1位結果確認 ＆ 2巡目以降へ進む
    # ------------------------------------------
    elif st.session_state.draft_state == "r1_result_view":
      st.subheader("🏆 1位指名 確定結果")
      for log in st.session_state.get("r1_logs", []):
        st.markdown(log)

      st.markdown("#### 各球団の1位獲得選手")
      r1_list = []
      for t in npb_teams:
        p = st.session_state.draft_results.get(t, {}).get(1, "不明")
        r1_list.append({"球団": t, "1位指名": p})
      st.dataframe(pd.DataFrame(r1_list), use_container_width=True, hide_index=True)

      st.divider()
      if st.button(
          "➡️ 2巡目（ウェーバー指名）の自チーム指名へ進む", type="primary"
      ):
        st.session_state.current_round = 2
        st.session_state.round_queue_idx = 0
        st.session_state.draft_state = "round_interactive"
        st.rerun()

    # ------------------------------------------
    # ステップ E: 2巡目以降のインタラクティブ進行
    # ------------------------------------------
    elif st.session_state.draft_state == "round_interactive":
      cur_round = st.session_state.current_round
      st.subheader(f"📝 ドラフト 第 {cur_round} 巡目 指名")

      if cur_round % 2 == 1:
        order_teams = npb_teams
      else:
        order_teams = list(reversed(npb_teams))

      if "round_queue_idx" not in st.session_state:
        st.session_state.round_queue_idx = 0

      queue_idx = st.session_state.round_queue_idx

      if queue_idx < len(order_teams):
        current_team = order_teams[queue_idx]

        st.info(
            f"現在進行中: **第 {cur_round} 巡目** — 指名権: **{current_team}**"
            f" {'(あなた)' if current_team == user_team else ''}"
        )

        avail_df = df[~df["氏名"].isin(st.session_state.already_drafted)]

        if current_team == user_team:
          st.write("あなたの球団の指名選手を選んでください。")
          avail_sorted = avail_df.sort_values(by="基礎スコア", ascending=False)
          user_pick_n = st.selectbox(
              f"{user_team}の第{cur_round}巡目指名",
              avail_sorted["氏名"].tolist(),
              key=f"user_pick_r{cur_round}",
          )

          if st.button("この選手を指名する", type="primary"):
            if current_team not in st.session_state.draft_results:
              st.session_state.draft_results[current_team] = {}
            st.session_state.draft_results[current_team][cur_round] = (
                user_pick_n
            )
            st.session_state.already_drafted.add(user_pick_n)
            st.session_state.round_queue_idx += 1
            st.rerun()
        else:
          st.write(f"{current_team} が思考中……")
          if st.button(
              f"{current_team} の指名を進める", key=f"ai_btn_{queue_idx}"
          ):
            t_weights = st.session_state.team_weights[current_team]
            temp_df = avail_df.copy()
            temp_df["球団別スコア"] = temp_df["基礎スコア"] * temp_df[
                "カテゴリ"
            ].map(t_weights)
            top_cands = temp_df.sort_values(
                by="球団別スコア", ascending=False
            ).head(3)

            if len(top_cands) > 0:
              chosen = top_cands.sample(n=1).iloc[0]["氏名"]
            else:
              chosen = avail_df.iloc[0]["氏名"]

            if current_team not in st.session_state.draft_results:
              st.session_state.draft_results[current_team] = {}
            st.session_state.draft_results[current_team][cur_round] = chosen
            st.session_state.already_drafted.add(chosen)
            st.session_state.round_queue_idx += 1
            st.rerun()
      else:
        st.success(f"🎉 第 {cur_round} 巡目の指名がすべて終了しました！")

        col1, col2 = st.columns(2)
        with col1:
          if st.button(f"➡️ 次の巡目（{cur_round + 1}巡目）へ進む", type="primary"):
            st.session_state.current_round += 1
            st.session_state.round_queue_idx = 0
            st.rerun()
        with col2:
          if st.button("🏁 ドラフト会議を終了して全結果を見る"):
            st.session_state.draft_state = "draft_complete"
            st.rerun()

    # ------------------------------------------
    # ステップ F: 最終結果の一覧表示
    # ------------------------------------------
    elif st.session_state.draft_state == "draft_complete":
      st.subheader("🏆 ドラフト会議 最終指名結果一覧")

      max_r = max(
          [
              max(r_dict.keys())
              for r_dict in st.session_state.draft_results.values()
              if r_dict
          ],
          default=1,
      )

      summary_data = []
      for team in npb_teams:
        row = {"球団": f"★ {team} (あなた)" if team == user_team else team}
        for r in range(1, max_r + 1):
          p_name = st.session_state.draft_results.get(team, {}).get(r, "-")
          row[f"{r}位" if r == 1 else f"{r}巡目"] = p_name
        summary_data.append(row)

      st.dataframe(
          pd.DataFrame(summary_data), use_container_width=True, hide_index=True
      )


# 補助関数：AIが外れ1位を自動処理するロジック
def process_ai_hature_1st(df, npb_teams):
  confirmed_picks = st.session_state.temp_r1_picks
  loser_teams = st.session_state.pending_losers
  rem_pool = df[~df["氏名"].isin(confirmed_picks.keys())].copy()

  for team in loser_teams:
    if len(rem_pool) > 0:
      t_weights = st.session_state.team_weights[team]
      rem_pool["スコア"] = rem_pool["基礎スコア"] * rem_pool["カテゴリ"].map(
          t_weights
      )
      rem_pool = rem_pool.sort_values(by="スコア", ascending=False).reset_index(
          drop=True
      )
      top_n = rem_pool.head(5)
      chosen = top_n.sample(n=1).iloc[0]["氏名"]
      confirmed_picks[chosen] = team
      rem_pool = rem_pool[rem_pool["氏名"] != chosen].reset_index(drop=True)

  for p, t in confirmed_picks.items():
    if t not in st.session_state.draft_results:
      st.session_state.draft_results[t] = {}
    st.session_state.draft_results[t][1] = p
    st.session_state.already_drafted.add(p)
