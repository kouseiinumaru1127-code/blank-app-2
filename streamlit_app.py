import streamlit as st
from supabase import create_client

# =========================
# 初期設定
# =========================
st.set_page_config(page_title="推し診断", page_icon="💖")
st.title("💖 あなたにぴったりの推し診断")

supabase = create_client(
    st.secrets["supabase"]["url"],
    st.secrets["supabase"]["key"]
)

# =========================
# 名前入力セッション管理
# =========================
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

# =========================
# 診断フォーム
# =========================
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

# =========================
# 診断ロジック
# =========================
if submitted:

    score_type = {"かわいい": 0, "クール": 0, "元気": 0}
    score_charm = {"ダンス": 0, "歌": 0, "バラエティ": 0}

    # メイン影響
    score_type[q1] += 5
    score_charm[q2] += 4

    # サブ影響
    if q3 == "のんびり":
        score_type["かわいい"] += 2
        score_type["クール"] += 1
    elif q3 == "アクティブ":
        score_type["元気"] += 2
        score_charm["ダンス"] += 1
    else:
        score_type["クール"] += 2
        score_charm["バラエティ"] += 1

    if q4 == "スイーツ":
        score_type["かわいい"] += 2
    elif q4 == "お肉":
        score_type["元気"] += 2
    else:
        score_type["クール"] += 2

    best_type = max(score_type, key=score_type.get)
    best_charm = max(score_charm, key=score_charm.get)

    # =========================
    # DB検索
    # =========================
    query = supabase.table("idols").select("*")
    if group_choice != "全部":
        query = query.eq("group_name", group_choice)

    resp = query.execute()
    candidates = resp.data or []

    ranked = []
    for oshi in candidates:
        score = 0
        if oshi["type"] == best_type:
            score += 5
        if oshi["charm"] == best_charm:
            score += 5

        # 性格スコア加算
        score += score_type.get(oshi["type"], 0)
        score += score_charm.get(oshi["charm"], 0)

        ranked.append((score, oshi))

    ranked.sort(key=lambda x: x[0], reverse=True)

    # =========================
    # 結果表示
    # =========================
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

    # =========================
    # 🔥 ログ保存
    # =========================
    try:
        top_oshi_name = ranked[0][1]["name"] if ranked else None

        supabase.table("diagnosis_logs").insert({
            "user_name": st.session_state.user_name,
            "group_choice": group_choice,
            "q1": q1,
            "q2": q2,
            "q3": q3,
            "q4": q4,
            "result_type": best_type,
            "result_charm": best_charm,
            "top_oshi": top_oshi_name
        }).execute()

    except Exception as e:
        st.warning("利用データの保存に失敗しました")
        st.text(str(e))
