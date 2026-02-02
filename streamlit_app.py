import streamlit as st
from supabase import create_client
import random

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

with st.form("diagnosis_form"):
    st.subheader("Q1. 好きな雰囲気はどっち？")
    q1 = st.radio("雰囲気", ["かわいい", "クール", "元気"], horizontal=True)

    st.subheader("Q2. 特に重視したいポイントは？")
    q2 = st.radio("魅力", ["ダンス", "歌", "バラエティ"], horizontal=True)

    # 追加質問（点数方式）
    st.subheader("Q3. 休日の過ごし方は？")
    q3 = st.radio("過ごし方", ["のんびり", "アクティブ", "友達と遊ぶ"], horizontal=True)

    st.subheader("Q4. 好きな食べ物は？")
    q4 = st.radio("食べ物", ["スイーツ", "お肉", "お寿司"], horizontal=True)

    submitted = st.form_submit_button("運命の推しを見つける！")

if submitted:

    # 点数テーブル（ここを好きに変更可能）
    score_type = {"かわいい": 0, "クール": 0, "元気": 0}
    score_charm = {"ダンス": 0, "歌": 0, "バラエティ": 0}

    # Q1
    score_type[q1] += 3

    # Q2
    score_charm[q2] += 3

    # Q3（例：のんびり→かわいい寄り、アクティブ→元気寄り、友達→クール寄り）
    if q3 == "のんびり":
        score_type["かわいい"] += 2
    elif q3 == "アクティブ":
        score_type["元気"] += 2
    else:
        score_type["クール"] += 2

    # Q4（例：スイーツ→かわいい、肉→元気、お寿司→クール）
    if q4 == "スイーツ":
        score_type["かわいい"] += 2
    elif q4 == "お肉":
        score_type["元気"] += 2
    else:
        score_type["クール"] += 2

    # 点数が高いtype/charmを選ぶ
    best_type = max(score_type, key=score_type.get)
    best_charm = max(score_charm, key=score_charm.get)

    # DB検索（最終的に一番近い推しを表示）
    response = (
        supabase
        .table("idols")
        .select("*")
        .eq("type", best_type)
        .eq("charm", best_charm)
        .execute()
    )

    if response.data:
        st.balloons()
        st.success("あなたにぴったりの推しが見つかりました！")

        oshi = random.choice(response.data)
        st.header(f"✨ {oshi['name']} ✨")
        st.subheader(f"（{oshi['group_name']}）")
        if oshi.get("message"):
            st.write(f"📌 推しポイント：{oshi['message']}")

    else:
        st.error("条件に一致する推しが見つかりませんでした")
        st.write("別の組み合わせを試してみてね！")
