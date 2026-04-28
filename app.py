"""
株式会社イシクラ 入稿コンシェルジュアプリ
Streamlit Community Cloud にそのままデプロイ可能。
依存ライブラリ: streamlit, google-generativeai
"""

import streamlit as st
import google.generativeai as genai

# =============================================================================
# ▼▼▼ 設定エリア ▼▼▼
# =============================================================================

# Gemini API Key (Streamlit Secrets または直接指定)
# 運用時は Streamlit の Secrets (st.secrets["GEMINI_API_KEY"]) を推奨します
GEMINI_API_KEY = "AIzaSyD2iPzPWH4SNczwJY4jV-QQPy2WgsoD__E"

# =============================================================================
# ▼▼▼ データ定義エリア ▼▼▼
# ここを編集するだけでコンテンツを更新できます
# =============================================================================

PRINT_TYPES = [
    "卒業アルバム",
    "チラシ・フライヤー",
    "パンフレット・冊子",
    "名刺",
    "記念誌・社史",
    "学校案内・広報誌",
    "その他",
]

SOFTWARE_LIST = [
    "Adobe Illustrator",
    "Adobe Photoshop",
    "Adobe InDesign",
    "Microsoft PowerPoint",
    "PDF のみ（編集ソフトなし）",
    "その他",
]

FILE_FORMATS = [
    "PDF（推奨）",
    "ai（Illustratorデータ）",
    "psd（Photoshopデータ）",
    "indd（InDesignデータ）",
    "jpg / png（画像データ）",
    "その他",
]

EXTRA_FLOW_NOTES = {
    "卒業アルバム": [
        "写真データは原寸 350dpi 以上を強く推奨します（特に見開きページ）",
        "個人写真の掲載許諾（プライバシー）を事前に確認してください",
        "ページ順・名前表記の最終確認は学校側担当者と必ず行ってください",
        "表紙・背表紙・裏表紙の仕様（素材・加工）は担当者と事前打ち合わせが必要です",
        "データ入稿前に「ラフ台割（レイアウト構成表）」を共有いただけるとスムーズです",
    ],
    "チラシ・フライヤー": [
        "両面印刷の場合、表裏のデータは別ページまたは別ファイルで作成してください",
        "特色（蛍光色・金銀）指定がある場合は事前にご相談ください",
    ],
    "パンフレット・冊子": [
        "総ページ数は 4 の倍数になるよう調整してください（中綴じ・無線綴じ共通）",
        "本文と表紙で用紙・加工が異なる場合は仕様書を別途ご用意ください",
    ],
    "名刺": [
        "仕上がりサイズは通常 91mm × 55mm です",
        "文字サイズは 7pt 以上を推奨します（細い書体は 8pt 以上）",
    ],
    "記念誌・社史": [
        "写真・図版の権利（著作権・肖像権）を事前に整理しておいてください",
        "長期保存を考慮する場合、用紙・製本方法のご相談をお勧めします",
    ],
    "学校案内・広報誌": [
        "校名・住所・電話番号など公式情報の最終確認を学校担当者と行ってください",
        "掲載写真の肖像権・使用許諾を必ず取得してください",
    ],
}

EXTRA_CHECKS_BY_SOFTWARE = {
    "Adobe Illustrator": [
        "すべてのテキストオブジェクトをアウトライン化している",
        "リンク画像をすべて埋め込み済み（またはリンクファイルを同梱）",
        "アピアランス・効果（ドロップシャドウなど）を分割・統合済み",
        "オーバープリント設定に問題がない（白オブジェクトに誤設定なし）",
        "ドキュメントのカラーモードが CMYK になっている",
        "トリムマーク（トンボ）が正しく設定されている",
    ],
    "Adobe Photoshop": [
        "カラーモードが CMYK になっている",
        "解像度が原寸で 300〜350dpi 以上になっている",
        "レイヤーを統合して保存している",
        "保存形式は PDF または TIFF 推奨",
    ],
    "Adobe InDesign": [
        "フォントをアウトライン化、またはフォントファイルを同梱している",
        "リンクパネルでリンク切れが 0 件になっている",
        "「パッケージ」機能でデータをまとめている",
        "カラープロファイルが CMYK",
        "ページサイズと塗り足し設定が正しい",
    ],
    "Microsoft PowerPoint": [
        "フォントが埋め込まれているか、または PDF で入稿している",
        "※ PowerPoint データの直接入稿はリスクが高いため PDF 書き出しを推奨します",
        "カラーモードの変化（RGB→CMYK）を了承している",
    ],
    "PDF のみ（編集ソフトなし）": [
        "PDF 規格が PDF/X-1a または PDF/X-4 になっている",
        "フォントが埋め込まれている",
        "カラーモードが CMYK になっている",
    ],
}

