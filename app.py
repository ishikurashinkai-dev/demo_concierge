"""
株式会社イシクラ 入稿コンシェルジュアプリ
Streamlit Community Cloud にそのままデプロイ可能。
依存ライブラリ: streamlit のみ（requirements.txt に記載）
"""

import streamlit as st

# =============================================================================
# ▼▼▼ データ定義エリア ▼▼▼
# ここを編集するだけでコンテンツを更新できます
# =============================================================================

# --- 印刷物の種類リスト ---
# 【拡張ポイント】新しい印刷物を追加する場合はここに追記してください
PRINT_TYPES = [
    "卒業アルバム",
    "チラシ・フライヤー",
    "パンフレット・冊子",
    "名刺",
    "記念誌・社史",
    "学校案内・広報誌",
    "その他",
]

# --- 使用ソフトのリスト ---
SOFTWARE_LIST = [
    "Adobe Illustrator",
    "Adobe Photoshop",
    "Adobe InDesign",
    "Microsoft PowerPoint",
    "PDF のみ（編集ソフトなし）",
    "その他",
]

# --- 入稿形式リスト ---
FILE_FORMATS = [
    "PDF（推奨）",
    "ai（Illustratorデータ）",
    "psd（Photoshopデータ）",
    "indd（InDesignデータ）",
    "jpg / png（画像データ）",
    "その他",
]

