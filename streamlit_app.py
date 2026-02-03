import streamlit as st
from supabase import create_client
from collections import Counter

st.set_page_config(page_title="推し診断", page_icon="💖")
st.title("💖 あなたにぴったりの推し診断")

# ✅ 先にSupabase接続
supabase = create_client(
    st.secrets["supabase"]["url"],
    st.secrets["supabase"]["key"]
)

page = st.sidebar.radio("メニュー", ["💖 推し診断", "📊 クラス人気ランキング"])


# ================= 名前管理 =================
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

# ================= グループ選択 =================
groups_resp = supabase.table("idols").select("group_name").execute()
group_list = sorted(list({row["group_name"] for row in groups_resp.data if row["group_name"]}))
group_list.insert(0, "全部")
group_choice = st.selectbox("グループを選んでね", group_list)

# ================= 診断ページ =================
if page == "💖 推し診断":

    with st.form("diagnosis_form"):
        q1 = st.radio("Q1. 惹かれる雰囲気", ["守ってあげたくなる", "近寄りがたい", "太陽みたい"])
        q2_style = st.radio("Q2. 見た目の系統", ["かわいい系", "清楚系", "クール系"])
        q3 = st.radio("Q3. 推しの魅力", ["ダンス", "歌", "バラエティ"])
        submitted = st.form_submit_button("診断する")

    if submitted:

        score_type = {"かわいい": 0, "クール": 0, "元気": 0}
        score_charm = {"ダンス": 0, "歌": 0, "バラエティ": 0}

        if q1 == "守ってあげたくなる": score_type["かわいい"] += 5
        elif q1 == "近寄りがたい": score_type["クール"] += 5
        else: score_type["元気"] += 5

        if q2_style == "かわいい系": score_type["かわいい"] += 4
        elif q2_style == "清楚系":
            score_type["かわいい"] += 2
            score_type["クール"] += 1
        else: score_type["クール"] += 4

        score_charm[q3] += 4

        best_type = max(score_type, key=score_type.get)
        best_charm = max(score_charm, key=score_charm.get)

        query = supabase.table("idols").select("*")
        if group_choice != "全部":
            query = query.eq("group_name", group_choice)

        candidates = query.execute().data or []

        ranked = []
        for oshi in candidates:
            score = 0
            if oshi["type"] == best_type: score += 5
            if oshi["charm"] == best_charm: score += 5
            ranked.append((score, oshi))

        ranked.sort(key=lambda x: x[0], reverse=True)

        if ranked:
            st.success(f"あなたの推しは **{ranked[0][1]['name']}** 💖")

            supabase.table("diagnosis_logs").insert({
                "user_name": st.session_state.user_name,
                "top_oshi": ranked[0][1]["name"]
            }).execute()

            if st.button("🔙 トップに戻る"):
                st.session_state.user_name = ""
                st.rerun()

# ================= ランキング =================
elif page == "📊 クラス人気ランキング":

    st.header("📊 クラス人気ランキング")

    logs = supabase.table("diagnosis_logs").select("top_oshi").execute().data

    if logs:
        counts = Counter(log["top_oshi"] for log in logs if log["top_oshi"])
        ranking = counts.most_common()

        for i, (name, count) in enumerate(ranking, start=1):
            st.write(f"{i}位：{name}（{count}票）")

        st.bar_chart(dict(ranking))
    else:
        st.info("まだデータがありません")
