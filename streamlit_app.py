import streamlit as st
from supabase import create_client

st.set_page_config(page_title="推し診断", page_icon="💖")
st.title("💖 あなたにぴったりの推し診断")

supabase = create_client(
    st.secrets["supabase"]["url"],
    st.secrets["supabase"]["key"]
)

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if not st.session_state.user_name:
    st.warning("まずは名前を入力してください")
    name_input = st.text_input("あなたの名前")

    if st.button("診断を始める"):
        if name_input.strip():
            st.session_state.user_name = name_input.strip()
            st.rerun()
    st.stop()

st.write(f"ようこそ、**{st.session_state.user_name}** さん！")

# =========================
# グループ選択
# =========================
groups_resp = supabase.table("idols").select("group_name").execute()
group_list = sorted(list({row["group_name"] for row in groups_resp.data if row["group_name"]}))
group_list.insert(0, "全部")

group_choice = st.selectbox("グループを選んでね", group_list)

with st.form("diagnosis_form"):
    st.subheader("Q1. 好きな雰囲気はどっち？")
    q1 = st.radio("雰囲気", ["かわいい", "クール", "元気"], horizontal=True)

    st.subheader("Q2. 特に重視したいポイントは？")
    q2 = st.radio("魅力", ["ダンス", "歌", "バラエティ"], horizontal=True)

    st.subheader("Q3. 休日の過ごし方は？")
    q3 = st.radio("過ごし方", ["のんびり", "アクティブ", "友達と遊ぶ"], horizontal=True)

    st.subheader("Q4. 好きな食べ物は？")
    q4 = st.radio("食べ物", ["スイーツ", "お肉", "お寿司"], horizontal=True)

    submitted = st.form_submit_button("運命の推しを見つける！")

if submitted:

    # -------------------------
    # 点数計算（type/charm）
    # -------------------------
    score_type = {"かわいい": 0, "クール": 0, "元気": 0}
    score_charm = {"ダンス": 0, "歌": 0, "バラエティ": 0}

    score_type[q1] += 3
    score_charm[q2] += 3

    if q3 == "のんびり":
        score_type["かわいい"] += 2
    elif q3 == "アクティブ":
        score_type["元気"] += 2
    else:
        score_type["クール"] += 2

    if q4 == "スイーツ":
        score_type["かわいい"] += 2
    elif q4 == "お肉":
        score_type["元気"] += 2
    else:
        score_type["クール"] += 2

    best_type = max(score_type, key=score_type.get)
    best_charm = max(score_charm, key=score_charm.get)

    # -------------------------
    # DB検索（グループ絞り込み）
    # -------------------------
    query = supabase.table("idols").select("*")

    if group_choice != "全部":
        query = query.eq("group_name", group_choice)

    resp = query.execute()

    candidates = resp.data or []

    # -------------------------
    # 候補に一致度スコアを付ける
    # -------------------------
    ranked = []
    for oshi in candidates:
        score = 0
        if oshi["type"] == best_type:
            score += 5
        if oshi["charm"] == best_charm:
            score += 5
        # ここに追加の一致度を増やせる
        ranked.append((score, oshi))

    ranked.sort(key=lambda x: x[0], reverse=True)

    # -------------------------
    # 結果表示（ランキング）
    # -------------------------
    if ranked and ranked[0][0] > 0:
        st.balloons()
        st.success("ランキング形式で表示します！")

        for i, (score, oshi) in enumerate(ranked[:5], start=1):
            st.write(f"### {i}位：{oshi['name']}（{oshi['group_name']}）")
            st.write(f"スコア：{score}点")
            if oshi.get("message"):
                st.write(f"📌 推しポイント：{oshi['message']}")
            st.write("---")

    else:
        st.error("条件に一致する推しが見つかりませんでした")
        st.write("別の組み合わせを試してみてね！")
