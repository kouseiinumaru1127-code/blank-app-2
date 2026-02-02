import streamlit as st
from st_supabase_connection import SupabaseConnection
import random

# =========================
# ページ設定
# =========================
st.set_page_config(
    page_title="推し診断",
    page_icon="💖"
)

st.title("💖 あなたにぴったりの推し診断")

# =========================
# Supabase 接続
# =========================
conn = st.connection("supabase", type=SupabaseConnection)

# =========================
# ログイン（名前入力）
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
# 診断結果
# =========================
if submitted:
    response = (
        conn.table("idols")
        .select("*")
        .eq("type", answer_type)
        .eq("charm", answer_charm)
        .execute()
    )

    # デバッグしたいときは有効化
    # st.write(response.data)

    if response.data and len(response.data) > 0:
        st.balloons()
        st.success("あなたにぴったりの推しが見つかりました！")

        # ランダムで1人選ぶ
        oshi = random.choice(response.data)

        st.header(f"✨ {oshi['name']} ✨")
        st.subheader(f"（{oshi['group_name']}）")

        # message カラムがあれば表示（無くても落ちない）
        if "message" in oshi and oshi["message"]:
            st.info(f"推しポイント：{oshi['message']}")

    else:
        st.error("条件に一致するアイドルが見つかりませんでした")
        st.write("別の組み合わせを試してみてね！")
