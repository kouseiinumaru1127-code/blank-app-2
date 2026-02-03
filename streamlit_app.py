import streamlit as st
from supabase import create_client
from collections import Counter

st.set_page_config(page_title="推し診断", page_icon="💖")
st.title("💖 あなたにぴったりの推し診断")

page = st.sidebar.radio("メニュー", ["💖 推し診断", "📊 クラス人気ランキング"])

supabase = create_client(
    st.secrets["supabase"]["url"],
    st.secrets["supabase"]["key"]
)

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

        st.subheader("Q4. ギャップのある人どう思う？")
        q4 = st.radio("ギャップ", ["大好物", "ちょっと好き", "安定がいい"])

        st.subheader("Q5. 推しに求めるポジションは？")
        q5 = st.radio("ポジション", ["センター", "支える人", "ムードメーカー"])

        st.subheader("Q6. 推しを見るとき一番テンション上がる瞬間は？")
        q6 = st.radio("瞬間", ["パフォーマンス中", "素の笑顔", "面白いことしてる時"])

        st.subheader("Q7. 推しとの理想の距離感は？")
        q7 = st.radio("距離感", ["近くに感じたい", "遠くから憧れたい", "友達みたいがいい"])

        st.subheader("Q8. 夜中に見たくなる推しはどれ？")
        q8 = st.radio("深夜タイプ", ["癒してくれる人", "かっこよすぎる人", "元気をくれる人"])

        st.subheader("Q9. 推しに言われたい言葉は？")
        q9 = st.radio("言葉", ["いつも頑張ってるね", "ついてこいよ", "一緒に楽しもう！"])

        st.subheader("Q10. グループで目で追っちゃうのは？")
        q10 = st.radio("目で追う人", ["控えめな人", "オーラある人", "騒いでる人"])

        submitted = st.form_submit_button("運命の推しを見つける！")

    # ================= 診断ロジック =================
    if submitted:

        score_type = {"かわいい": 0, "クール": 0, "元気": 0}
        score_charm = {"ダンス": 0, "歌": 0, "バラエティ": 0}

        # 強い軸
        if "守ってあげたくなる" in q1: score_type["かわいい"] += 5
        elif "近寄りがたい" in q1: score_type["クール"] += 5
        else: score_type["元気"] += 5

        if q2_style == "かわいい系": score_type["かわいい"] += 4
        elif q2_style == "清楚系":
            score_type["かわいい"] += 2
            score_type["クール"] += 1
        else: score_type["クール"] += 4

        score_charm[q3] += 4

        # 補助軸
        if q4 == "大好物":
            score_type["クール"] += 2
            score_charm["バラエティ"] += 2
        elif q4 == "安定がいい":
            score_type["かわいい"] += 2

        if q5 == "センター": score_type["クール"] += 2
        elif q5 == "支える人": score_type["かわいい"] += 2
        else: score_type["元気"] += 2

        if q6 == "パフォーマンス中":
            score_charm["ダンス"] += 2
            score_charm["歌"] += 1
        elif q6 == "素の笑顔":
            score_type["かわいい"] += 2
        else:
            score_type["元気"] += 2
            score_charm["バラエティ"] += 1

        if q7 == "近くに感じたい": score_type["かわいい"] += 2
        elif q7 == "遠くから憧れたい": score_type["クール"] += 2
        else: score_type["元気"] += 2

        if q8 == "癒してくれる人": score_type["かわいい"] += 2
        elif q8 == "かっこよすぎる人": score_type["クール"] += 2
        else: score_type["元気"] += 2

        if q9 == "いつも頑張ってるね": score_type["かわいい"] += 2
        elif q9 == "ついてこいよ": score_type["クール"] += 2
        else: score_type["元気"] += 2

        if q10 == "控えめな人": score_type["かわいい"] += 2
        elif q10 == "オーラある人": score_type["クール"] += 2
        else: score_type["元気"] += 2

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
            if oshi["type"] == best_type: score += 5
            if oshi["charm"] == best_charm: score += 5
            score += score_type.get(oshi["type"], 0)
            score += score_charm.get(oshi["charm"], 0)
            ranked.append((score, oshi))

        ranked.sort(key=lambda x: x[0], reverse=True)

        # 結果表示
        if ranked:
            st.balloons()
            st.success("ランキング形式で表示します！")

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
                "top_oshi": ranked[0][1]["name"] if ranked else None
            }).execute()
        except:
            pass

# ================= 📊 ランキング =================
elif page == "📊 クラス人気ランキング":

    st.header("📊 クラス人気ランキング")

    logs = supabase.table("diagnosis_logs").select("top_oshi").execute().data

    if logs:
        counts = Counter(log["top_oshi"] for log in logs if log["top_oshi"])
        ranking = counts.most_common()

        for i, (name, count) in enumerate(ranking, start=1):
            st.write(f"### {i}位：{name}（{count}票）")

        st.bar_chart(dict(ranking))
    else:
        st.info("まだデータがありません")
