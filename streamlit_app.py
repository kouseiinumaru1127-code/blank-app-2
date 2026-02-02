import streamlit as st
from st_supabase_connection import SupabaseConnection
import random
pip install st-supabase-connection streamlit

# ページ設定
st.set_page_config(page_title="推し診断", page_icon="💖")
st.title("💖 あなたにぴったりの推し診断")

# 1. Supabase接続
conn = st.connection("supabase", type=SupabaseConnection)

# --- ログイン（名前入力）エリア ---
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if not st.session_state.user_name:
    st.warning("まずは名前を入力してください")
    name_input = st.text_input("あなたの名前")
    if st.button("診断を始める"):
        if name_input:
            st.session_state.user_name = name_input
            st.rerun()
    st.stop() # 名前がないとここより下は動きません

st.write(f"ようこそ、**{st.session_state.user_name}** さん！")

# --- 2. 診断フォーム ---
with st.form("diagnosis_form"):
    st.subheader("Q1. 好きな雰囲気はどっち？")
    # ここの選択肢は、Supabaseの 'type' カラムの中身と文字を合わせてください
    answer_type = st.radio("雰囲気", ["かわいい", "クール", "元気"], horizontal=True)

    st.subheader("Q2. 特に重視したいポイントは？")
    # ここの選択肢は、Supabaseの 'charm' カラムの中身と文字を合わせてください
    answer_charm = st.radio("魅力", ["ダンス", "歌", "バラエティ"], horizontal=True)

    submitted = st.form_submit_button("運命の推しを見つける！")

# --- 3. 結果の判定と表示 ---
if submitted:
    # Supabaseから条件に合うアイドルを検索
    # type と charm が両方一致するデータを探す
    response = conn.table("idols").select("*")\
        .eq("type", answer_type)\
        .eq("charm", answer_charm)\
        .execute()
    
    # 診断結果のログを保存（課題の要件：利用データの保存）
    log_data = {
        "user_name": st.session_state.user_name,
        "selected_type": answer_type,
        "selected_charm": answer_charm,
    }
    # ログ用テーブル 'diagnosis_logs' があればここに保存
    # conn.table("diagnosis_logs").insert(log_data).execute() 

    if len(response.data) > 0:
        st.balloons()
        st.success("あなたにぴったりの推しが見つかりました！")
        
        # マッチした中から1人を表示
        oshi = response.data[0] 
        
        st.header(f"✨ {oshi['name']} ✨")
        st.subheader(f"（{oshi['group_name']}）")
        st.info(f"推しポイント：{oshi['message']}")
        
    else:
        st.error("条件に完全一致するアイドルがまだ登録されていません...")
        st.write("別の組み合わせを試してみてね！")
