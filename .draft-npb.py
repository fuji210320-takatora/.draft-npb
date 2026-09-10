import random
import pandas as pd
import streamlit as st

# ページの設定
st.set_page_config(
    page_title="プロ野球ドラフトシミュレーター（2巡目対応版）",
    page_icon="⚾",
    layout="wide",
)

st.title("⚾ プロ野球ドラフトシミュレーター")

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

  # --- 2. 画面の切り替え（設定画面 vs ドラフト実行画面） ---
  app_mode = st.radio(
      "画面を選択",
      ["📋 1. 各球団の設定・チューニング", "🏟️ 2. ドラフト会議会場"],
      horizontal=True,
  )

  # ==========================================
  # 【画面1】各球団の設定・チューニング画面
  # ==========================================
  if app_mode == "📋 1. 各球団の設定・チューニング":
    st.subheader("📋 担当球団 & 12球団の補正（好み）設定")
    st.write(
        "ここであなたが操作する球団や、各球団がどのカテゴリの選手を重視するかを設定します。"
    )

    # 担当球団の選択
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

    # 各球団の係数設定タブ
    st.markdown("#### 🎛️ 12球団のカテゴリ別補正スライダー")
    team_tabs = st.tabs(npb_teams)

    for i, team in enumerate(npb_teams):
      with team_tabs[i]:
        st.write(
            f"**{team} の好み設定** （スライダーが高いほどその層を好んで指名します）"
        )
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
  # 【画面2】ドラフト会議実行画面（1位 ＆ 2巡目）
  # ==========================================
  elif app_mode == "🏟️ 2. ドラフト会議会場":
    user_team = st.session_state.user_team
    st.info(
        f"現在の担当球団: **{user_team}** （設定画面からいつでも変更できます）"
    )

    # データの加工（カテゴリ判定と基礎スコア化）
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

    st.subheader("📝 1位指名 入札選手選択")
    default_sorted = df.sort_values(by="基礎スコア", ascending=False)
    user_choice = st.selectbox(
        f"{user_team}で1位入札する選手を選ぶ",
        default_sorted["氏名"].tolist(),
    )

    if st.button("🚀 ドラフト会議スタート（1位 ＆ 2巡目実行）", type="primary"):
      # ------------------------------------------
      # 【1位指名フェーズ】
      # ------------------------------------------
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

      confirmed_picks = {}  # {選手名: 球団名} (1位獲得者)
      loser_teams = []

      # 抽選処理
      for player, competing_teams in player_bids.items():
        if len(competing_teams) == 1:
          confirmed_picks[player] = competing_teams[0]
        else:
          winner = random.choice(competing_teams)
          confirmed_picks[player] = winner
          losers = [t for t in competing_teams if t != winner]
          loser_teams.extend(losers)

      # 外れ1位の処理
      remaining_pool = df[~df["氏名"].isin(confirmed_picks.keys())].copy()
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

      # 1位指名結果の逆引き辞書 {球団名: 選手名}
      first_round_results = {t: p for p, t in confirmed_picks.items()}

      # ------------------------------------------
      # 【2巡目指名フェーズ（ウェーバー順）】
      # ------------------------------------------
      # 2巡目は1巡目とは逆の順番（ウェーバー順：ここではシンプルにnpb_teamsの逆順、または指定順で回す）
      weber_teams = list(reversed(npb_teams))
      second_round_results = {}

      for team in weber_teams:
        if len(remaining_pool) > 0:
          t_weights = st.session_state.team_weights[team]
          remaining_pool["スコア"] = remaining_pool[
              "基礎スコア"
          ] * remaining_pool["カテゴリ"].map(t_weights)
          remaining_pool = remaining_pool.sort_values(
              by="スコア", ascending=False
          ).reset_index(drop=True)

          # 2巡目は上位3人からランダム、または最高評価の選手を獲得
          top_n_pool = remaining_pool.head(3)
          chosen_2nd = top_n_pool.sample(n=1).iloc[0]["氏名"]
          second_round_results[team] = chosen_2nd
          # プールから除外
          remaining_pool = remaining_pool[
              remaining_pool["氏名"] != chosen_2nd
          ].reset_index(drop=True)

      # ------------------------------------------
      # 【結果発表の表示】
      # ------------------------------------------
      st.success("🎉 ドラフト会議（1位 & 2巡目）が終了しました！")

      st.subheader("🏆 ドラフト指名 最終結果一覧")

      final_summary = []
      for team in npb_teams:
        # 1位選手
        p1_name = first_round_results.get(team, "不明")
        p1_row = (
            df[df["氏名"] == p1_name].iloc[0]
            if p1_name in df["氏名"].values
            else None
        )

        # 2巡目選手
        p2_name = second_round_results.get(team, "指名漏れ")
        p2_row = (
            df[df["氏名"] == p2_name].iloc[0]
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

      st.dataframe(pd.DataFrame(final_summary), use_container_width=True)
