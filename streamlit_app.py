import streamlit as st
from supabase import create_client
import random

# =========================
# ページ設定
# =========================
st.set_page_config(page_title="推し診断", page_icon="💖")
st.title("💖 あなたにぴったりの推し診断")

# =========================
# Supabase 接続（公式）
# =========================
supabase = create_client(
    st.secrets["supabase"]["url"],
    st.secrets["supabase"]["key"]
)

# =========================
# 名前入力
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
# 診断フォーム
# =========================
with st.form("diagnosis_form"):
    st.subheader("Q1. 好きな雰囲気はどっち？")
    answer_type = st.radio(
        "雰囲気",
        ["かわいい", "クール", "元気"],
        horizontal=True
    )

    st.subheader("Q2. 特に重視したいポイントは？")
    answer_charm = st.radio(
        "魅力",
        ["ダンス", "歌", "バラエティ"],
        horizontal=True
    )

    submitted = st.form_submit_button("運命の推しを見つける！")

# =========================
# 結果表示
# =========================
if submitted:
    response = (
        supabase
        .table("idols")
        .select("*")
        .eq("type", answer_type)
        .eq("charm", answer_charm)
        .execute()
    )

    if response.data:
        st.balloons()
        st.success("あなたにぴったりの推しが見つかりました！")

        oshi = random.choice(response.data)

        st.header(f"✨ {oshi['name']} ✨")
        st.subheader(f"（{oshi['group_name']}）")

        if "message" in oshi and oshi["message"]:
            st.info(f"推しポイント：{oshi['message']}")

    else:
        st.error("条件に一致するアイドルが見つかりませんでした")
        st.write("別の組み合わせを試してみてね！")