COMMON_CHECKLIST = [
    "カラーモードは CMYK になっている",
    "仕上がりサイズで作成している",
    "塗り足し（上下左右各 3mm）が設定されている",
    "重要な文字・ロゴが断裁位置から 3mm 以上の余白を取っている",
    "画像解像度は原寸で 300〜350dpi 程度ある",
    "トンボ（トリムマーク）の設定が正しい",
    "透明効果・グラデーションの見た目を最終確認した",
    "入稿用データと編集用データを分けて保存している",
    "確認用 PDF でレイアウト崩れがないことを確認した",
    "ファイル名に全角文字・特殊文字が含まれていない",
]

FAQ_DATA = [
    {"q": "RGB のまま入稿するとどうなりますか？", "a": "印刷時に CMYK へ自動変換され、色がくすむ可能性があります。事前に変換して確認してください。"},
    {"q": "フォントをアウトライン化しないとどうなりますか？", "a": "文字化けやフォントの置き換えが発生するリスクがあります。必ずアウトライン化してください。"},
    {"q": "塗り足しがないとどうなりますか？", "a": "断裁時のズレで紙の端に白い地が出てしまう可能性があります。"},
    {"q": "画像解像度はどのくらい必要ですか？", "a": "印刷物では原寸で 300〜350dpi が目安です。"},
]

COMMON_FLOW_STEPS = [
    "仕上がり仕様の最終確認",
    "カラーモードを CMYK に設定",
    "塗り足し（3mm）の設定",
    "フォントのアウトライン化・埋め込み",
    "画像解像度の確認（300-350dpi）",
    "リンク画像の処理（埋め込み等）",
    "トンボ・断裁位置の確認",
    "PDF 書き出し（PDF/X-4推奨）",
    "セルフチェックリストの実行",
    "担当者へ入稿連絡",
]

# =============================================================================
# デザイン・ユーティリティ
# =============================================================================