# --- 入稿フロー：印刷物の種類ごとの補足ステップ ---
# 【拡張ポイント】印刷物の種類ごとの特有注意点をここに追記してください
# key: PRINT_TYPES の文字列, value: 追加で表示するメモのリスト
EXTRA_FLOW_NOTES: dict[str, list[str]] = {
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

# --- ソフト別の追加チェック項目 ---
# 【拡張ポイント】ソフトごとの特有チェックをここに追記してください
EXTRA_CHECKS_BY_SOFTWARE: dict[str, list[str]] = {
    "Adobe Illustrator": [
        "すべてのテキストオブジェクトをアウトライン化している",
        "リンク画像をすべて埋め込み済み（またはリンクファイルを同梱）",
        "アピアランス・効果（ドロップシャドウなど）を分割・統合済み",
        "オーバープリント設定に問題がない（白オブジェクトに誤設定なし）",
        "ドキュメントのカラーモードが CMYK になっている（ファイル→ドキュメントのカラーモード）",
        "トリムマーク（トンボ）が正しく設定されている",
    ],
    "Adobe Photoshop": [
        "カラーモードが CMYK になっている（イメージ→モード）",
        "解像度が原寸で 300〜350dpi 以上になっている",
        "レイヤーを統合して保存している（または埋め込みスマートオブジェクトの確認）",
        "保存形式は PDF（印刷品質）または TIFF（非圧縮）推奨",
    ],
    "Adobe InDesign": [
        "すべてのフォントをアウトライン化、またはフォントファイルを同梱している",
        "リンクパネルでリンク切れが 0 件になっている",
        "「パッケージ」機能でデータをまとめてから入稿している",
        "ドキュメントのカラープロファイルが CMYK（Japan Color 2001 Coated 推奨）",
        "ページサイズと断ち落とし（塗り足し）設定が正しい",
    ],
    "Microsoft PowerPoint": [
        "フォントが埋め込まれているか、または PDF に書き出して入稿している",
        "画像解像度：PowerPoint からのエクスポートは低解像度になりやすいため担当者に相談を",
        "カラーモードの変換は印刷会社側で行うが、見た目の色変化を了承している",
        "※ PowerPoint データは印刷用途への変換リスクが高いため、PDF 書き出しを推奨します",
    ],
    "PDF のみ（編集ソフトなし）": [
        "PDF の規格が PDF/X-1a または PDF/X-4 になっている（推奨）",
        "フォントが埋め込まれている（Acrobat でプロパティ確認）",
        "カラーモードがすべて CMYK になっている（RGB 混在に注意）",
        "塗り足しが PDF 内に含まれている",
    ],
}

# --- 共通チェックリスト ---
# 【拡張ポイント】全印刷物共通の注意点をここに追記・編集してください
COMMON_CHECKLIST: list[str] = [
    "カラーモードは CMYK になっている",
    "仕上がりサイズで作成している（断裁後のサイズ）",
    "塗り足し（上下左右各 3mm）が設定されている",
    "重要な文字・ロゴが断裁位置から内側に 3mm 以上の余白を取っている",
    "画像解像度は原寸で 300〜350dpi 程度ある",
    "トンボ（トリムマーク）の設定が正しい",
    "透明効果・グラデーションの見た目を実際の印刷物でも確認した",
    "入稿用データと編集用データを分けて保存している",
    "確認用 PDF を自分で開いてレイアウト崩れがないことを確認した",
    "ファイル名に全角文字・特殊文字・スペースが含まれていない",
    "最終版データをバックアップしている",
]

# --- FAQ データ ---
# 【拡張ポイント】Q&A を追加・編集する場合はここに辞書を追記してください
# key: 質問文, value: 回答文
FAQ_DATA: list[dict[str, str]] = [
    {
        "q": "RGB のまま入稿するとどうなりますか？",
        "a": (
            "印刷時に CMYK へ自動変換されますが、変換アルゴリズムによって画面で見た色と大きく異なる場合があります。"
            "特に鮮やかな青・緑・橙などの色は再現できない色域のため、くすんだ仕上がりになることがあります。"
            "必ず事前に CMYK に変換し、色を確認してから入稿してください。"
        ),
    },
    {
        "q": "フォントをアウトライン化しないとどうなりますか？",
        "a": (
            "印刷会社の環境に同じフォントがない場合、文字化けや別フォントへの置き換えが起こります。"
            "レイアウトが崩れたり、意図しない書体で印刷されるリスクがあります。"
            "Illustrator・InDesign では「書式 → アウトラインを作成」で必ずアウトライン化してください。"
        ),
    },
    {
        "q": "塗り足し（断ち落とし）がないとどうなりますか？",
        "a": (
            "断裁は機械で行うため、わずかなズレが生じます。"
            "塗り足しがないと、用紙の端に白い地が出てしまう可能性があります。"
            "背景色や写真が端まである場合は、仕上がりサイズよりも上下左右各 3mm 広げて作成してください。"
        ),
    },
    {
        "q": "画像解像度はどのくらい必要ですか？",
        "a": (
            "印刷原稿では、原寸（使用サイズ）で 300〜350dpi が目安です。"
            "Web 用画像（72〜96dpi）をそのまま使うと、印刷時にぼやけた仕上がりになります。"
            "卒業アルバムの見開きページや大きな写真は 350dpi 以上を推奨します。"
        ),
    },
    {
        "q": "PDF で入稿する場合に気をつけることは？",
        "a": (
            "PDF 書き出し時は「PDF/X-1a」または「PDF/X-4」規格を推奨します。"
            "フォント埋め込み・トンボ・塗り足しを含めて書き出してください。"
            "Acrobat でプロパティを確認し、カラーモードが CMYK になっているかチェックしてください。"
        ),
    },
    {
        "q": "オーバープリントとは何ですか？なぜ注意が必要ですか？",
        "a": (
            "オーバープリントは、重なったオブジェクトのインクを混合させる印刷設定です。"
            "白いオブジェクトにオーバープリントが設定されていると、印刷時に白が透けてしまい、"
            "背景が透けて見えるトラブルが起きます。"
            "Illustrator の「属性」パネルでオーバープリント設定を確認してください。"
        ),
    },
    {
        "q": "PowerPoint データで入稿できますか？",
        "a": (
            "PowerPoint データは直接入稿よりも、PDF に書き出してから入稿することを推奨します。"
            "PowerPoint のままでは画像解像度が下がったり、フォントが置き換わるリスクがあります。"
            "書き出し時は「印刷品質」を選択してください。カラーモードの変換は当社で対応しますが、"
            "色味の変化についてはご了承ください。"
        ),
    },
    {
        "q": "入稿後に修正はできますか？",
        "a": (
            "印刷工程が進んでからの修正はお受けできない場合があります。"
            "入稿前に必ず確認用 PDF で最終チェックを行い、問題がないことを確認してから入稿してください。"
            "不安な点は入稿前にイシクラ担当者にご相談ください。"
        ),
    },
    {
        "q": "卒業アルバム特有の注意点はありますか？",
        "a": (
            "卒業アルバムは個人情報（顔写真・氏名）を扱うため、掲載許諾の管理が重要です。"
            "また、写真品質のばらつきが目立ちやすいため、できるだけ原寸 350dpi 以上の写真を使用してください。"
            "ページ構成（台割）と氏名の最終確認は、学校担当者と必ず行ってください。"
        ),
    },
]

# --- 入稿フロー：共通ステップ ---
# 【拡張ポイント】フローのステップを追加・変更する場合はここを編集してください
COMMON_FLOW_STEPS: list[str] = [
    "仕上がりサイズ・ページ数・仕様の確認（担当者への事前確認を推奨）",
    "カラーモードを CMYK に設定する",
    "塗り足し（通常 上下左右 3mm）を設定する",
    "フォントのアウトライン化（Illustrator / InDesign の場合）またはフォント埋め込み確認",
    "画像解像度の確認（原寸で 300〜350dpi 目安）",
    "リンク画像の埋め込み、またはリンクファイルを同梱する",
    "トンボ（トリムマーク）の設定と断裁位置の確認",
    "重要な文字・ロゴが断裁位置から内側に十分な余白を取れているか確認（3mm 以上）",
    "オーバープリントの設定確認（特に白オブジェクトに注意）",
    "PDF 書き出し（印刷品質 / PDF/X-1a または PDF/X-4 推奨）",
    "確認用 PDF を自分で開いてレイアウト・文字化けがないか最終確認",
    "チェックリストをすべて確認してから入稿",
]

# =============================================================================
# ▲▲▲ データ定義エリア終わり ▲▲▲
# =============================================================================


# =============================================================================
# デザイン・ユーティリティ
# =============================================================================

def apply_custom_style():
    """カスタムCSSを適用してプレミアムな外観にする"""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Noto+Sans+JP', sans-serif;
        }
        
        .main {
            background-color: #f8f9fa;
        }
        
        /* タイトル・見出しのスタイル */
        h1, h2, h3 {
            color: #00529b; /* イシクラ・ブルー */
            border-left: 5px solid #00529b;
            padding-left: 15px;
            margin-top: 1.5rem !important;
        }
        
        /* サイドバー */
        .css-1d391kg {
            background-color: #ffffff;
        }
        
        /* カード風のコンテナ */
        .stAlert, .stCallout {
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        
        /* ボタン */
        .stButton > button {
            border-radius: 20px;
            border: 1px solid #00529b;
            background-color: #ffffff;
            color: #00529b;
            transition: all 0.3s;
        }
        .stButton > button:hover {
            background-color: #00529b;
            color: #ffffff;
        }
        
        /* ステップ表示 */
        .step-container {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            margin-bottom: 10px;
        }
        .step-number {
            display: inline-block;
            width: 30px;
            height: 30px;
            background-color: #00529b;
            color: white;
            border-radius: 50%;
            text-align: center;
            line-height: 30px;
            font-weight: bold;
            margin-right: 10px;
        }
        </style>
    """, unsafe_allow_html=True)


# =============================================================================
# ページ関数
# =============================================================================

def page_about() -> None:
    """画面1：はじめに（イシクラについて）"""
    st.title("株式会社イシクラ 入稿コンシェルジュ")
    
    st.markdown(
        """
        <div style='padding: 20px; background-color: #e3f2fd; border-radius: 15px; border-left: 8px solid #00529b; margin-bottom: 25px;'>
            <h4 style='margin:0; color:#00529b;'>想い出をカタチに、未来へつなぐ。</h4>
            <p style='margin-top:10px;'>株式会社イシクラは、埼玉県さいたま市を拠点に、卒業アルバムや各種印刷物の企画・制作を通じて、皆様の大切な瞬間を形にするお手伝いをしています。</p>
        </div>
        """, unsafe_allow_html=True
    )

    st.subheader("このアプリの目的")
    st.write("データ入稿時の「困った」を解決し、スムーズな印刷進行をサポートするためのコンシェルジュアプリです。")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("🎯 **入稿ガイド**\n\n印刷物の種類や使用ソフトに合わせた最適な制作フローをステップ形式でご案内します。")
    with col2:
        st.success("✅ **チェックリスト**\n\nうっかりミスを防ぐための重要項目を網羅。入稿前の最終確認にご活用ください。")

    st.divider()
    
    st.subheader("主な事業領域")
    tabs = st.tabs(["🎓 学校向け", "🏢 企業・団体向け", "📷 写真館向け"])
    
    with tabs[0]:
        st.markdown("#### 卒業アルバム・学校案内\n卒業アルバムのトップメーカーとして、撮影から製本までトータルでサポートします。")
    with tabs[1]:
        st.markdown("#### 商業印刷・記念誌\nパンフレット、チラシ、記念誌など、高品質な印刷物を提供します。")
    with tabs[2]:
        st.markdown("#### プロフェッショナル支援\n写真館やプロカメラマンの皆様のパートナーとして、最高の品質を追求します。")


def page_flow_guide() -> None:
    """画面2：入稿フローガイド（ウィザード形式）"""
    st.title("入稿フローガイド")
    st.markdown("以下の条件を選択してください。最適な入稿ステップが表示されます。")

    with st.container():
        st.markdown("<div style='background-color: white; padding: 25px; border-radius: 15px; border: 1px solid #eee; margin-bottom: 20px;'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            print_type = st.selectbox("① 印刷物の種類", PRINT_TYPES, key="flow_print_type")
        with col2:
            software = st.selectbox("② 使用するソフト", SOFTWARE_LIST, key="flow_software")
        with col3:
            file_format = st.selectbox("③ 入稿形式", FILE_FORMATS, key="flow_format")
        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader(f"📋 あなたの入稿プラン：{print_type}")
    
    # ステップ表示
    for i, step in enumerate(COMMON_FLOW_STEPS, 1):
        st.markdown(f"""
            <div class='step-container'>
                <span class='step-number'>{i}</span> {step}
            </div>
        """, unsafe_allow_html=True)

    # 印刷物の種類に応じた追加注意点
    extra_notes = EXTRA_FLOW_NOTES.get(print_type, [])
    if extra_notes:
        with st.expander(f"📌 {print_type} 特有の重要なアドバイス", expanded=True):
            for note in extra_notes:
                st.markdown(f"**・ {note}**")

    # ソフト別の補足
    software_tips: dict[str, str] = {
        "Adobe Illustrator": "フォントのアウトライン化・画像の埋め込みは Illustrator では必須作業です。",
        "Adobe Photoshop": "Photoshop は画像データ専用です。テキストを含む場合は Illustrator や InDesign との組み合わせを推奨します。",
        "Adobe InDesign": "InDesign の「パッケージ」機能を使うと、リンク画像・フォントをまとめて整理できます。",
        "Microsoft PowerPoint": "PowerPoint からは PDF（印刷品質）で書き出してから入稿することを強く推奨します。",
        "PDF のみ（編集ソフトなし）": "PDF 入稿の場合は PDF/X-1a または PDF/X-4 規格で書き出してください。",
    }
    tip = software_tips.get(software)
    if tip:
        st.info(f"💡 **{software} のワンポイント:** {tip}")


def page_checklist() -> None:
    """画面3：入稿チェックリスト"""
    st.title("入稿チェックリスト")
    st.markdown("選択した内容に基づき、入稿前に確認すべき項目をリストアップしました。")

    col1, col2 = st.columns(2)
    with col1:
        print_type = st.selectbox("対象の印刷物", PRINT_TYPES, key="check_print_type")
    with col2:
        software = st.selectbox("制作ソフト", SOFTWARE_LIST, key="check_software")

    st.divider()

    # チェック項目の組み立て
    all_items: list[str] = list(COMMON_CHECKLIST)
    software_items: list[str] = EXTRA_CHECKS_BY_SOFTWARE.get(software, [])
    
    # 印刷物の種類ごとの追加チェック項目
    # 【拡張ポイント】印刷物の種類ごとのチェック項目をここに追加してください
    extra_print_checks: dict[str, list[str]] = {
        "卒業アルバム": [
            "個人写真の掲載許諾（プライバシー）をすべて取得済みである",
            "ページ順・氏名表記に間違いがないか、学校側と最終確認済みである",
            "表紙の仕様（布貼り・印刷等）が発注内容と一致している",
            "集合写真等の重要画像が原寸で 350dpi 以上の解像度を確保している",
        ],
        "パンフレット・冊子": [
            "総ページ数が 4 の倍数（中綴じ等の場合）になっている",
            "表紙と本文のデータが区別できるように命名されている",
        ],
        "名刺": [
            "仕上がりサイズ（91x55mm等）が正しく設定されている",
            "重要な文字が断裁線から 3mm 以上内側に配置されている",
        ],
    }
    extra_print = extra_print_checks.get(print_type, [])

    # チェックボックスの状態を session_state で管理
    # 選択が変わるたびにリセットされるのを防ぐため、keyを工夫
    state_key = f"checks_{print_type}_{software}"
    
    # 内部での表示用
    st.subheader("✅ セルフチェック")
    
    all_sections = [
        ("🌐 共通チェック項目", COMMON_CHECKLIST),
        (f"🛠️ {software} 固有項目", software_items),
        (f"📌 {print_type} 固有項目", extra_print)
    ]
    
    results = {}
    
    for section_title, items in all_sections:
        if items:
            st.markdown(f"**{section_title}**")
            for item in items:
                # 一意のキーを作成
                item_key = f"chk_{state_key}_{item}"
                results[item] = st.checkbox(item, key=item_key)
            st.write("")

    # チェック結果の要約
    st.divider()
    checked_items = [item for item, val in results.items() if val]
    unchecked_items = [item for item, val in results.items() if not val]
    total_count = len(results)
    
    if total_count > 0:
        progress = len(checked_items) / total_count
        st.progress(progress)
        
        if not unchecked_items:
            st.balloons()
            st.success("✨ 素晴らしい！すべての項目が確認されました。入稿可能です！")
        else:
            st.warning(f"現在 {len(checked_items)} / {total_count} 項目完了しています。")
            with st.expander("未完了の項目を確認する"):
                for item in unchecked_items:
                    st.markdown(f"- ⚠️ {item}")


def page_faq() -> None:
    """画面4：よくある質問（FAQ）"""
    st.title("よくある質問（FAQ）")
    st.markdown("制作や入稿時によくあるトラブルと、その対策についてまとめました。")

    # 検索機能
    search_query = st.text_input("キーワードで検索", placeholder="例：RGB, 解像度...")

    for i, faq in enumerate(FAQ_DATA):
        if search_query.lower() in faq['q'].lower() or search_query.lower() in faq['a'].lower():
            with st.expander(f"Q{i + 1}：{faq['q']}"):
                st.markdown(f"**A：** {faq['a']}")

    st.divider()
    st.info("疑問が解決しない場合は、イシクラ担当者までお電話またはメールにてお気軽にご相談ください。")


def page_contact() -> None:
    """画面5：お問い合わせ案内"""
    st.title("お問い合わせ案内")

    st.warning(
        "**【重要】**\n\n"
        "本アプリは入稿準備を補助するためのガイドです。実際の入稿可否や仕様の最終判断については、必ず当社担当者と直接お打ち合わせください。"
    )

    st.subheader("お問い合わせ窓口")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        #### 📞 お電話
        **048-XXX-XXXX** (仮)  
        受付時間：平日 9:00 〜 17:00  
        *※土日祝、弊社指定休業日を除く*
        """)
    with col2:
        st.markdown("""
        #### 📧 Webから
        [お問い合わせフォームはこちら](https://www.ishikura.co.jp/)  
        24時間受付（回答は営業時間内となります）
        """)

    st.divider()
    
    st.subheader("会社情報")
    st.markdown("""
    | 項目 | 内容 |
    | :--- | :--- |
    | **会社名** | 株式会社イシクラ |
    | **所在地** | 埼玉県さいたま市岩槻区古ヶ場 1-6-11 |
    | **設立** | 19XX年（詳細は公式サイトへ） |
    | **事業内容** | 卒業アルバム制作、各種商業印刷、企画デザイン |
    """)
    
    # アクセス（簡易表示）
    st.markdown("---")
    st.markdown("📍 [Googleマップで開く](https://www.google.com/maps/search/?api=1&query=埼玉県さいたま市岩槻区古ヶ場1-6-11)")


