import random
import pandas as pd
import streamlit as st

# ページの設定
st.set_page_config(
    page_title="プロ野球ドラフト会議シミュレーター", page_icon="⚾", layout="wide"
)

st.title("⚾ プロ野球ドラフト会議シミュレーター")

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

  # ドラフトの進行ステージ管理 ("config", "round1_done", "round2")
  if "draft_stage" not in st.session_state:
    st.session_state.draft_stage = "config"
    st.session_state.round1_results = {}
    st.session_state.round2_results = {}
    st.session_state.lottery_logs = []

  # --- 2. 画面の切り替え ---
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

    # データの加工
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

    # --- ステップ1: 1位指名入札フェーズ ---
    if st.session_state.draft_stage == "config":
      st.subheader("📝 プロ野球ドラフト会議：1位指名 入札")
      st.write("各球団が1位指名する選手に入札します。競合した場合は抽選を行います。")

      default_sorted = df.sort_values(by="基礎スコア", ascending=False)
      user_choice = st.selectbox(
          f"{user_team}で1位入札する選手を選ぶ",
          default_sorted["氏名"].tolist(),
      )

      if st.button("🔔 1位入札を確定して抽選を行う", type="primary"):
        # 各球団の入札
        bids = {}
        for team in npb_teams:
          if team == user_team:
            bids[team] = user_choice
          else:
            t_weights = st.session_state.team_weights[team]
            temp_df = df.copy()
            temp_df["球団別スコア"] = temp_df["基礎スコア"] * temp_df[
                "カテゴリ"
            ].map(t_weights)
            top_candidates = temp_df.sort_values(
                by="球団別スコア", ascending=False
            ).head(5)
            if len(top_candidates) > 0:
              bids[team] = top_candidates.sample(n=1).iloc[0]["氏名"]
            else:
              bids[team] = temp_df.iloc[0]["氏名"]

        # 競合集計
        player_bids = {}
        for team, player in bids.items():
          if player not in player_bids:
            player_bids[player] = []
          player_bids[player].append(team)

        confirmed_picks = {}
        loser_teams = []
        logs = []

        logs.append("### 【1位入札・抽選結果】")
        for player, competing_teams in player_bids.items():
          if len(competing_teams) == 1:
            winner = competing_teams[0]
            confirmed_picks[player] = winner
            logs.append(
                f"- **{player}**: **{winner}** が単独指名で交渉権獲得！"
            )
          else:
            winner = random.choice(competing_teams)
            confirmed_picks[player] = winner
            losers = [t for t in competing_teams if t != winner]
            loser_teams.extend(losers)
            losers_str = ", ".join(losers)
            logs.append(
                f"- 🔥 **{player}** ({len(competing_teams)}球団競合): 抽選の結果、**{winner}** が交渉権獲得！（外れ: {losers_str}）"
            )

        # 外れ1位の処理
        remaining_pool = df[~df["氏名"].isin(confirmed_picks.keys())].copy()
        logs.append("\n### 【外れ1位 指名結果】")
        for team in loser_teams:
          if len(remaining_pool) > 0:
            t_weights = st.session_state.team_weights[team]
            remaining_pool["スコア"] = remaining_pool[
                "基礎スコア"
            ] * remaining_pool["カテゴリ"].map(t_weights)
            remaining_pool = remaining_pool.sort_values(
                by="スコア", ascending=False
            ).reset_index(drop=True)
            top_n_pool = remaining_pool.head(5)
            hature_player = top_n_pool.sample(n=1).iloc[0]["氏名"]
            confirmed_picks[hature_player] = team
            remaining_pool = remaining_pool[
                remaining_pool["氏名"] != hature_player
            ].reset_index(drop=True)
            logs.append(f"- 🔄 **{team}**: **{hature_player}** を外れ1位指名")

        # 結果をセッションに保存してステージを進める
        st.session_state.round1_results = {
            t: p for p, t in confirmed_picks.items()
        }
        st.session_state.lottery_logs = logs
        st.session_state.draft_stage = "round1_done"
        st.rerun()

    # --- ステップ2: 1位結果発表 ＆ 2巡目へ進む ---
    elif st.session_state.draft_stage == "round1_done":
      st.subheader("🎯 第1回選択希望選手（1位指名）確定")

      for log in st.session_state.lottery_logs:
        st.markdown(log)

      st.divider()
      if st.button("➡️ 2巡目（ウェーバー指名）に進む", type="primary"):
        st.session_state.draft_stage = "round2_in_progress"
        st.rerun()

    # --- ステップ3: 2巡目（ウェーバー順）進行フェーズ ---
    elif st.session_state.draft_stage in [
        "round2_in_progress",
        "draft_finished",
    ]:
      st.subheader("📝 ドラフト2巡目（ウェーバー指名）")

      # 2巡目のウェーバー順（実際のNPBに倣い、1位の逆順や固定順など）
      weber_teams = list(reversed(npb_teams))

      # まだ2巡目指名が済んでいない場合、順番に処理
      if st.session_state.draft_stage == "round2_in_progress":
        # 1位までに取られた選手を除外したプール
        already_picked = list(st.session_state.round1_results.values())
        remaining_pool = df[~df["氏Name" if "氏Name" in df.columns else "氏名"].isin(already_picked)].copy() # 念のため
        # 正しくは "氏名"
        remaining_pool = df[~df["氏名"].isin(already_picked)].copy()

        sec_results = {}
        sec_logs = []

        for team in weber_teams:
          if len(remaining_pool) > 0:
            t_weights = st.session_state.team_weights[team]
            remaining_pool["スコア"] = remaining_pool[
                "基礎スコ>ア"
                if "基礎スコ>ア" in remaining_pool.columns
                else "基礎スコア"
            ] * remaining_pool["カテゴリ"].map(t_weights)
            remaining_pool = remaining_pool.sort_values(
                by="スコア", ascending=False
            ).reset_index(drop=True)

            top_n_pool = remaining_pool.head(3)
            chosen = top_n_pool.sample(n=1).iloc[0]["氏名"]
            sec_results[team] = chosen
            remaining_pool = remaining_pool[
                remaining_pool["氏名"] != chosen
            ].reset_index(drop=True)
            sec_logs.append(f"- **{team}**: **{chosen}** を指名")

        st.session_state.round2_results = sec_results
        st.session_state.sec_logs = sec_logs
        st.session_state.draft_stage = "draft_finished"
        st.rerun()

      # --- ステップ4: 最終結果発表 ---
      if st.session_state.draft_stage == "draft_finished":
        st.success("🎉 全日程のドラフト会議が終了しました！")

        st.subheader("📜 2巡目 指名経過ログ")
        for log in st.session_state.get("sec_logs", []):
          st.markdown(log)

        st.divider()
        st.subheader("🏆 ドラフト指名 最終結果一覧（1位 ＆ 2巡目）")

        final_summary = []
        for team in npb_teams:
          p1_name = st.session_state.round1_results.get(team, "不明")
          p1_row = (
              df[df["氏名"] == p1_name].iloc[0]
              if p1_name in df["氏名"].values
              else None
          )

          p2_name = st.session_state.round2_results.get(team, "指名漏れ")
          p2_row = (
              df[df["氏Name" if "氏Name" in df.columns else "氏名"] == p2_name].iloc[0]
              if p2_name in df["氏名"].values
              else None
          )

          final_summary.append({
              "球団": f"★ {team} (あなた)" if team == user_team else team,
              "1位 指名選手": p1_name,
              "1位(区分/守備)": (
                  f"{p1_row['区分']} / {p1_row['守備位置']}"
                  if p1_row is not None
                  else ""
              ),
              "2巡目 指名選手": p2_name,
              "2巡目(区分/守備)": (
                  f"{p2_row['区分']} / {p2_row['守備位置']}"
                  if p2_row is not None
                  else ""
              ),
          })

        st.dataframe(
            pd.DataFrame(final_summary),
            use_container_width=True,
            hide_index=True,
        )

        if st.button("🔄 最初からやり直す"):
          st.session_state.draft_stage = "config"
          st.rerun()