def apply_custom_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap');
        html, body, [class*="css"] { font-family: 'Noto+Sans+JP', sans-serif; }
        .main { background-color: #f8f9fa; }
        h1, h2, h3 { color: #00529b; border-left: 5px solid #00529b; padding-left: 15px; margin-top: 1.5rem !important; }
        .stButton > button { border-radius: 20px; border: 1px solid #00529b; background-color: #white; color: #00529b; }
        .stButton > button:hover { background-color: #00529b; color: white; }
        .step-container { background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; margin-bottom: 8px; }
        .step-number { display: inline-block; width: 25px; height: 25px; background-color: #00529b; color: white; border-radius: 50%; text-align: center; line-height: 25px; font-weight: bold; margin-right: 10px; }
        /* チャット用スタイル */
        .chat-message { padding: 10px; border-radius: 10px; margin-bottom: 10px; }
        .user-message { background-color: #e3f2fd; border-left: 5px solid #2196f3; }
        .assistant-message { background-color: #f1f8e9; border-left: 5px solid #4caf50; }
        </style>
    """, unsafe_allow_html=True)

# =============================================================================
# ページ関数
# =============================================================================

def page_about():
    st.title("株式会社イシクラ 入稿コンシェルジュ")
    st.markdown("""
        <div style='padding: 20px; background-color: #e3f2fd; border-radius: 15px; border-left: 8px solid #00529b; margin-bottom: 25px;'>
            <h4 style='margin:0; color:#00529b;'>想い出をカタチに、未来へつなぐ。</h4>
            <p style='margin-top:10px;'>株式会社イシクラは、埼玉県さいたま市を拠点に、卒業アルバムや各種印刷物の制作を通じて、皆様の大切な瞬間を形にするお手伝いをしています。</p>
        </div>
    """, unsafe_allow_html=True)
    st.subheader("このアプリでできること")
    col1, col2 = st.columns(2)
    with col1:
        st.info("🎯 **入稿フローガイド**\n\n条件に合わせて最適な制作手順をご案内します。")
        st.info("🤖 **AIチャット相談**\n\nGemini AI が入稿の疑問にリアルタイムでお答えします。")
    with col2:
        st.success("✅ **セルフチェックリスト**\n\nミスを未然に防ぐための確認項目を提供します。")
        st.success("❓ **よくある質問**\n\n過去の代表的なトラブル事例と解決策を確認できます。")

def page_flow_guide():
    st.title("入稿フローガイド")
    col1, col2, col3 = st.columns(3)
    with col1: print_type = st.selectbox("① 印刷物の種類", PRINT_TYPES)
    with col2: software = st.selectbox("② 使用するソフト", SOFTWARE_LIST)
    with col3: file_format = st.selectbox("③ 入稿形式", FILE_FORMATS)
    st.subheader(f"📋 推奨入稿フロー：{print_type}")
    for i, step in enumerate(COMMON_FLOW_STEPS, 1):
        st.markdown(f"<div class='step-container'><span class='step-number'>{i}</span> {step}</div>", unsafe_allow_html=True)
    extra = EXTRA_FLOW_NOTES.get(print_type, [])
    if extra:
        with st.expander(f"📌 {print_type} 特有の注意点", expanded=True):
            for note in extra: st.markdown(f"・ {note}")

def page_checklist():
    st.title("入稿チェックリスト")
    col1, col2 = st.columns(2)
    with col1: print_type = st.selectbox("印刷物", PRINT_TYPES)
    with col2: software = st.selectbox("ソフト", SOFTWARE_LIST)
    st.divider()
    items = list(COMMON_CHECKLIST) + EXTRA_CHECKS_BY_SOFTWARE.get(software, [])
    if print_type == "卒業アルバム": items += ["個人写真の掲載許諾確認", "ページ順の最終確認"]
    results = {item: st.checkbox(item, key=f"chk_{item}") for item in items}
    st.divider()
    checked = sum(results.values())
    st.progress(checked / len(items))
    if checked == len(items): st.success("🎉 全項目確認済み！入稿可能です。")
    else: st.warning(f"残り {len(items) - checked} 項目です。")

def page_ai_chat():
    st.title("🤖 AIチャット相談 (Gemini)")
    st.write("入稿に関する疑問や、データの作り方についてAIに相談できます。")

    if not GEMINI_API_KEY:
        st.error("APIキーが設定されていません。")
        return

    # AI設定
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # セッション状態の初期化
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # チャット履歴の表示
    for message in st.session_state.chat_history:
        role_class = "user-message" if message["role"] == "user" else "assistant-message"
        st.markdown(f"<div class='chat-message {role_class}'><b>{'あなた' if message['role'] == 'user' else 'イシクラAI'}</b>: {message['content']}</div>", unsafe_allow_html=True)

    # 入力エリア
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("質問を入力してください（例：塗り足しの設定方法は？）")
        submit_button = st.form_submit_button("送信")

    if submit_button and user_input:
        # 履歴に追加
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # システムプロンプトを含むメッセージ構築
        prompt = f"""
        あなたは「株式会社イシクラ」の印刷入稿コンシェルジュです。
        以下の知識をベースに、ユーザーの質問に丁寧かつプロフェッショナルに日本語で回答してください。
        
        【イシクラの基本知識】
        - 埼玉県さいたま市の印刷会社。
        - 卒業アルバムが主力製品。
        - 入稿は CMYK 推奨、塗り足し 3mm 必須。
        - 解像度は 300〜350dpi 推奨。
        - フォントはアウトライン化を推奨。
        
        ユーザーの質問: {user_input}
        """
        
        with st.spinner("AIが回答を生成中..."):
            try:
                response = model.generate_content(prompt)
                ai_response = response.text
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                st.rerun()
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

def page_faq():
    st.title("よくある質問（FAQ）")
    for faq in FAQ_DATA:
        with st.expander(faq["q"]): st.write(faq["a"])

def page_contact():
    st.title("お問い合わせ案内")
    st.markdown("""
        #### 📞 お電話
        **048-794-XXXX** (代表)  
        受付：平日 9:00 〜 17:00
        #### 🌐 Webサイト
        [https://www.ishikura.co.jp/](https://www.ishikura.co.jp/)
    """)

# =============================================================================
# メイン
# =============================================================================

def main():
    st.set_page_config(page_title="イシクラ 入稿コンシェルジュ", page_icon="🖨️", layout="wide")
    apply_custom_style()
    with st.sidebar:
        st.markdown("<h2 style='color:#00529b;'>ISHIKURA</h2>", unsafe_allow_html=True)
        page = st.radio("メニュー", ["はじめに", "入稿フローガイド", "AIチャット相談", "チェックリスト", "FAQ", "お問い合わせ"])
        st.divider()
        st.caption("© 株式会社イシクラ")

    if page == "はじめに": page_about()
    elif page == "入稿フローガイド": page_flow_guide()
    elif page == "AIチャット相談": page_ai_chat()
    elif page == "チェックリスト": page_checklist()
    elif page == "FAQ": page_faq()
    elif page == "お問い合わせ": page_contact()

if __name__ == "__main__":
    main()