# =============================================================================
# メインアプリ
# =============================================================================

def main() -> None:
    st.set_page_config(
        page_title="イシクラ 入稿コンシェルジュ",
        page_icon="🖨️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # カスタムCSSの適用
    apply_custom_style()

    # --- サイドバー ---
    with st.sidebar:
        # ロゴ（テキスト）
        st.markdown(
            """
            <div style='text-align: left; padding-bottom: 20px;'>
                <h2 style='border:none; padding:0; margin:0; color:#00529b;'>ISHIKURA</h2>
                <small style='color:#666;'>CONCIERGE APP</small>
            </div>
            """, unsafe_allow_html=True
        )
        
        st.write("---")
        
        # ナビゲーション
        page = st.radio(
            "メニューを選択してください",
            options=[
                "はじめに（イシクラについて）",
                "入稿フローガイド",
                "入稿チェックリスト",
                "よくある質問（FAQ）",
                "お問い合わせ案内",
            ],
            label_visibility="visible"
        )

        st.write("---")
        st.caption("© 株式会社イシクラ")
        st.caption("v1.0.0 (Standard Edition)")

    # --- ページルーティング ---
    if page == "はじめに（イシクラについて）":
        page_about()
    elif page == "入稿フローガイド":
        page_flow_guide()
    elif page == "入稿チェックリスト":
        page_checklist()
    elif page == "よくある質問（FAQ）":
        page_faq()
    elif page == "お問い合わせ案内":
        page_contact()


if __name__ == "__main__":
    main()
