import streamlit as st
import sqlite3
from collections import Counter

# ================= ページ設定 =================
st.set_page_config(
    page_title="推し診断",
    page_icon="💖"
)

st.title("💖 あなたにぴったりの推し診断")


# ================= SQLite3接続 =================

DB_NAME = "oshi_database.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


# ================= テーブル作成 =================

def init_db():

    with get_connection() as conn:

        # アイドル情報
        conn.execute("""
            CREATE TABLE IF NOT EXISTS idols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                group_name TEXT NOT NULL,
                type TEXT,
                charm TEXT,
                message TEXT
            )
        """)

        # 診断ログ
        conn.execute("""
            CREATE TABLE IF NOT EXISTS diagnosis_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                top_oshi TEXT NOT NULL,
                group_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


# データベース初期化
init_db()


# ================= DB操作関数 =================

# アイドル情報取得
def get_idols(group_name=None):

    with get_connection() as conn:

        if group_name and group_name != "全部":

            rows = conn.execute("""
                SELECT *
                FROM idols
                WHERE group_name = ?
            """, (group_name,)).fetchall()

        else:

            rows = conn.execute("""
                SELECT *
                FROM idols
            """).fetchall()

    return [dict(row) for row in rows]


# グループ一覧取得
def get_groups():

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT DISTINCT group_name
            FROM idols
            WHERE group_name IS NOT NULL
            ORDER BY group_name
        """).fetchall()

    return [row["group_name"] for row in rows]


# 診断結果保存
def save_diagnosis(user_name, top_oshi, group_name):

    with get_connection() as conn:

        conn.execute("""
            INSERT INTO diagnosis_logs
            (user_name, top_oshi, group_name)
            VALUES (?, ?, ?)
        """, (
            user_name,
            top_oshi,
            group_name
        ))


