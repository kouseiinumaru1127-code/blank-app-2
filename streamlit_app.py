import streamlit as st
from supabase import create_client
from collections import Counter

# =========================
# 初期設定
# =========================
st.set_page_config(page_title="推し診断", page_icon="💖")
st.title("💖 あなたにぴったりの推し診断")

page = st.sidebar.radio("メニュー", ["💖 推し診断", "📊 クラス人気ランキング"])

supabase = create_client(
    st.secrets["supabase"]["url"],
    st.secrets["supabase"]["key"]
)

# =========================
# 名前入力管理
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
# 💖 推し診断ページ
# =========================
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

        st.subheader("Q4. ギャップのある人どう思う？")
        q4 = st.radio("ギャップ", ["大好物", "ちょっと好き", "安定がいい"])

        st.subheader("Q5. 推しに求めるポジションは？")
        q5 = st.radio("ポジション", ["センター", "支える人", "ムードメーカー"])

        submitted = st.form_submit_button("運命の推しを見つける！")

    # =========================
    # 診断処理
    # =========================
    if submitted:

        score_type = {"かわいい": 0, "クール": 0, "元気": 0}
        score_charm = {"ダンス": 0, "歌": 0, "バラエティ": 0}

        # Q1 心理タイプ
        if "守ってあげたくなる" in q1:
            score_type["かわいい"] += 5
        elif "近寄りがたい" in q1:
            score_type["クール"] += 5
        else:
            score_type["元気"] += 5

        # Q2 見た目系統（強）
        if q2_style == "かわいい系":
            score_type["かわいい"] += 4
        elif q2_style == "清楚系":
            score_type["かわいい"] += 2
            score_type["クール"] += 1
        else:
            score_type["クール"] += 4

        # Q3 魅力
        score_charm[q3] += 4

        # Q4 ギャップ
        if q4 == "大好物":
            score_type["クール"] += 2
            score_charm["バラエティ"] += 2
        elif q4 == "ちょっと好き":
            score_type["元気"] += 1
        else:
            score_type["かわいい"] += 2

        # Q5 ポジション
        if q5 == "センター":
            score_type["クール"] += 2
        elif q5 == "支える人":
            score_type["かわいい"] += 2
        else:
            score_type["元気"] += 2

        best_type = max(score_type, key=score_type.get)
        best_charm = max(score_charm, key=score_charm.get)

        # ================= DB検索 =================
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
            score += score_type.get(oshi["type"], 0)
            score += score_charm.get(oshi["charm"], 0)
            ranked.append((score, oshi))

        ranked.sort(key=lambda x: x[0], reverse=True)

        # ================= 結果表示 =================
        if ranked and ranked[0][0] > 0:
            st.balloons()
            st.success("ランキング形式で表示します！")

            for i, (score, oshi) in enumerate(ranked[:5], start=1):
                st.write(f"### {i}位：{oshi['name']}（{oshi['group_name']}）")
                st.write(f"スコア：{score}点")
                if oshi.get("message"):
                    st.write(f"📌 推しポイント：{oshi['message']}")
                st.write("---")

        # 🔙 トップに戻る
        if st.button("🔙 トップに戻る"):
            st.session_state.user_name = ""
            st.rerun()

        # ================= ログ保存 =================
        try:
            top_oshi_name = ranked[0][1]["name"] if ranked else None

            supabase.table("diagnosis_logs").insert({
                "user_name": st.session_state.user_name,
                "group_choice": group_choice,
                "q1": q1,
                "q2_style": q2_style,
                "q3": q3,
                "q4": q4,
                "q5": q5,
                "result_type": best_type,
                "result_charm": best_charm,
                "top_oshi": top_oshi_name
            }).execute()

        except Exception as e:
            st.warning("ログ保存に失敗しました")
            st.text(str(e))


# =========================
# 📊 ランキングページ
# =========================
elif page == "📊 クラス人気ランキング":

    st.header("📊 クラスの推し人気ランキング")

    logs = supabase.table("diagnosis_logs").select("top_oshi").execute().data

    if not logs:
        st.info("まだ診断データがありません")
    else:
        counts = Counter(log["top_oshi"] for log in logs if log["top_oshi"])
        ranking = counts.most_common()

        for i, (name, count) in enumerate(ranking, start=1):
            st.write(f"### {i}位：{name}（{count}票）")

        st.bar_chart(dict(ranking))
