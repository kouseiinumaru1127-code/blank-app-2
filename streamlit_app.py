import streamlit as st
from supabase import create_client

# --------------------
# 初期設定
# --------------------
st.set_page_config(page_title="推し診断", page_icon="💖")
st.title("💖 あなたにぴったりの推し診断")

supabase = create_client(
    st.secrets["supabase"]["url"],
    st.secrets["supabase"]["key"]
)

# --------------------
# ユーザー名入力
# --------------------
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

# --------------------
# グループ一覧取得
# --------------------
groups_resp = supabase.table("groups").select("id, name").execute()
groups = groups_resp.data or []

group_map = {g["name"]: g["id"] for g in groups}
group_names = ["全部"] + list(group_map.keys())

group_choice = st.selectbox("推しグループを選んでね", group_names)

# --------------------
# 診断フォーム
# --------------------
with st.form("diagnosis_form"):
    st.subheader("Q1. 好きな雰囲気は？")
    q1 = st.radio("雰囲気", ["かわいい", "クール", "元気"], horizontal=True)

    st.subheader("Q2. 一番重視する魅力は？")
    q2 = st.radio("魅力", ["ダンス", "歌", "バラエティ"], horizontal=True)

    st.subheader("Q3. 休日の過ごし方は？")
    q3 = st.radio("休日", ["のんびり", "アクティブ", "友達と遊ぶ"], horizontal=True)

    st.subheader("Q4. 好きな食べ物は？")
    q4 = st.radio("食べ物", ["スイーツ", "お肉", "お寿司"], horizontal=True)

    submitted = st.form_submit_button("診断する！")

# --------------------
# 診断ロジック
# --------------------
if submitted:
    score_type = {"かわいい": 0, "クール": 0, "元気": 0}
    score_charm = {"ダンス": 0, "歌": 0, "バラエティ": 0}

    score_type[q1] += 3
    sco
