import streamlit as st
from supabase import create_client
from collections import Counter

st.set_page_config(page_title="推し診断", page_icon="💖")
st.title("💖 あなたにぴったりの推し診断")

# ================= Supabase接続 =================
supabase = create_client(
    st.secrets["supabase"]["url"],
    st.secrets["supabase"]["key"]
)

# ================= メニュー =================
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

# ================= 💖 診断ページ =================
if page == "💖 推し診断":

    with st.form("diagnosis_form"):

        st.subheader("Q1. どんな雰囲気の人に一番惹かれる？")
        q1 = st.radio("雰囲気", [
            "守ってあげたくなる優しい雰囲気",
            "近寄りがたいけど目が離せない雰囲気",
            "場を明るくする太陽みたいな雰囲気"
        ])

        st.subheader("Q2. 見た目の系統で一番好きなのは？")
        q2_style = st.radio("系統", ["かわいい系", "清楚系", "クール系"])

        st.subheader("Q3. 推しに一番求める魅力は？")
        q3 = st.radio("魅力", ["ダンス", "歌", "バラエティ"])

        # 🆕 追加質問
        st.subheader("Q4. 推しの性格で一番好きなのは？")
        q4_personality = st.radio("性格", ["癒し系", "ミステリアス", "ムードメーカー"])

        submitted = st.form_submit_button("運命の推しを見つける！")

    # ================= 診断ロジック =================
    if submitted:

        score_type = {"かわいい": 0, "クール": 0, "元気": 0}
        score_charm = {"ダンス": 0, "歌": 0, "バラエティ": 0}

        # Q1 雰囲気
        if "守ってあげたくなる" in q1:
            score_type["かわいい"] += 5
        elif "近寄りがたい" in q1:
            score_type["クール"] += 5
        else:
            score_type["元気"] += 5

        # Q2 見た目系統
        if q2_style == "かわいい系":
            score_type["かわいい"] += 4
        elif q2_style == "清楚系":
            score_type["かわいい"] += 2
            score_type["クール"] += 1
        else:
            score_type["クール"] += 4

        # Q3 魅力
        score_charm[q3] += 4

        # 🆕 Q4 性格反映
        if q4_personality == "癒し系":
            score_type["かわいい"] += 2
        elif q4_personality == "ミステリアス":
            score_type["クール"] += 2
        else:
            score_type["元気"] += 2

        best_type = max(score_type, key=score_type.get)
        best_charm = max(score_charm, key=score_charm.get)

        # DB検索
        query = supabase.table("idols").select("*")
        if group_choice != "全部":
            query = query.eq("group_name", group_choice)

        candidates = query.execute().data or []

        ranked = []
        for oshi in candidates:
            score = 0
            if oshi["type"] == best_type:
                score += 5
            if oshi["charm"] == best_charm:
                score += 5
            score += score_type.get(oshi["type"], 0)
            score += score_charm.get(oshi["charm"], 0)
            ranked.append((score, oshi))

        ranked.sort(key=lambda x: x[0], reverse=True)

        if ranked:
            st.balloons()
            st.success("あなたの推しランキング！")

            for i, (score, oshi) in enumerate(ranked[:5], start=1):
                st.write(f"### {i}位：{oshi['name']}（{oshi['group_name']}）")
                st.write(f"スコア：{score}点")
                if oshi.get("message"):
                    st.write(f"📌 推しポイント：{oshi['message']}")
                st.write("---")

            # ログ保存
            try:
                supabase.table("diagnosis_logs").insert({
                    "user_name": st.session_state.user_name,
                    "top_oshi": ranked[0][1]["name"],
                    "group_name": ranked[0][1]["group_name"]
                }).execute()
            except:
                st.warning("ログ保存に失敗しました")

            if st.button("🔙 トップに戻る"):
                st.session_state.user_name = ""
                st.rerun()

# ================= 📊 ランキングページ =================
elif page == "📊 クラス人気ランキング":

    st.header("📊 クラス人気ランキング")

    logs = supabase.table("diagnosis_logs").select("*").execute().data

    if not logs:
        st.info("まだデータがありません")
        st.stop()

    # 全体ランキング
    st.subheader("🏆 全体ランキング")
    counts = Counter(log["top_oshi"] for log in logs if log["top_oshi"])
    ranking = counts.most_common()

    for i, (name, count) in enumerate(ranking, start=1):
        st.write(f"{i}位：{name}（{count}票）")

    st.bar_chart(dict(ranking))
    st.markdown("---")

    # グループ別
    st.subheader("🎤 グループ別ランキング")
    groups = set(log["group_name"] for log in logs if log.get("group_name"))

    for group in groups:
        st.markdown(f"### 【{group}】")
        group_logs = [log for log in logs if log.get("group_name") == group]
        group_counts = Counter(log["top_oshi"] for log in group_logs)

        for i, (name, count) in enumerate(group_counts.most_common(), start=1):
            st.write(f"{i}位：{name}（{count}票）")

    st.markdown("---")

    # 誰が誰推しか
    st.subheader("🧑‍🤝‍🧑 みんなの推し一覧")
    for log in logs:
        st.write(f"**{log['user_name']}** → {log['top_oshi']}（{log.get('group_name','?')}）")
