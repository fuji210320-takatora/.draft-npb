import pandas as pd
import streamlit as st

# ページの設定
st.set_page_config(
    page_title="プロ野球ドラフトシミュレーター", page_icon="⚾", layout="centered"
)

# スタイリング（カード風デザインや見栄えの調整）
st.markdown(
    """
    <style>
    .main-card {
        background-color: #fcfbfa;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e0dede;
        margin-bottom: 20px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("⚾ ドラフトシミュレーター")

# --- 1. スプレッドシートデータの読み込み ---
SHEET_ID = "1Qd_GNT-V0Ololma_QpIAhgEzLSFXlsv8sMG99espI90"
# 従来の export?format=csv ではなく、gviz/tq を使う
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

  # --- 2. 担当球団を選ぶUI（画像のデザインを再現） ---
  st.markdown("### 担当する球団を選ぶ")
  st.write("選んだ球団の指名だけ、あなたが決めます。")

  # 12球団リスト（セ・パ交互、または画像風配置）
  teams_data = [
      ("セ 阪神", "阪神"),
      ("セ DeNA", "DeNA"),
      ("セ 巨人", "巨人"),
      ("セ 中日", "中日"),
      ("セ 広島", "広島"),
      ("セ ヤクルト", "ヤクルト"),
      ("パ ソフトバンク", "ソフトバンク"),
      ("パ 日本ハム", "日本ハム"),
      ("パ オリックス", "オリックス"),
      ("パ 楽天", "楽天"),
      ("パ 西武", "西武"),
      ("パ ロッテ", "ロッテ"),
  ]

  # セッション状態で選択球団を保持
  if "user_team" not in st.session_state:
    st.session_state.user_team = "阪神"

  # 2列グリッドでボタンを配置
  cols = st.columns(2)
  for i, (label, team_name) in enumerate(teams_data):
    col = cols[i % 2]
    with col:
      # 選択されている球団は色を変えるなどの演出（primaryボタンを使用）
      is_selected = st.session_state.user_team == team_name
      button_type = "primary" if is_selected else "secondary"

      if st.button(
          label, key=f"team_btn_{team_name}", use_container_width=True, type=button_type
      ):
        st.session_state.user_team = team_name
        st.rerun()

  st.divider()

  # --- 3. サイドバー：カテゴリ別係数設定 ---
  st.sidebar.header("🎛️ 評価係数チューニング")
  st.sidebar.write("各層の評価にボーナスをかけて好みを反映します。")

  weights = {}
  st.sidebar.subheader("高校生")
  c1, c2 = st.sidebar.columns(2)
  weights["高投"] = c1.slider("高投", 0.0, 2.0, 1.0, 0.1)
  weights["高捕"] = c2.slider("高捕", 0.0, 2.0, 1.0, 0.1)
  c3, c4 = st.sidebar.columns(2)
  weights["高内"] = c3.slider("高内", 0.0, 2.0, 1.0, 0.1)
  weights["高外"] = c4.slider("高外", 0.0, 2.0, 1.0, 0.1)

  st.sidebar.subheader("大学生")
  c5, c6 = st.sidebar.columns(2)
  weights["大投"] = c5.slider("大投", 0.0, 2.0, 1.0, 0.1)
  weights["大捕"] = c6.slider("大捕", 0.0, 2.0, 1.0, 0.1)
  c7, c8 = st.sidebar.columns(2)
  weights["大内"] = c7.slider("大内", 0.0, 2.0, 1.0, 0.1)
  weights["大外"] = c8.slider("大外", 0.0, 2.0, 1.0, 0.1)

  st.sidebar.subheader("社会人・その他")
  c9, c10 = st.sidebar.columns(2)
  weights["社投"] = c9.slider("社投", 0.0, 2.0, 1.0, 0.1)
  weights["社捕"] = c10.slider("社捕", 0.0, 2.0, 1.0, 0.1)
  c11, c12 = st.sidebar.columns(2)
  weights["社内"] = c11.slider("社内", 0.0, 2.0, 1.0, 0.1)
  weights["社外"] = c12.slider("社外", 0.0, 2.0, 1.0, 0.1)
  weights["他"] = st.sidebar.slider("その他", 0.0, 2.0, 1.0, 0.1)

  # --- 4. データの前処理とスコア計算 ---
  df = df_raw.copy()


  def get_category_key(row):
    aff = str(row["所属"])
    pos = str(row["ポジション"])
    prefix = "他"
    if "高" in aff:
      prefix = "高"
    elif "大" in aff:
      prefix = "大"
    elif "社会人" in aff or "社" in aff or "独立" in aff:
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
    return key if key in weights else "他"


  df["カテゴリ"] = df.apply(get_category_key, axis=1)
  df["係数"] = df["カテゴリ"].map(weights).fillna(1.0)
  df["最終評価スコア"] = df["評価点"] * df["係数"]
  df_sorted = df.sort_values(by="最終評価スコア", ascending=False).reset_index(
      drop=True
  )

  # --- 5. ドラフト実行画面 ---
  st.subheader(f"🎯 ドラフトシミュレーション (担当: {st.session_state.user_team})")

  # 1位指名の順番（セ・パ混合やウェーバーなど、まずはシンプルに固定順）
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

  # 自分が担当する球団がどこにあるか確認
  user_team = st.session_state.user_team

  # 仮想のドラフト進行用セッション
  if "draft_done" not in st.session_state:
    st.session_state.draft_done = False
    st.session_state.available_players = df_sorted.copy()
    st.session_state.draft_results = []
    st.session_state.user_choice = df_sorted.iloc[0][
        "選手名"
    ]  # デフォルトは最上位選手

  # まだ指名していない場合、ユーザーのターンで止まるような設計に拡張可能
  if st.button("ドラフト1位指名を開始する", type="primary"):
    results = []
    pool = df_sorted.copy()

    for team in npb_teams:
      if team == user_team:
        # ユーザー担当球団は、プールから自分が選んだ選手を取る（簡易的にセレクトボックス等で選ばせることも可能）
        chosen_name = st.session_state.user_choice
        # プールから該当選手を探す
        player_row = pool[pool["選手名"] == chosen_name]
        if not player_row.empty:
          p = player_row.iloc[0]
          results.append({
              "球団": f"★ {team} (あなた)",
              "指名選手": p["選手名"],
              "所属": p["所属"],
              "ポジション": p["ポジション"],
              "スコア": round(p["最終評価スコア"], 2),
          })
          pool = pool[pool["選手名"] != chosen_name].reset_index(drop=True)
        else:
          # すでに取られてたらプールの一位
          p = pool.iloc[0]
          results.append({
              "球団": f"★ {team} (あなた)",
              "指名選手": p["選手名"],
              "所属": p["所属"],
              "ポジション": p["ポジション"],
              "スコア": round(p["最終評価スコア"], 2),
          })
          pool = pool.iloc[1:].reset_index(drop=True)
      else:
        # AI球団は評価スコア最上位を指名
        if len(pool) > 0:
          p = pool.iloc[0]
          results.append({
              "球団": team,
              "指名選手": p["選手名"],
              "所属": p["所属"],
              "ポジション": p["ポジション"],
              "スコア": round(p["最終評価スコア"], 2),
          })
          pool = pool.iloc[1:].reset_index(drop=True)

    st.session_state.draft_results = results
    st.session_state.draft_done = True

  # ユーザーが自分の指名選手を選べるようにするセレクトボックス
  st.write("---")
  st.subheader("📝 あなたの球団の1位指名選手選択")
  selected_pick = st.selectbox(
      f"{user_team}の1位指名選手を選ぶ",
      df_sorted["選手名"].tolist(),
      index=0,
  )
  st.session_state.user_choice = selected_pick

  # 結果の表示
  if st.session_state.draft_done and st.session_state.draft_results:
    st.subheader("🏆 1位指名 結果速報")
    df_res = pd.DataFrame(st.session_state.draft_results)
    st.table(df_res)