# 診断ログ取得
def get_logs():

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT *
            FROM diagnosis_logs
            ORDER BY created_at DESC, id DESC
        """).fetchall()

    return [dict(row) for row in rows]


# ================= メニュー =================

page = st.sidebar.radio(
    "メニュー",
    [
        "💖 推し診断",
        "📊 クラス人気ランキング"
    ]
)


# ================= 名前管理 =================

if "user_name" not in st.session_state:
    st.session_state.user_name = ""


# トップに戻る処理
def back_to_top():

    st.session_state.user_name = ""
    st.session_state.diagnosis_result = None


# 名前が未入力の場合
if not st.session_state.user_name:

    st.warning("まずは名前を入力してください")

    name_input = st.text_input("あなたの名前")

    if st.button("診断を始める"):

        if name_input.strip():

            st.session_state.user_name = name_input.strip()

            st.rerun()

        else:

            st.error("名前を入力してください")

    st.stop()


st.write(
    f"ようこそ、**{st.session_state.user_name}** さん！"
)


# ================= 💖 診断ページ =================

if page == "💖 推し診断":

    # グループ選択
    group_list = get_groups()
    group_list.insert(0, "全部")

    group_choice = st.selectbox(
        "グループを選んでね",
        group_list
    )

    # 診断フォーム
    with st.form("diagnosis_form"):

        st.subheader(
            "Q1. どんな雰囲気の人に一番惹かれる？"
        )

        q1 = st.radio(
            "雰囲気",
            [
                "守ってあげたくなる優しい雰囲気",
                "近寄りがたいけど目が離せない雰囲気",
                "場を明るくする太陽みたいな雰囲気"
            ]
        )

        st.subheader(
            "Q2. 見た目の系統で一番好きなのは？"
        )

        q2_style = st.radio(
            "系統",
            [
                "かわいい系",
                "清楚系",
                "クール系"
            ]
        )

        st.subheader(
            "Q3. 推しに一番求める魅力は？"
        )

        q3 = st.radio(
            "魅力",
            [
                "ダンス",
                "歌",
                "バラエティ"
            ]
        )

        st.subheader(
            "Q4. 推しの性格で一番好きなのは？"
        )

        q4_personality = st.radio(
            "性格",
            [
                "癒し系",
                "ミステリアス",
                "ムードメーカー"
            ]
        )

        submitted = st.form_submit_button(
            "運命の推しを見つける！"
        )


    # ================= 診断ロジック =================

    if submitted:

        score_type = {
            "かわいい": 0,
            "クール": 0,
            "元気": 0
        }

        score_charm = {
            "ダンス": 0,
            "歌": 0,
            "バラエティ": 0
        }

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


        # Q4 性格
        if q4_personality == "癒し系":

            score_type["かわいい"] += 2

        elif q4_personality == "ミステリアス":

            score_type["クール"] += 2

        else:

            score_type["元気"] += 2


        # 最も相性の良いタイプ
        best_type = max(
            score_type,
            key=score_type.get
        )

        best_charm = max(
            score_charm,
            key=score_charm.get
        )


        # ================= DB検索 =================

        candidates = get_idols(group_choice)

        ranked = []

        for oshi in candidates:

            score = 0

            if oshi["type"] == best_type:
                score += 5

            if oshi["charm"] == best_charm:
                score += 5

            score += score_type.get(
                oshi["type"], 0
            )

            score += score_charm.get(
                oshi["charm"], 0
            )

            ranked.append(
                (score, oshi)
            )


        ranked.sort(
            key=lambda x: x[0],
            reverse=True
        )


        # 診断結果をセッションに保存
        st.session_state.diagnosis_result = ranked


        # ================= ログ保存 =================

        if ranked:

            try:

                save_diagnosis(
                    st.session_state.user_name,
                    ranked[0][1]["name"],
                    ranked[0][1]["group_name"]
                )

            except sqlite3.Error as e:

                st.warning(
                    f"ログ保存に失敗しました：{e}"
                )


    # ================= 診断結果表示 =================

    if st.session_state.get("diagnosis_result") is not None:

        ranked = st.session_state.diagnosis_result

        if ranked:

            st.success(
                "あなたの推しランキング！"
            )

            for i, (score, oshi) in enumerate(
                ranked[:5],
                start=1
            ):

                st.write(
                    f"### {i}位：{oshi['name']}（{oshi['group_name']}）"
                )

                st.write(
                    f"スコア：{score}点"
                )

                if oshi.get("message"):

                    st.write(
                        f"📌 推しポイント：{oshi['message']}"
                    )

                st.write("---")

        else:

            st.warning(
                "対象のアイドルが登録されていません"
            )


    # トップに戻る
    st.button(
        "🔙 トップに戻る",
        on_click=back_to_top
    )


# ================= 📊 ランキングページ =================

elif page == "📊 クラス人気ランキング":

    st.header(
        "📊 クラス人気ランキング"
    )

    logs = get_logs()

    if not logs:

        st.info(
            "まだデータがありません"
        )

    else:

        # ================= 全体ランキング =================

        st.subheader(
            "🏆 全体ランキング"
        )

        counts = Counter(
            log["top_oshi"]
            for log in logs
            if log["top_oshi"]
        )

        ranking = counts.most_common()

        for i, (name, count) in enumerate(
            ranking,
            start=1
        ):

            st.write(
                f"{i}位：{name}（{count}票）"
            )


        st.bar_chart(
            dict(ranking)
        )

        st.markdown("---")


        # ================= グループ別ランキング =================

        st.subheader(
            "🎤 グループ別ランキング"
        )

        groups = sorted(
            {
                log["group_name"]
                for log in logs
                if log.get("group_name")
            }
        )

        for group in groups:

            st.markdown(
                f"### 【{group}】"
            )

            group_logs = [
                log
                for log in logs
                if log.get("group_name") == group
            ]

            group_counts = Counter(
                log["top_oshi"]
                for log in group_logs
            )

            for i, (name, count) in enumerate(
                group_counts.most_common(),
                start=1
            ):

                st.write(
                    f"{i}位：{name}（{count}票）"
                )


        st.markdown("---")


        # ================= 誰が誰推しか =================

        st.subheader(
            "🧑‍🤝‍🧑 みんなの推し一覧"
        )

        for log in logs:

            st.write(
                f"**{log['user_name']}** → "
                f"{log['top_oshi']} "
                f"（{log.get('group_name', '?')}）"
            )


    st.button(
        "🔙 トップに戻る",
        on_click=back_to_top
    )
