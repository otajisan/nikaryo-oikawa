"""公開サイト（docs/）の HTML を生成する。

ヘッダ・ナビ・フッタ・出典の一覧をページ間で共通にするためのスクリプト。
ページの本文と出典はこのファイルに書き、`python3 tools/build_site.py` で docs/ の HTML を作り直す。
docs/assets/（CSS・グラフの JS・アイコン）と docs/.nojekyll は手で管理し、このスクリプトは触らない。
生成した HTML もコミットする（GitHub Pages は main の /docs をそのまま配信する）。
"""
import html
import os
import re
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
ASOF = "2026-10-19"
REPO = "https://github.com/otajisan/nikaryo-oikawa"

# 出典: key -> (種類, ページ名, URL, 取得日)
S = {
    "env_info": ("official", "環境省 クビアカツヤカミキリ関連情報", "https://www.env.go.jp/nature/gairai/info_kubiaka.html", ASOF),
    "env_honbu": ("official", "環境省 クビアカツヤカミキリ対策本部", "https://www.env.go.jp/nature/intro/4document/data/aromia-bungii.html", ASOF),
    "env_matters": ("official", "環境省 第 3 回クビアカツヤカミキリ対策本部 申合せ事項", "https://www.env.go.jp/nature/intro/4document/data/aromia-bungii/aromia-bungii03/matters.pdf", ASOF),
    "env_yobihi": ("official", "環境省 予備費使用の資料", "https://www.env.go.jp/content/000433725.pdf", ASOF),
    "env_jigyo": ("official", "環境省 特定外来生物防除等対策事業の概要", "https://www.env.go.jp/content/000433736.pdf", ASOF),
    "env_koubo": ("official", "環境省 特定外来生物防除等対策事業 追加公募", "https://www.env.go.jp/press/press_05666.html", ASOF),
    "env_net": ("official", "環境省 クビアカツヤカミキリの情報収集システムの試行", "https://www.env.go.jp/press/press_05662.html", "2026-10-18"),
    "env_bassoku": ("official", "環境省 外来生物法の罰則", "https://www.env.go.jp/nature/intro/1law/bassoku.html", ASOF),
    "env_qa": ("official", "環境省 外来生物法 Q&A", "https://www.env.go.jp/nature/intro/1law/qa.html", ASOF),
    "env_doutei": ("official", "環境省 特定外来生物同定マニュアル（昆虫類）", "https://www.env.go.jp/nature/intro/2outline/manual/6hp_konchurui2.pdf", ASOF),
    "env_dino": ("official", "環境省 ジノテフランの水産動植物の登録保留基準の資料", "https://www.env.go.jp/content/900544321.pdf", ASOF),
    "env_perm": ("official", "環境省 ペルメトリンの水産動植物の登録保留基準の資料", "https://www.env.go.jp/content/900544450.pdf", ASOF),
    "lawtrans": ("official", "日本法令外国語訳データベース 外来生物法", "https://www.japaneselawtranslation.go.jp/ja/laws/view/3354", "2026-10-18"),
    "maff_status": ("official", "農林水産省 クビアカツヤカミキリの確認状況（令和 8 年 8 月時点）", "https://www.maff.go.jp/j/syouan/syokubo/keneki/k_kokunai/kubiaka/attach/pdf/kubiaka-33.pdf", ASOF),
    "maff_honbu": ("official", "農林水産省 クビアカツヤカミキリ対策本部", "https://www.maff.go.jp/j/syouan/syokubo/keneki/k_kokunai/kubiaka/taisaku.html", ASOF),
    "senryaku": ("official", "クビアカツヤカミキリ防除戦略（2026-09-11 対策本部決定）", "https://www.maff.go.jp/j/syouan/syokubo/keneki/k_kokunai/kubiaka/attach/pdf/taisaku-18.pdf", "2026-10-18"),
    "pesticide": ("official", "農林水産省 農薬登録情報提供システム", "https://pesticide.maff.go.jp/", "2026-10-18"),
    "ffpri3": ("official", "森林総合研究所「クビアカツヤカミキリの防除法」生態と探索法の章", "https://www.ffpri.go.jp/pubs/chukiseika/documents/5th-chuukiseika12-3.pdf", "2026-10-18"),
    "ffpri4": ("official", "森林総合研究所「クビアカツヤカミキリの防除法」防除法の章", "https://www.ffpri.go.jp/pubs/chukiseika/documents/5th-chuukiseika12-4.pdf", "2026-10-18"),
    "ffpri5": ("official", "森林総合研究所「クビアカツヤカミキリの防除法」総合防除の章", "https://www.ffpri.go.jp/pubs/chukiseika/documents/5th-chuukiseika12-5.pdf", "2026-10-18"),
    "ffpri2020": ("official", "森林総合研究所 研究の“いま”「注射でサクラを守る」（2020）", "https://www.ffpri.go.jp/research/saizensen/2020/20200512-01.html", ASOF),
    "ffpri_bottle": ("official", "森林総合研究所 研究の“いま”ボトル型毒餌剤（2026-03-02）", "https://www.ffpri.go.jp/research/saizensen/2026/20260302.html", ASOF),
    "kanagawa": ("official", "神奈川県 クビアカツヤカミキリに関するお知らせ（2026-09-04 更新）", "https://www.pref.kanagawa.jp/docs/t4i/cnt/f986/kubiaka.html", ASOF),
    "kawa_page": ("official", "川崎市 特定外来生物 クビアカツヤカミキリについて（2026-09-01 更新）", "https://www.city.kawasaki.jp/300/page/0000166500.html", ASOF),
    "kawa_0626": ("official", "川崎市 報道発表資料（2026-06-26）", "https://www.city.kawasaki.jp/templates/prs/cmsfiles/contents/0000188/188375/20260626.pdf", ASOF),
    "kawa_0701": ("official", "川崎市 報道発表資料（2026-07-01）", "https://www.city.kawasaki.jp/templates/prs/cmsfiles/contents/0000188/188500/0701kubiaka.pdf", ASOF),
    "kawa_0714": ("official", "川崎市 報道発表資料（2026-07-14）", "https://www.city.kawasaki.jp/templates/prs/cmsfiles/contents/0000188/188707/20260714_kubiaka.pdf", ASOF),
    "kawa_form": ("official", "川崎市 クビアカツヤカミキリ・フラス発見報告フォーム", "https://logoform.jp/f/uCGbM", ASOF),
    "kawa_kikaku": ("official", "川崎市 環境局 総務部 企画課", "https://www.city.kawasaki.jp/300/soshiki/7-1-3-0-0.html", ASOF),
    "kawa_council": ("official", "川崎市議会 令和 8 年 第 3 回定例会", "https://www.city.kawasaki.jp/980/page/0000190006.html", ASOF),
    "kawa_kihon": ("official", "川崎市 二ヶ領用水基本方針 概要版（2026-02）", "https://www.city.kawasaki.jp/templates/pubcom/cmsfiles/contents/0000182/182166/kouhyougaiyouban.pdf", ASOF),
    "kawa_honsen": ("official", "川崎市 二ヶ領本川", "https://www.city.kawasaki.jp/530/page/0000018309.html", ASOF),
    "kawa_iji": ("official", "川崎市 河川の維持管理", "https://www.city.kawasaki.jp/530/page/0000018546.html", ASOF),
    "kawa_ijigaiyou": ("official", "川崎市 河川維持管理計画 概要版（2022-03）", "https://www.city.kawasaki.jp/530/cmsfiles/contents/0000094/94935/ijikannrigaiyou.pdf", ASOF),
    "kawa_jumoku": ("official", "川崎市 河川維持管理実施計画【河川樹木編】（2024-03）", "https://www.city.kawasaki.jp/530/cmsfiles/contents/0000165/165241/03_ijikanrijisshikeikaku(kasenjumokuhen).pdf", ASOF),
    "kawa_kinenbutsu": ("official", "川崎市 二ヶ領用水の国登録記念物の資料", "https://www.city.kawasaki.jp/880/cmsfiles/contents/0000112/112712/011126hukoku3.pdf", ASOF),
    "kawa_iinkai": ("official", "川崎市議会 まちづくり委員会資料（2025-11-06）", "https://www.city.kawasaki.jp/980/cmsfiles/contents/0000175/175709/20251106-1(2)-1koushin.pdf", ASOF),
    "kawa_policy": ("official", "川崎市 サイトポリシー（著作権）", "https://www.city.kawasaki.jp/main/site_policy/0000000027.html", ASOF),
    "yokohama": ("official", "横浜市 記者発表資料（2026-07-10）", "https://www.city.yokohama.lg.jp/city-info/koho-kocho/press/kankyo/2026/0710_k.files/0005_20260710.pdf", ASOF),
    "tokyo": ("official", "東京都環境局 クビアカツヤカミキリ（2026-09-07 更新）", "https://www.kankyo.metro.tokyo.lg.jp/nature/animals_plants/400100a20191204115758336", ASOF),
    "setagaya": ("official", "世田谷区 クビアカツヤカミキリ", "https://www.city.setagaya.lg.jp/02074/29378.html", ASOF),
    "ota": ("official", "大田区 クビアカツヤカミキリ", "https://www.city.ota.tokyo.jp/seikatsu/sumaimachinami/kankyou/karasu/kubiakatuyakamikiri.html", ASOF),
    "kyoto": ("official", "京都府 クビアカツヤカミキリ防除対策マニュアル 第 1 版（2024-08）", "https://www.pref.kyoto.jp/gairai/documents/manyuaru.pdf", ASOF),
    "gunma_flyer": ("official", "群馬県 クビアカツヤカミキリのチラシ", "https://ecogunma.pref.gunma.jp/sakura/wp-content/uploads/2026/06/d5eb77f2b5852ffca964d8abc5fc9353.pdf", ASOF),
    "gunma_net": ("official", "群馬県 ぐんまクビアカネット", "https://www.pref.gunma.jp/site/houdou/101582.html", ASOF),
    "saitama": ("official", "埼玉県環境科学国際センター 被害防止の手引", "https://www.pref.saitama.lg.jp/documents/105886/kubiakamanual5.pdf", ASOF),
    "saitama_survey": ("official", "埼玉県 クビアカツヤカミキリ発見大調査 2026", "https://www.pref.saitama.lg.jp/a0508/news/page/news2026071401.html", ASOF),
    "osaka": ("official", "大阪府立環境農林水産総合研究所 被害対策の手引書（改訂第 6 版、2026-04）", "https://www.knsk-osaka.jp/kankyo/info/doc/2026042000042/file_contents/Tebiki_6.pdf", ASOF),
    "yamanashi": ("official", "山梨県 クビアカツヤカミキリ緊急防除の補助金", "https://www.pref.yamanashi.jp/shizen/gairaiseibutu/kubiakahojokin.html", ASOF),
    "kazo": ("official", "加須市 クビアカツヤカミキリ防除の補助金", "https://www.city.kazo.lg.jp/soshiki/kakyou_seisaku/choujuu/39831.html", ASOF),
    "nagano": ("official", "長野県 報道発表の別紙（22 都府県）", "https://www.pref.nagano.lg.jp/shizenhogo/happyou/documents/080917bessi.pdf", ASOF),
    "funabashi": ("web", "船橋市 クビアカツヤカミキリ（指定日）", "https://www.city.funabashi.lg.jp/machi/kankyou/010/p127511.html", ASOF),
    "townnews_0710": ("web", "タウンニュース（2026-07-10）菅生緑地での確認", "https://www.townnews.co.jp/0203/2026/07/10/844107.html", ASOF),
    "townnews_odawara": ("web", "タウンニュース（2026-10-17）小田原市の試行伐採", "https://www.townnews.co.jp/0607/2026/10/17/857683.html", ASOF),
    "townnews_matsuda": ("web", "タウンニュース（2026-10-03）松田町の報奨金", "https://www.townnews.co.jp/0608/2026/10/03/855464.html", ASOF),
    "sakigake": ("web", "秋田魁新報（2026-08-26）環境省の概算要求", "https://www.sakigake.jp/news/article/20260826CO0132/", ASOF),
    "nikkei": ("web", "日本経済新聞（2026-10-06）予備費", "https://www.nikkei.com/article/DGXZQOUA062GA0W6A001C2000000/", ASOF),
    "kankou": ("web", "神奈川県観光協会 二ヶ領用水宿河原堤桜並木", "https://kanagawa-kankou.or.jp/notices/54", ASOF),
    # ゴミ問題（water/litter.html）
    "kawa_honpen": ("official", "川崎市 二ヶ領用水基本方針 本編（2026-02）", "https://www.city.kawasaki.jp/530/cmsfiles/contents/0000058/58112/kouhyouhonpen.pdf", ASOF),
    "kawa_survey": ("official", "川崎市議会 まちづくり委員会資料（2025-11-06）二ヶ領用水についての市民アンケート", "https://www.city.kawasaki.jp/980/cmsfiles/contents/0000175/175709/20251106-1(2)-2.pdf", "2026-10-18"),
    "kawa_pubcom": ("official", "川崎市議会 まちづくり委員会資料（2026-02-09）二ヶ領用水基本方針のパブリックコメントの結果", "https://www.city.kawasaki.jp/980/cmsfiles/contents/0000175/175709/20260209-2(2)-1.pdf", "2026-10-18"),
    "kawa_suishin10": ("official", "川崎市 第 10 回 二ヶ領用水推進会議 議事録（2025-02-17）", "https://www.city.kawasaki.jp/530/cmsfiles/contents/0000176/176971/gijiroku.pdf", "2026-10-18"),
    "kawa_suishin9": ("official", "川崎市 二ヶ領用水推進会議 資料（2024 年の一斉清掃の結果）", "https://www.city.kawasaki.jp/530/cmsfiles/contents/0000172/172143/siryou.pdf", "2026-10-18"),
    "kawa_suishin9_log": ("official", "川崎市 二ヶ領用水推進会議 議事録（2024 年度）", "https://www.city.kawasaki.jp/530/cmsfiles/contents/0000172/172143/gijiroku.pdf", "2026-10-18"),
    "kawa_aigo_flyer": ("official", "川崎市 河川愛護ボランティアのチラシ", "https://www.city.kawasaki.jp/530/cmsfiles/contents/0000028/28431/kasenaigo-chirasi.pdf", ASOF),
    "kawa_aigo": ("official", "川崎市 河川愛護ボランティア制度", "https://www.city.kawasaki.jp/kurashi/category/29-5-19-6-0-0-0-0-0-0.html", "2026-10-18"),
    "kawa_kasenka": ("official", "川崎市 建設緑政局 道路河川整備部 河川課", "https://www.city.kawasaki.jp/530/soshiki/10-5-3-0-0.html", "2026-10-18"),
    "kawa_tsuho": ("official", "川崎市 道路・公園・河川の損傷などの通報", "https://www.city.kawasaki.jp/kurashi/category/28-6-6-9-0-0-0-0-0-0.html", "2026-10-18"),
    "kawa_fuho": ("official", "川崎市 不法投棄の通報", "https://www.city.kawasaki.jp/kurashi/category/262-2-2-0-0-0-0-0-0-0.html", "2026-10-18"),
    "kawa_touro": ("official", "川崎市 二ヶ領用水 灯篭流し＆清掃（2025-09-28）", "https://www.city.kawasaki.jp/530/page/0000181039.html", "2026-10-18"),
    "kawa_hosho": ("official", "川崎市 市民活動（ボランティア活動）補償制度", "https://www.city.kawasaki.jp/templates/faq/250/0000012210.html", "2026-10-18"),
    "nakahara_kumin": ("official", "川崎市中原区 第 5 期 区民会議の報告（ごみ問題）", "https://www.city.kawasaki.jp/nakahara/cmsfiles/contents/0000076/76506/houdouteikyousiryou.pdf", "2026-10-18"),
    "nakahara_dayori": ("official", "市政だより なかはら区版（2024 年 3 月号）", "https://www.city.kawasaki.jp/170/cmsfiles/contents/0000158/158810/0301_nakahara_web.pdf", ASOF),
    "nakahara_sdc": ("official", "川崎市中原区 なかはら SDC（YORIAI）", "https://www.city.kawasaki.jp/nakahara/page/0000186667.html", "2026-10-16"),
    "seseragikan": ("web", "二ヶ領せせらぎ館 2026 年 二ヶ領用水一斉清掃のお知らせ", "https://www.seseragikan.com/news-topics/5543/", ASOF),
    "seven_josei": ("web", "セブン-イレブン記念財団 地域美化助成", "https://www.7midori.org/josei/", "2026-10-18"),
    "kasen_kikin": ("web", "河川財団 河川基金の助成", "https://www.kasen.or.jp/kikin/tabid290.html", "2026-10-18"),
    "flora_cialdini": ("web", "FORRT Replication Atlas: Cialdini ら（1990）の再現研究のまとめ", "https://forrt.org/flora-replication-atlas/doi/10.1037/0022-3514.58.6.1015/", "2026-10-18"),
    "beijer_gavle": ("web", "Beijer Institute: 子どもの絵のごみ箱の実験（スウェーデン・イェヴレ、2023）", "https://beijer.kva.se/?p=4215", "2026-10-19"),
}
LABEL = {"official": "公式", "web": "Web"}

NAV = [
    ("index.html", "ホーム", "home"),
    ("water/index.html", "水と生きもの", "water"),
    ("sakura/index.html", "桜並木を守る", "sakura"),
    ("action/index.html", "みんなでできること", "action"),
    ("about.html", "このサイトについて", "about"),
]

LOGO = ('<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="15" class="lg-bg" stroke-width="1.5"/>'
        '<path d="M5 19c3-2 6-2 9 0s6 2 9 0 4-1.5 4-1.5" fill="none" class="lg-wave" stroke-width="1.8" stroke-linecap="round"/>'
        '<path d="M9 14c3-3.5 8-4 12-1.5-2 .6-3 2-3.4 3.4-2.6-.3-5.6-.8-8.6-1.9z" class="lg-fish"/>'
        '<circle cx="23" cy="9" r="2.2" class="lg-sakura"/></svg>')


def esc(s):
    return html.escape(s, quote=True)


def render(body, prefix, used):
    def badge(m):
        key = m.group(1)
        if key == "est":
            return '<span class="src est" title="公開資料からの推定。確かめられていません">推定</span>'
        if key == "tbc":
            return '<span class="tbc">要確認</span>'
        kind, title, url, date = S[key]
        if key not in used:
            used.append(key)
        return (f'<a class="src {kind}" href="{esc(url)}" target="_blank" rel="noopener noreferrer" '
                f'title="{esc(title)}（取得 {date}）">{LABEL[kind]}</a>')
    body = body.replace("{asof}", ASOF)
    body = re.sub(r"\[\[([a-z0-9_]+)\]\]", badge, body)
    body = body.replace('href="@/', f'href="{prefix}')
    return body


def page(path, title, section, crumbs, body, theme="", desc="", charts=False, pager=None):
    depth = path.count("/")
    prefix = "/nikaryo-oikawa/" if path == "404.html" else "../" * depth
    used = []
    content = render(body, prefix, used)
    nav = "".join(
        f'<li><a href="{prefix}{href}"{" aria-current=\"page\"" if href == path else (" class=\"active\"" if key == section else "")}>{label}</a></li>'
        for href, label, key in NAV)
    bc = ""
    if crumbs:
        items = "".join(f'<li><a href="{prefix}{h}">{t}</a></li>' for h, t in crumbs)
        bc = f'<nav class="breadcrumb" aria-label="パンくずリスト"><ol>{items}<li aria-current="page">{title}</li></ol></nav>'
    srcs = ""
    if used:
        lis = "".join(
            f'<li><span class="src {S[k][0]}">{LABEL[S[k][0]]}</span> <a href="{esc(S[k][2])}" target="_blank" rel="noopener noreferrer">{esc(S[k][1])}</a>（取得 {S[k][3]}）<br>{esc(S[k][2])}</li>'
            for k in used)
        srcs = f'<h2 id="sources">このページの出典</h2><ol class="sources">{lis}</ol>'
    pg = ""
    if pager:
        prev, nxt = pager
        a = f'<a class="prev" href="{prefix}{prev[0]}"><small>← 前へ</small>{prev[1]}</a>' if prev else "<span></span>"
        b = f'<a class="next" href="{prefix}{nxt[0]}"><small>次へ →</small>{nxt[1]}</a>' if nxt else ""
        pg = f'<nav class="pager" aria-label="前後のページ">{a}{b}</nav>'
    full_title = "武蔵小杉の二ヶ領用水にもオイカワを" if path == "index.html" else f"{title}｜武蔵小杉の二ヶ領用水にもオイカワを"
    hero = ""
    if path == "index.html":
        hero, content = content.split("<!--/hero-->", 1)
    main_body = f'{bc}{content}{srcs}{pg}'
    script = f'<script src="{prefix}assets/chart.js" defer></script>' if charts else ""
    doc = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self'; script-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'">
<meta name="referrer" content="no-referrer">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="stylesheet" href="{prefix}assets/site.css">
<link rel="icon" href="{prefix}assets/icon.svg" type="image/svg+xml">
{script}
</head>
<body class="{theme}">
<a href="#main" class="skip">本文へ</a>
<header class="site-header"><div class="inner">
<a class="brand" href="{prefix}index.html">{LOGO}<span>武蔵小杉の二ヶ領用水にもオイカワを<small>二ヶ領用水の水辺と桜並木を守る市民のプロジェクト</small></span></a>
<nav class="site-nav" aria-label="サイト内のメニュー"><ul>{nav}</ul></nav>
</div></header>
<div class="notice-bar"><div class="inner">市民による非公式のサイトです（川崎市の公式サイトではありません）。情報は {ASOF} 時点のものです。手続き・連絡先は、必ず各機関の公式ページで確かめてください。</div></div>
{hero}
<main id="main">
{main_body}
</main>
<footer class="site-footer"><div class="inner">
<p><b>武蔵小杉の二ヶ領用水にもオイカワを</b> — 二ヶ領用水（神奈川県川崎市）の水辺の自然と桜並木を守るための、市民の調査と仕組みづくり。</p>
<p>文章: <a href="{REPO}/blob/main/LICENSE-docs" target="_blank" rel="noopener noreferrer">CC BY 4.0</a>。引用した公式資料の権利は各発行元にあります。間違いのご指摘は <a href="{REPO}/issues" target="_blank" rel="noopener noreferrer">GitHub の Issue</a> へ。</p>
<p><a href="{prefix}about.html">このサイトについて</a> ・ <a href="{REPO}" target="_blank" rel="noopener noreferrer">ソース（GitHub）</a></p>
</div></footer>
<div class="viz-tip" role="status" aria-live="polite"></div>
</body>
</html>
"""
    dest = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(doc)


K = "sakura/kubiaka/"
KUBIAKA_PAGES = [
    (K + "index.html", "クビアカツヤカミキリとは"),
    (K + "identify.html", "見分け方と見回りの時期"),
    (K + "status.html", "広がり方と川崎市の状況"),
    (K + "control.html", "防除の方法"),
    (K + "rules.html", "法律と国・県・市の仕組み"),
    (K + "found.html", "見つけたら（できること・できないこと）"),
]


def kpager(i):
    prev = KUBIAKA_PAGES[i - 1] if i > 0 else ("sakura/index.html", "桜並木を守る")
    nxt = KUBIAKA_PAGES[i + 1] if i + 1 < len(KUBIAKA_PAGES) else ("action/index.html", "みんなでできること")
    return (prev, nxt)


KCRUMB = [("index.html", "ホーム"), ("sakura/index.html", "桜並木を守る")]
KCRUMB2 = KCRUMB + [(K + "index.html", "クビアカツヤカミキリ")]

FOUND_BOX = """<div class="box alert">
<h3>クビアカツヤカミキリを見つけたら</h3>
<ol>
<li><b>写真を撮る</b>（成虫・根元の木くず〈フラス〉・木の全体・場所の分かる目印）</li>
<li><b>成虫はその場でつぶす</b>。生きたまま持ち帰る・飼う・運ぶのは法律で禁止です [[kawa_0701]]</li>
<li><b>川崎市に知らせる</b>: <a href="https://logoform.jp/f/uCGbM" target="_blank" rel="noopener noreferrer">発見報告フォーム</a>、メール 30kikaku@city.kawasaki.jp、電話 044-200-3720（環境局 総務部 企画課）[[kawa_page]]</li>
</ol>
<p><a href="@/sakura/kubiaka/found.html">くわしく: 見つけたら（できること・できないこと）</a></p>
</div>"""

pages = []

# ---------------- ホーム ----------------
pages.append(dict(path="index.html", title="ホーム", section="home", crumbs=None,
    desc="神奈川県川崎市の二ヶ領用水をきれいにし、そこに暮らす生きものと水辺の自然、用水沿いの桜並木を守るための市民のプロジェクト。",
    body="""<section class="hero"><div class="inner">
<h1>武蔵小杉の二ヶ領用水にもオイカワを</h1>
<p>神奈川県川崎市を流れる<strong>二ヶ領用水</strong>をきれいにし、そこに暮らす生きものと水辺の自然を守るための、市民の調査と仕組みづくりのプロジェクトです。</p>
<p>オイカワは、きれいな流れを好む川魚です。武蔵小杉のあたりの用水にも、オイカワが泳ぐ流れを取り戻すことを目指します。</p>
</div></section><!--/hero-->
<h2>3 つの取り組み</h2>
<div class="cards">
<a class="card water" href="@/water/index.html"><h3>水と生きもの</h3><p>用水の水質・生きもの・水辺の環境と、それを損なう要因を、公式の資料と観察で調べます。</p><span class="status">一部公開</span></a>
<a class="card sakura" href="@/sakura/index.html"><h3>桜並木を守る</h3><p>用水沿いの桜並木を、特定外来生物「クビアカツヤカミキリ」の被害から守ります。</p><span class="status">公開中</span></a>
<a class="card leaf" href="@/action/index.html"><h3>みんなでできること</h3><p>見回り・記録・通報の仕組みを作り、地域の人と続けられる形にします。</p><span class="status">準備中</span></a>
</div>
""" + FOUND_BOX + """
<h2>いま知ってほしいこと</h2>
<ul>
<li>桜を枯らす外来のカミキリムシ「クビアカツヤカミキリ」が、<strong>2026 年 6 月に川崎市内（宮前区の菅生緑地）で初めて見つかりました</strong>。[[kawa_0701]]</li>
<li>二ヶ領用水沿いでの確認は、{asof} 時点で公表されていません。でも、国の防除戦略は「サクラが続く河川沿い」を、被害が広がる道すじとして重点的に見張るよう求めています。[[senryaku]]</li>
<li>早く見つけることが、桜並木を守るいちばんの近道です。散歩のついでに、桜の根元を見てください。</li>
</ul>
<h2>お知らせ</h2>
<ul>
<li><time>2026-10-19</time> 「<a href="@/water/litter.html">用水のゴミ問題</a>」のページを公開しました（{asof} 時点の情報）。</li>
<li><time>2026-10-19</time> 「<a href="@/sakura/kubiaka/index.html">クビアカツヤカミキリ</a>」のページを公開しました（{asof} 時点の情報）。</li>
</ul>
<h2>このサイトの見かた</h2>
<p>本文の右にある小さな印は出典です。<span class="src official">公式</span> は国・自治体・研究機関のページ、<span class="src web">Web</span> は報道など公式以外のページ、<span class="src est">推定</span> は公開資料からの推定（まだ確かめられていないこと）です。印を押すと、元のページが開きます。くわしくは「<a href="@/about.html">このサイトについて</a>」へ。</p>
""".replace("{asof}", ASOF)))

# ---------------- 水と生きもの ----------------
pages.append(dict(path="water/index.html", title="水と生きもの", section="water", theme="theme-water",
    crumbs=[("index.html", "ホーム")],
    desc="二ヶ領用水の水質・生きもの・水辺の環境について（準備中）。",
    body="""<h1>水と生きもの</h1>
<p class="page-meta">一部を公開しています（{asof} 時点）</p>
<p class="intro">二ヶ領用水の水質・生きもの（オイカワなどの魚、エビ・カニ、水生昆虫）・水辺の環境と、それを損なう要因を、公式の資料と観察にもとづいて調べ、このページにまとめていきます。</p>
<h2>公開中のページ</h2>
<div class="cards">
<a class="card water" href="@/water/litter.html"><h3>用水のゴミ問題</h3><p>分かっていること、知らせる先、清掃への参加のしかた、ポイ捨てを減らす手</p></a>
</div>
<h2>二ヶ領用水のあらまし</h2>
<ul>
<li>二ヶ領用水は、二ヶ領本川・上河原線・宿河原線・円筒分水から下流の区間でできています。[[kawa_kihon]]</li>
<li>武蔵小杉のある中原区を流れる「円筒分水から下流」の区間（高津区・中原区・幸区）は、<strong>川崎市が管理する普通河川で、長さは約 9.0km</strong> です。[[kawa_kihon]]</li>
<li>多摩区・高津区・中原区・幸区の約 9.2km が、国の登録記念物に登録されています。[[kawa_kinenbutsu]]</li>
<li>川崎市は 2026 年 2 月に「二ヶ領用水基本方針」を定め、市民と行政が意見を交わす場「（仮称）二ヶ領用水基本方針会議」をつくるとしています。[[kawa_kihon]]</li>
</ul>
<h2>これから調べること</h2>
<ul>
<li>公共用水域の水質の測定結果と、その読み方</li>
<li>用水にいる生きものと、オイカワがすむのに必要な条件（流れ・瀬と淵・水温・えさ）</li>
<li>生きものを損なう要因（落差・護岸・水量・ごみ・外来種など）</li>
<li>観察会・清掃を安全に、ルールを守って行う方法</li>
</ul>
<div class="box note">
<h3>生きものを採るときは</h3>
<p>魚や水の生きものを採るのは、河川・用水の管理者のルールと、法令（特定外来生物・漁業権・採捕の規制など）を確かめてからにしてください。このサイトでは、確かめられない採り方は勧めません。</p>
</div>
<h2>桜並木とのつながり</h2>
<p>用水沿いの桜をクビアカツヤカミキリから守るために薬を使うと、水の生きものに影響が出るおそれがあります。オイカワのえさになる水生昆虫は、魚よりずっと薬に弱いことがあります。くわしくは「<a href="@/sakura/kubiaka/control.html#water">防除の方法（用水のそばで）</a>」へ。</p>
""".replace("{asof}", ASOF)))

# ---------------- 水と生きもの: ゴミ問題 ----------------
pages.append(dict(path="water/litter.html", title="用水のゴミ問題", section="water", theme="theme-water",
    crumbs=[("index.html", "ホーム"), ("water/index.html", "水と生きもの")], charts=True,
    desc="二ヶ領用水（川崎市中原区の周辺）のゴミについて、公開資料で分かっていること、知らせる先、清掃への参加のしかた、ポイ捨てを減らす手。",
    body="""<h1>用水のゴミ問題</h1>
<p class="page-meta">{asof} 時点の情報</p>
<p class="intro">二ヶ領用水について市民がいちばん多く書いた困りごとは「ゴミ」でした。[[kawa_survey]] 一方で、清掃を続けてきた人からは「ゴミは大分減った」という声もあります。[[kawa_suishin10]] このページでは、武蔵小杉のある中原区の区間を中心に、公開資料で分かっていることと、お金をかけずに今日からできることをまとめます。</p>
<div class="stats">
<div class="stat"><div class="stat-label">市民アンケートの自由記述で最も多かった内容</div><div class="stat-value">31<span class="stat-unit">件</span></div><div class="stat-sub">「ゴミが目立つ」（自由記述 297 件中、2025-03〜04）[[kawa_survey]]</div></div>
<div class="stat"><div class="stat-label">用水の清掃活動を「知らない」</div><div class="stat-value">55<span class="stat-unit">%</span></div><div class="stat-sub">回答 864 件中 475 件 [[kawa_survey]]</div></div>
<div class="stat"><div class="stat-label">イベント・清掃に「興味がある」</div><div class="stat-value">77<span class="stat-unit">%</span></div><div class="stat-sub">参加しやすいのは「休日の朝」49% [[kawa_survey]]</div></div>
</div>
<h2>公開資料で分かっていること</h2>
<figure class="viz">
<figcaption><b>二ヶ領用水についての市民アンケート: 自由記述の主な内容（件数、2025 年 3〜4 月、用水全体）</b>川崎市議会 まちづくり委員会資料 [[kawa_survey]]</figcaption>
<div class="viz-chart"><script type="application/json">
{"type": "bar", "unit": "件", "digits": 0, "categoryLabel": "自由記述の内容",
 "categories": ["ゴミが目立つ", "除草", "生物・植物の保護", "樹木管理", "花見のマナー", "清掃活動への感謝", "清掃活動に参加したい"],
 "series": [{"name": "件数", "values": [31, 22, 20, 18, 17, 11, 11]}],
 "emphasis": "ゴミが目立つ"}
</script></div>
<p class="viz-note">Web（二次元バーコード）で自分から答えた人の回答です（864 件、うち中原区に住む人は 23%）。無作為に選んだ人の回答ではなく、中原区の区間だけの集計でもありません。</p>
</figure>
<p class="takeaway">ゴミを気にしている人は多いのに、清掃活動を知らない人が半数を超えています。「ゴミが気になる人」と「清掃の場」が、まだつながっていません。</p>
<ul>
<li><strong>「減った」という声</strong>: 2025-02 の市の推進会議で、市民の委員が「清掃を始めた 10 年前くらいはごみがそこそこあったが、最近は大分減った」と話しています。[[kawa_suishin10]]</li>
<li><strong>「毎日のように置かれている」という声</strong>: 基本方針のパブリックコメントには、ゴミが毎日のように置かれている、トイレの周りでたばこ・ペットボトルが捨てられる、釣り糸に鳥が絡まっていた、といった声が寄せられました。[[kawa_pubcom]]</li>
<li><strong>ごみ箱は置かない</strong>: 市は、家庭ごみが持ち込まれるおそれがあるため用水沿いにごみ箱を置かず、見回り・啓発・広報で対応するとしています。[[kawa_pubcom]]</li>
<li><strong>清掃の記録</strong>: 2024-06-02 の一斉清掃は 6 団体・171 人で、30L の袋 61 袋分を集めました。中原区の会場（コスギ アイハグ前広場）は 43 人・7 袋でした。記録は人数と袋の数だけで、ゴミの種類や重さは残っていません。[[kawa_suishin9]]</li>
</ul>
<p class="takeaway">「減った」と「毎日ある」は、どちらも本当かもしれません。用水全体では減っても、ベンチ・トイレ・橋のたもとなど、特定の場所や時間に残っている可能性があります。[[est]] これを確かめるには、<a href="#record">場所と時間を分けた記録</a>が役に立ちます。</p>

<h2>ゴミは 3 種類に分けて考える</h2>
<div class="table-wrap"><table>
<thead><tr><th>種類</th><th>例</th><th>主な対応</th></tr></thead>
<tbody>
<tr><td>(A) 用水沿いでのポイ捨て</td><td>吸い殻・飲み物の容器・お菓子の袋</td><td>きれいな状態を保つ、掲示の文面、清掃の仲間を増やす</td></tr>
<tr><td>(B) 上流・風・雨で流れ着くゴミ</td><td>水の中の袋・ボトル</td><td>定期的な清掃、管理者（市）への報告</td></tr>
<tr><td>(C) まとめて捨てる不法投棄</td><td>家電・袋ごとのゴミ</td><td>生活環境事業所に通報する（ゴミは動かさない）</td></tr>
</tbody></table></div>
<p>掲示など「ちょっとした仕掛け」が効くのは、主に (A) です。(B)(C) は、清掃と通報で対応します。</p>

<h2 id="report">見つけたら: 知らせる先</h2>
<div class="table-wrap"><table>
<thead><tr><th>こんなとき</th><th>知らせる先</th></tr></thead>
<tbody>
<tr><td>用水・護岸・柵の壊れ、ゴミがたまって流れをふさいでいる</td><td>区ごとの通報フォーム、または川崎市 LINE のメニュー「道路/公園等損傷通報」。中原区は道路公園センター（044-788-2311、開庁日 8:30〜17:15）[[kawa_tsuho]]<br>散らばったゴミの通報に使ってよいかは、確かめられていません <span class="tbc">要確認</span></td></tr>
<tr><td>家電・袋ごとのゴミなど、不法投棄</td><td>中原区は中原生活環境事業所（044-411-9220、月〜土 8:00〜16:45、電話のみ）。ゴミは動かさず、場所と種類を伝える [[kawa_fuho]]</td></tr>
<tr><td>清掃・ボランティア・用水全体の相談</td><td>川崎市 建設緑政局 道路河川整備部 河川課（環境担当）044-200-2906 [[kawa_kasenka]]</td></tr>
</tbody></table></div>

<h2 id="join">清掃に参加する</h2>
<p class="lead">新しい団体をつくらなくても、すでにある清掃の場と制度に加われます。</p>
<ul>
<li><strong>二ヶ領用水一斉清掃</strong>: 例年 6 月上旬の日曜。2026 年は 6/7（日）9:00〜10:30 でした。中原区の集合場所はコスギ アイハグ前広場（武蔵小杉駅から徒歩 5 分）。申し込みが必要で、軍手・ゴミ袋は主催者が用意します。[[seseragikan]] 2027 年の日程は、まだ公表されていません。</li>
<li><strong>灯篭流し＆清掃</strong>: 2025-09-28 に中原区で開かれ、子どもを含む約 100 人が参加しました。[[kawa_touro]]</li>
<li><strong>中原区で活動している団体</strong>: 市の基本方針は、沿川の市民活動として「二ヶ領用水中原桃の会」などを挙げています。[[kawa_honpen]] 桃の会は用水沿いのハナモモの手入れと桃まつりを行い、会員を募集していました（2024-03 時点）。[[nakahara_dayori]] 団体を知りたいときは、河川課か中原区役所 企画課（044-744-3149）に問い合わせてください。</li>
<li><strong>河川愛護ボランティア制度</strong>: 5 人以上の団体が約 200m を受け持ち、市と合意書を交わして、清掃（月 1 回程度）・除草（年 2 回程度）をします。軍手・ゴミ袋は市が支給し、年 1 回、市と意見交換会があります。二ヶ領用水は名指しで歓迎されています。個人で参加したい人は河川課に連絡します。[[kawa_aigo_flyer]] [[kawa_aigo]]</li>
<li><strong>けがへの備え</strong>: 市内の団体の活動中の事故は、市の市民活動補償制度の対象になります（事前の登録・掛け金は不要。個人だけの活動は対象外）。[[kawa_hosho]]</li>
</ul>

<h2 id="record">記録のしかた（お金をかけずに）</h2>
<p>「用水全体が汚い」ではなく、「<strong>どの区間に・いつ・何が</strong>残っているか」を記録すると、市や清掃団体が動きやすくなります。市の記録（人数・袋の数）に、品目ごとの個数を足すと、市にない情報になります。[[est]]</p>
<ol class="steps">
<li><b>区間を決める</b>橋から次の橋まで、約 200m ごとに区切って「区間 ID」を付けます（河川愛護ボランティアの受け持ちの長さに合わせる）。場所は GPS ではなく区間 ID で記録します。</li>
<li><b>同じ項目で記録する</b>日付・時刻、天気（48 時間以内の雨）、区間 ID と岸、人数、30L 袋の数、品目ごとの個数（飲み物の容器・吸い殻・包装・袋・釣り糸など）、拾ったか数えただけか。「ゴミなし」も記録します。</li>
<li><b>無料の道具でまとめる</b>入力フォーム → 表計算 → 地図で区間ごとに色分け、のように、無料のサービスで足ります。アカウントは個人ではなく団体で持ち、管理する人を 2 人以上にします。</li>
<li><b>届ける</b>区間ごとの集計を、河川課や、ボランティア制度の年 1 回の意見交換会に持っていきます。</li>
</ol>
<div class="box note">
<h3>記録を公開するときの決まり</h3>
<ul>
<li>名前は集めず、グループ名までにします。写真に人の顔・表札・車のナンバーを写さず、位置情報（EXIF）は消します。</li>
<li>子どもの記録を公開するときは、保護者と学校の同意を先にもらい、名前・学校名・顔は出しません。</li>
</ul>
</div>

<h2 id="nudge">ポイ捨てを減らすために</h2>
<p class="lead">いちばん根拠があって安いのは、「きれいな状態を保ち続ける」ことです。</p>
<ul>
<li>きれいな場所ほどポイ捨てが少ないことは、再現の実験でも確かめられています。[[flora_cialdini]] ゴミが残りやすい場所を、短い間隔で拾い続けるのが基本です。</li>
<li>掲示や SNS で「ゴミが多い」と強調すると、「みんな捨てている」という印象を与えて、かえって逆効果になることがあります。[[est]]</li>
</ul>
<h3>掲示・発信の文面の順番</h3>
<ol>
<li>この用水を大切にしている人がたくさんいます</li>
<li>それでも、ここに、これ（例: 吸い殻）が残っています</li>
<li>持ち帰ってください</li>
<li>ありがとう</li>
</ol>
<h3>子どもが描いた絵の掲示</h3>
<p>費用が安く、家族が関わる入口にもなります。ただし、掲示だけでポイ捨てが減るという根拠は強くありません。子どもの絵に「ポイ捨て禁止」を添えたごみ箱では、ごみ箱にゴミを入れる人がかえって減り、逆効果だった実験もあります。[[beijer_gavle]] 使うときは次のようにします。[[est]]</p>
<ul>
<li>元気な生きもの（魚・カモなど）を、目が正面を向くように描く。ゴミや泣き顔は描かない</li>
<li>文面は「ありがとう」と「持ち帰ってね」を主にして、禁止の言葉を主にしない</li>
<li>清掃の直後に貼り、4〜6 週で描き替える。傷んだら、すぐに外す</li>
<li>用水沿いに貼るときは、管理者（市）の許可の条件を先に確かめる <span class="tbc">要確認</span></li>
</ul>
<div class="box alert">
<h3>使わない手</h3>
<ul>
<li>偽の防犯カメラや「監視中」の嘘</li>
<li>特定の人たちを名指しして責めること</li>
<li>新しいごみ箱（市は家庭ごみの持ち込みを心配して置かない方針です [[kawa_pubcom]]）</li>
</ul>
</div>

<h2 id="kids">子どもと一緒に清掃するとき</h2>
<ul>
<li>用水には入らず、岸からトング（マジックハンド）で拾います。</li>
<li>水際の水草は、生きもののすみかなので取りません。[[kawa_suishin10]]</li>
<li>護岸の作りから、子どもが清掃しやすい場所は限られます。場所は下見して決めます。[[kawa_suishin10]]</li>
<li>中原区では、小学 5 年生 84 人が市長と清掃した例（2024-06）や、子どもが作ったポスターを用水に貼った例があります。[[kawa_suishin9_log]]</li>
</ul>

<h2 id="money">使える支援</h2>
<p>市・区の助成は、規約のある団体が対象で、個人では申し込めません。締め切りは {asof} 時点の情報です。必ず元のページで確かめてください。</p>
<div class="table-wrap"><table>
<thead><tr><th>支援</th><th>対象・内容</th><th>締め切り・時期</th></tr></thead>
<tbody>
<tr><td>セブン-イレブン記念財団 地域美化助成（2027 年度）[[seven_josei]]</td><td>地域住民が中心の非営利の任意団体。最大 50 万円/年（道具・ゴミの運搬処理・保険など）</td><td>2026-10-30（金）</td></tr>
<tr><td>河川財団 河川基金 学校部門 [[kasen_kikin]]</td><td>学校が申し込む。単学年 20 万円まで。活動は 2027-04〜2028-03</td><td>2026-11-13（金）17:00</td></tr>
<tr><td>かわさき市民公益活動助成金 スタートアップ</td><td>3 人以上・発足 3 年未満の団体。10 万円以内。申し込み前の相談が必要</td><td>例年 12 月上旬に募集開始 <span class="tbc">要確認</span></td></tr>
<tr><td>中原区 市民提案型協働事業</td><td>区の負担は最大 30 万円。窓口は中原区役所 企画課</td><td>例年 1 月ごろに募集開始 <span class="tbc">要確認</span></td></tr>
</tbody></table></div>
<p>仲間を探す場として、中原区の住民・団体・区役所が集まる「なかはら SDC」の定例会 YORIAI（申し込み不要・オンライン可）もあります。[[nakahara_sdc]] 中原区は 2014〜16 年の区民会議で「ごみ問題」を取り上げ、ポイ捨て禁止の看板を試したこともあります。[[nakahara_kumin]]</p>

<h2>まだ分かっていないこと</h2>
<ul>
<li>中原区の区間で、どこに・いつ・何のゴミが多いか（区間ごとの記録がまだない）</li>
<li>市の通報フォームで、散らばったゴミを受け付けているか</li>
<li>単発のボランティア清掃で出たゴミの回収方法と、トングなどの道具の貸し出し</li>
<li>用水沿いにポスターを貼るときの許可の条件</li>
<li>2027 年の一斉清掃の日程と、市の「（仮称）二ヶ領用水基本方針会議」の開かれ方</li>
<li>議会で二ヶ領用水のゴミが話し合われたか</li>
</ul>
""".replace("{asof}", ASOF)))

# ---------------- 桜並木を守る ----------------
pages.append(dict(path="sakura/index.html", title="桜並木を守る", section="sakura", theme="theme-sakura",
    crumbs=[("index.html", "ホーム")], charts=True,
    desc="二ヶ領用水沿いの桜並木のあらましと、クビアカツヤカミキリから守るための情報。",
    pager=(("index.html", "ホーム"), (K + "index.html", "クビアカツヤカミキリとは")),
    body="""<h1>桜並木を守る</h1>
<p class="page-meta">{asof} 時点</p>
<p class="intro">二ヶ領用水は「桜の名所」として知られています。[[kawa_iinkai]] その桜並木を、特定外来生物「クビアカツヤカミキリ」の被害から守るための情報をまとめています。</p>
<h2>クビアカツヤカミキリのページ</h2>
<div class="cards">
<a class="card sakura" href="@/sakura/kubiaka/index.html"><h3>クビアカツヤカミキリとは</h3><p>どんな虫か、要点のまとめ</p></a>
<a class="card sakura" href="@/sakura/kubiaka/identify.html"><h3>見分け方と見回りの時期</h3><p>成虫・フラス（木くず）の見分け方、季節ごとに見るもの</p></a>
<a class="card sakura" href="@/sakura/kubiaka/status.html"><h3>広がり方と川崎市の状況</h3><p>全国・神奈川・川崎市、二ヶ領用水への危険度</p></a>
<a class="card sakura" href="@/sakura/kubiaka/control.html"><h3>防除の方法</h3><p>方法ごとの効果、用水のそばでの注意、費用と補助</p></a>
<a class="card sakura" href="@/sakura/kubiaka/rules.html"><h3>法律と国・県・市の仕組み</h3><p>外来生物法、だれが何をするのか、国の最新の動き</p></a>
<a class="card sakura" href="@/sakura/kubiaka/found.html"><h3>見つけたら</h3><p>市民・子どもができること、できないこと、通報先</p></a>
</div>
<h2>二ヶ領用水の桜並木のあらまし</h2>
<ul>
<li>川崎市は昭和 60（1985）年ごろから、用水の護岸に桜などを植えてきました。[[kawa_kihon]]</li>
<li>市が管理する河川全体で、高さ 3m 以上の木は約 2,700 本あり、いちばん多いのはサクラです。樹木医の外観の診断で、伐採の対象になった木は 101 本でした。[[kawa_ijigaiyou]]</li>
<li>市は「植えた時期や管理区分が分からない木が多く、老木化が進んでいる」と書いています。[[kawa_ijigaiyou]] 1 本ずつの位置・樹齢の台帳は公開されていません。</li>
<li>多摩区の宿河原の桜並木は、地元の町会・保存会も育て、手入れをしています。[[kankou]]</li>
</ul>
<p class="lead">市の 5 年間の計画では、武蔵小杉のある中原区の区間で、伐採の予定がいちばん多くなっています。</p>
<figure class="viz">
<figcaption><b>二ヶ領用水の区間ごとの、樹木の伐採・植樹の計画本数（川崎市、2024〜2028 年度の 5 年間）</b>川崎市「河川維持管理実施計画【河川樹木編】」[[kawa_jumoku]]</figcaption>
<div class="viz-chart"><script type="application/json">
{"type": "bar", "unit": "本", "digits": 0, "categoryLabel": "区間（区）",
 "categories": ["円筒分水下流（中原区）", "二ヶ領本川（多摩区）", "円筒分水下流（高津区）", "上河原線（多摩区）", "円筒分水下流（幸区）", "宿河原線（多摩区）"],
 "series": [{"name": "伐採", "values": [49, 16, 11, 7, 5, 4]}, {"name": "植樹", "values": [24, 6, 10, 1, 12, 0]}]}
</script></div>
<p class="viz-note">桜以外の樹木も含む計画本数です。この計画は、川崎市でクビアカツヤカミキリが見つかる前（2024-03）に作られたもので、クビアカツヤカミキリについての記述はありません。</p>
</figure>
<p class="takeaway">伐採の予定が多いことは、弱った木・古い木が多いことの目安になります。弱った木はクビアカツヤカミキリに食べられると、枝が落ちたり倒れたりする危険が早く高まります。[[osaka]] 中原区の区間は、見回りでとくに気をつけたい区間です。[[est]]</p>
<h2>区間と管理者</h2>
<div class="table-wrap"><table>
<thead><tr><th>区間</th><th>区</th><th>種類と管理者</th><th>長さ</th></tr></thead>
<tbody>
<tr><td>円筒分水から下流</td><td>高津区・中原区・幸区</td><td>普通河川・川崎市</td><td>約 9.0km</td></tr>
<tr><td>宿河原線</td><td>多摩区</td><td>準用河川・川崎市</td><td>約 2.2km</td></tr>
<tr><td>上河原線</td><td>多摩区</td><td>準用河川・川崎市</td><td>約 1.2km</td></tr>
<tr><td>二ヶ領本川の一部</td><td>多摩区〜高津区</td><td>一級河川・神奈川県（工事と維持は協定で市が行う）[[kawa_honsen]]</td><td>約 6.06km</td></tr>
</tbody></table></div>
<p>出典: [[kawa_kihon]]。市の河川維持管理計画は、「河川樹木」を管理する施設に含めています。[[kawa_iji]] 用水沿いの桜 1 本ずつが、川の土地の木なのか、緑道（公園）の木なのか、道路の木なのかは、確かめられていません。<span class="tbc">要確認</span></p>
<h2>植え替えの方針と、クビアカツヤカミキリ</h2>
<p>市の計画では、ソメイヨシノを、てんぐ巣病に強いジンダイアケボノ・コマツオトメなどに植え替えていくとしています。[[kawa_jumoku]] ただし、これらもサクラなので、クビアカツヤカミキリの被害を受けます。[[osaka]] 計画が作られたのはクビアカツヤカミキリが市内で見つかる前のため、これからの見直しが大切になります。[[est]]</p>
""".replace("{asof}", ASOF)))

# ---------------- クビアカ: index ----------------
pages.append(dict(path=K + "index.html", title="クビアカツヤカミキリとは", section="sakura", theme="theme-sakura",
    crumbs=KCRUMB, pager=kpager(0),
    desc="桜を枯らす特定外来生物クビアカツヤカミキリの要点。川崎市・二ヶ領用水の桜並木を守るために。",
    body="""<h1>クビアカツヤカミキリとは</h1>
<p class="page-meta">{asof} 時点の情報</p>
<p class="intro">中国などから来たカミキリムシです。幼虫が桜の幹の中を 2 年ほど食べ続け、木を枯らします。2018 年に「特定外来生物」に指定され、生きたまま飼う・運ぶ・放すことが法律で禁止されています。[[env_info]] [[funabashi]]</p>
<div class="stats">
<div class="stat"><div class="stat-label">確認された都府県</div><div class="stat-value">22<span class="stat-unit">都府県</span></div><div class="stat-sub">2026-08 時点 [[maff_status]]</div></div>
<div class="stat"><div class="stat-label">確認された市町村</div><div class="stat-value">300<span class="stat-unit">超</span></div><div class="stat-sub">2026-09 時点 [[senryaku]]</div></div>
<div class="stat"><div class="stat-label">川崎市での初確認</div><div class="stat-value">2026<span class="stat-unit">年 6 月</span></div><div class="stat-sub">宮前区の菅生緑地 [[kawa_0701]]</div></div>
</div>
<h2>要点</h2>
<div class="box key">
<ul>
<li><strong>見つける手がかり</strong>は、桜の根元にたまる、うどんやかりんとうのような木くず（フラス）です。フラスは 4〜10 月ごろに出ます。[[kawa_page]] → <a href="@/sakura/kubiaka/identify.html">見分け方</a></li>
<li><strong>川崎市では</strong>、2026 年 6 月に宮前区の菅生緑地で見つかりました。その後、市内で新たに見つかったという公式の発表は、{asof} 時点でありません。二ヶ領用水沿いでの確認も公表されていません。[[kawa_page]] → <a href="@/sakura/kubiaka/status.html">広がり方</a></li>
<li><strong>いちばん確実な防除</strong>は、被害を受けた木を伐って根まで取り除くことです。用水のそばでは、薬を散布しないのが原則です。[[osaka]] → <a href="@/sakura/kubiaka/control.html">防除の方法</a></li>
<li><strong>国が大きく動いています</strong>。2026 年 7 月に政府の対策本部ができ、9 月に防除戦略が決まり、10 月には予備費を使った交付金の追加公募が始まりました。[[env_honbu]] [[env_koubo]] → <a href="@/sakura/kubiaka/rules.html">仕組みと最新の動き</a></li>
<li><strong>市民ができるいちばん大事なこと</strong>は、見回って、写真で市に知らせることです。→ <a href="@/sakura/kubiaka/found.html">見つけたら</a></li>
</ul>
</div>
""" + FOUND_BOX + """
<h2>どんな木がやられるか</h2>
<p>バラ科のサクラの仲間です。サクラ（ソメイヨシノ・オオシマザクラ・ヤマザクラ）、モモ（ハナモモを含む）、ウメ、スモモ、アンズなど。[[ffpri3]] [[senryaku]] 街の桜並木に多いソメイヨシノは、やられる本数がとくに多い木です。[[ffpri3]]</p>
<h2>どうなるか</h2>
<p>幼虫が幹の内側（養分を運ぶ層）を食べると、その先の枝が枯れ、木が弱ります。幼虫が多いと 1 年〜数年で枯れることがあります。弱ったり枯れたりした木は、枝が落ちたり倒れたりして、人がけがをするおそれもあります。[[ffpri3]] [[senryaku]]</p>
""".replace("{asof}", ASOF)))

# ---------------- 見分け方 ----------------
pages.append(dict(path=K + "identify.html", title="見分け方と見回りの時期", section="sakura", theme="theme-sakura",
    crumbs=KCRUMB2, pager=kpager(1),
    desc="クビアカツヤカミキリの成虫とフラス（木くず）の見分け方、似ている在来の虫との違い、季節ごとの見回りのポイント。",
    body="""<h1>見分け方と見回りの時期</h1>
<p class="page-meta">{asof} 時点</p>
<p class="intro">成虫は、黒い体に赤い「首」が目印です。でも成虫が見られるのは夏の短い間だけ。一年の多くの時期は、根元にたまるフラス（幼虫が出す木くずとフンが混ざったもの）が手がかりです。</p>
<h2>一年の暮らし（ふつうは 2 年で 1 世代）</h2>
<div class="table-wrap"><table>
<thead><tr><th>時期</th><th>起きること</th></tr></thead>
<tbody>
<tr><td>6 月初め〜7 月下旬（地域・年により 5〜8 月）</td><td>成虫が幹から出てくる [[ffpri3]] [[kyoto]] [[gunma_flyer]]</td></tr>
<tr><td>出てすぐ</td><td>交尾して、樹皮の割れ目に卵を産む。平均 300 個、多いと 1,000 個以上 [[kyoto]]</td></tr>
<tr><td>約 10 日〜2 週間後</td><td>卵がかえり、幼虫はすぐ樹皮の下に潜る [[kyoto]]</td></tr>
<tr><td>2 年間</td><td>幼虫が幹の中で育つ（冬は休む）。3 年目の初夏にさなぎになり、約 1 か月で成虫に [[kyoto]] [[ffpri3]]</td></tr>
<tr><td>4〜10 月ごろ</td><td>幼虫がフラスを外に押し出す [[kawa_page]]</td></tr>
</tbody></table></div>
<h2>成虫の見分け方</h2>
<p>体長は約 2.5〜4cm。体全体がつやのある<strong>青みがかった黒</strong>で、<strong>前胸（首の部分）だけが赤い</strong>のが目印です。前胸の両わきに、とげのような出っぱりが 1 対あります。オスの触角は体よりずっと長いです。[[env_doutei]] つかまえると強いにおいの液を出します。[[kyoto]]</p>
<div class="table-wrap"><table>
<thead><tr><th>似ている虫</th><th>違い</th></tr></thead>
<tbody>
<tr><td>ジャコウカミキリ（在来）</td><td>前胸は同じく赤いが、体が緑〜青緑で、黒っぽくない。国内では北海道にしかいない [[env_doutei]]</td></tr>
<tr><td>ベニカミキリ（在来）</td><td>小さい。首だけでなく、羽（背中）も赤い [[kyoto]]</td></tr>
<tr><td>チャイロホソヒラタカミキリ</td><td>小さい。前胸が「ビーズ型」（クビアカツヤカミキリは「そろばんの珠型」）[[kyoto]]</td></tr>
<tr><td>マメハンミョウ</td><td>小さい。赤いのは頭 [[kyoto]]</td></tr>
</tbody></table></div>
<p>迷ったら、自分で決めずに写真を撮って、「疑い」として市に知らせれば十分です。</p>
<h2>フラス（木くず）の見分け方</h2>
<div class="table-wrap"><table>
<thead><tr><th>だれのフラスか</th><th>特徴</th></tr></thead>
<tbody>
<tr><td><strong>クビアカツヤカミキリ</strong></td><td>明るいオレンジ〜茶色。<strong>うどん・ひき肉・かりんとう</strong>のように連なって出る。大きさのそろった薄い木片が多い。<strong>根元に積もるほど大量</strong>に出る [[kyoto]] [[gunma_flyer]] [[ffpri3]]</td></tr>
<tr><td>コスカシバ（在来のガ）</td><td>黒っぽいコロコロした粒のフンが目立つ。こぶや枝の分かれ目に出る。量はずっと少なく、根元に積もることはほとんどない [[ffpri3]]</td></tr>
<tr><td>ゴマダラカミキリ（在来）</td><td>色は似ているが、木くずが、引きちぎったようなささくれた長い繊維になっている [[ffpri3]]</td></tr>
<tr><td>アリの通り道（蟻道）</td><td>木くずが、幹の上に道のように細長く付く [[ffpri3]]</td></tr>
</tbody></table></div>
<ul>
<li><strong>成虫が出ていった穴</strong>は、縦長のだ円で、縦 2〜3cm。冬でも見える手がかりです。[[gunma_flyer]]</li>
<li>ねっとりした新しいフラスなら、幼虫は穴の近くにいます。乾いたパラパラのフラスが多ければ、木の奥にいます。[[ffpri3]]</li>
</ul>
<h2 id="calendar">見回りカレンダー（川崎あたり）</h2>
<p class="lead">年に 1 回しか見られないなら、お盆過ぎ（8 月下旬）がいちばん見落としが少ない時期です。[[ffpri4]]</p>
<ol class="timeline" aria-label="見回りカレンダー">
<li><time>4〜5 月</time><b>フラスが出始める</b><p>根元を一周して見る [[kawa_page]]</p></li>
<li><time>6〜7 月（8 月まで）</time><b>成虫とフラス</b><p>晴れた日に幹の上にいる成虫を探す [[ffpri3]]</p></li>
<li class="key"><span class="badge">重点</span><time>8 月下旬</time><b>お盆過ぎの見回り</b><p>フラスの出ている木がいちばん多い時期 [[ffpri4]]</p></li>
<li><time>9〜10 月</time><b>フラスはまだ出る</b><p>「被害なし」も記録しておくと、次の年の比べる材料になる</p></li>
<li><time>11〜3 月</time><b>成虫が出た穴・古いフラスの跡・枝枯れ</b><p>被害を受けた木を伐るのに向く時期（管理者が行う）[[kyoto]]</p></li>
</ol>
<p class="takeaway">見るのは根元から目の高さまでで十分です。脚立に乗ったり、木に登ったりしないでください。</p>
""".replace("{asof}", ASOF)))

# ---------------- 広がり方 ----------------
pages.append(dict(path=K + "status.html", title="広がり方と川崎市の状況", section="sakura", theme="theme-sakura",
    crumbs=KCRUMB2, pager=kpager(2), charts=True,
    desc="クビアカツヤカミキリの全国・神奈川県・川崎市での広がり方と、二ヶ領用水の桜並木への危険度。",
    body="""<h1>広がり方と川崎市の状況</h1>
<p class="page-meta">{asof} 時点。新しい確認があれば、数は変わります</p>
<p class="intro">2012 年に 1 県だったのが、2026 年 8 月には 22 都府県に広がりました。川崎市でも 2026 年 6 月に初めて見つかっています。</p>
<h2>全国</h2>
<p class="lead">2026 年だけで 6 県増えていて、広がる速さが上がっています。</p>
<figure class="viz">
<figcaption><b>クビアカツヤカミキリが確認された都府県の数（累計、全国、2012〜2026 年 8 月）</b>農林水産省「確認状況（令和 8 年 8 月時点）」の初確認年の表から数えた累計 [[maff_status]]</figcaption>
<div class="viz-chart"><script type="application/json">
{"type": "line", "unit": "都府県", "digits": 0, "zero": true, "categoryLabel": "年",
 "categories": ["2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026(8月)"],
 "series": [{"name": "累計", "values": [1, 2, 2, 6, 7, 8, 8, 11, 11, 12, 13, 13, 15, 16, 22]}]}
</script></div>
<p class="viz-note">暦年での数え方です。年度で数える資料とは、数がずれることがあります。2026 年は 8 月までの値。2026-08 時点の 22 都府県は、長野県の資料とも一致します。[[nagano]]</p>
</figure>
<p class="takeaway">2026 年に新しく加わったのは、岐阜・山梨・香川・岡山・長野・福井です。[[maff_status]] 市町村の数では、2026 年 9 月時点で 300 を超えています。[[senryaku]] 神奈川県は 2021 年に加わりました。</p>
<h2>どう広がるか</h2>
<ul>
<li>成虫はよく飛び、1 年に 2〜3km 広がります。車や鉄道に付いて、遠くまで運ばれることもあります。[[kyoto]]</li>
<li>新しく被害が出る場所の多くは、すでに被害がある所から 3km 以内です。でも、約 40km 離れた所に飛び地のように出ることもあります。[[senryaku]]</li>
<li>主要な道路の沿線と、<strong>サクラが続く河川沿い</strong>が、広がる道すじになりえます。[[senryaku]]</li>
</ul>
<h2>神奈川県内</h2>
<div class="table-wrap"><table>
<thead><tr><th>確認時期</th><th>市町村（区）</th><th>内容</th></tr></thead>
<tbody>
<tr><td>2021 年度</td><td>藤沢市</td><td>成虫・フラス被害（サクラ）</td></tr>
<tr><td>2024 年度</td><td>相模原市南区</td><td>成虫</td></tr>
<tr><td>2025 年度</td><td>相模原市南区</td><td>フラス被害（サクラ・ウメ）</td></tr>
<tr><td>2026-06</td><td>小田原市</td><td>成虫</td></tr>
<tr><td>2026-06</td><td><strong>川崎市宮前区</strong></td><td>幼虫・フラス被害（サクラ）・成虫</td></tr>
<tr><td>2026-06</td><td>横浜市青葉区</td><td>幼虫・フラス被害（サクラ）</td></tr>
<tr><td>2026-07</td><td>相模原市南区、小田原市</td><td>成虫、成虫・フラス被害の疑い（ウメ）</td></tr>
<tr><td>2026-07</td><td>中井町</td><td>成虫・幼虫の疑い・フラス被害の疑い（ウメ）</td></tr>
<tr><td>2026-08</td><td>三浦市</td><td>フラス被害の疑い（サクラ）</td></tr>
</tbody></table></div>
<p>出典: [[kanagawa]]（2026-09-04 更新。{asof} 時点でこれより新しい更新はありません）。横須賀市の「疑い」は、本種の可能性が低いとして一覧から外されています。</p>
<h2>川崎市</h2>
<ol class="timeline" aria-label="川崎市での経過">
<li class="done"><time>2026-06-18</time><b>菅生緑地（宮前区）の桜で、幼虫らしきものとフラスが見つかり通報</b><p>造園の組合の人が見つけた [[townnews_0710]]</p></li>
<li class="done"><time>2026-06-19</time><b>市が桜 4 本に、幼虫を退治する薬を入れる</b><p>[[kawa_0626]]</p></li>
<li class="done"><time>2026-06-30</time><b>菅生緑地で成虫を確認（市内初）</b><p>7-01 に発表 [[kawa_0701]]</p></li>
<li class="done"><time>2026-07-14〜08-31</time><b>市が発見情報を募集</b><p>終了後も、フォーム・メール・電話で受け付けている [[kawa_0714]]</p></li>
<li class="done"><time>2026-09-09</time><b>市議会の代表質問で「クビアカツヤカミキリへの対応」が取り上げられる</b><p>[[kawa_council]]（答弁の中身は、会議録の公開待ち）</p></li>
<li class="now"><span class="badge">今</span><time>{asof}</time><b>市内で新たに見つかったという公式の発表はない</b><p>担当課の関連記事は 2026-09-01 が最後 [[kawa_kikaku]]</p></li>
</ol>
<p>菅生緑地の 4 本をその後どうしたか（伐ったか）、周りを調べた結果、募集で集まった情報の件数は、{asof} 時点で公表されていません。<span class="tbc">要確認</span> 「発表がない」ことは「いない」ことを意味しません。</p>
<h2>まわりの自治体</h2>
<div class="table-wrap"><table>
<thead><tr><th>自治体</th><th>状況</th></tr></thead>
<tbody>
<tr><td>横浜市</td><td>青葉区で確認。見つかった公園のまわりの公園 85 か所・街路樹 12 路線・川 1 本を調べ、被害の可能性がある木が公園で 7 本、街路樹で 14 本見つかった。川沿いではなし（2026-07-10）[[yokohama]]</td></tr>
<tr><td>町田市（麻生区と接する）</td><td>2025 年度に確認。東京都では 8 区 10 市 2 町 [[tokyo]]</td></tr>
<tr><td>稲城市・狛江市・調布市</td><td>東京都の被害の一覧には載っていない [[tokyo]]</td></tr>
<tr><td>世田谷区・大田区</td><td>「確認されていない」とあるが、ページの更新が 2025 年と古い [[setagaya]] [[ota]]</td></tr>
</tbody></table></div>
<h2>二ヶ領用水の桜並木への危険度</h2>
<p class="lead">二ヶ領用水沿いではまだ確認されていませんが、危険度は「中〜高」と見ています。[[est]]</p>
<div class="table-wrap"><table>
<thead><tr><th>理由</th><th>中身</th></tr></thead>
<tbody>
<tr><td>近くで見つかっている</td><td>同じ市の宮前区と、隣の横浜市青葉区・町田市 [[kanagawa]] [[tokyo]]</td></tr>
<tr><td>川沿いの桜並木は通り道</td><td>国の防除戦略は「サクラが続く河川沿い」を重点的に見張る場所にしている [[senryaku]]</td></tr>
<tr><td>距離</td><td>菅生緑地から用水の多摩区の区間までは数 km、中原区までは 10km 前後とみられる。中原区には、飛んで来るより先に、車などで運ばれて飛び地のように出る心配のほうが大きい [[est]]</td></tr>
<tr><td>古い木が多い</td><td>中原区の区間は、市の計画で伐採の予定が最も多い [[kawa_jumoku]]</td></tr>
<tr><td>分かれ目の時期</td><td>菅生緑地で 2026 年の初夏に卵が産まれていれば、2 年後の 2028 年初夏に成虫になりうる。それまでに対策できるかが分かれ目 [[est]]</td></tr>
</tbody></table></div>
<p class="takeaway">いちばん効く備えは、2027 年の 4〜8 月に、根元のフラスをこまめに見て回ることです。</p>
<h2>まだ分かっていないこと</h2>
<ul>
<li>菅生緑地の被害木のその後、周りの調査の結果、募集の結果</li>
<li>川崎市が二ヶ領用水沿い・公園・街路樹を一斉に調べたか</li>
<li>神奈川県の「地域防除戦略」で、川崎市がどの区分（ゾーン）に入るか（<a href="@/sakura/kubiaka/rules.html#zoning">ゾーニング</a>）</li>
<li>二ヶ領用水までの正確な距離（地図で測ったものではありません）</li>
</ul>
""".replace("{asof}", ASOF)))

# ---------------- 防除 ----------------
pages.append(dict(path=K + "control.html", title="防除の方法", section="sakura", theme="theme-sakura",
    crumbs=KCRUMB2, pager=kpager(3),
    desc="クビアカツヤカミキリの防除の方法ごとの効果と時期、用水のそばでの注意、費用と補助、植え替え。",
    body="""<h1>防除の方法</h1>
<p class="page-meta">{asof} 時点。防除は、木の持ち主・管理者が行います（市民が自分で行うものではありません）</p>
<p class="intro">いちばん確実なのは、被害を受けた木を伐って根まで取り、砕くか燃やすことです。ほかの方法は、木を長持ちさせ、広がりを抑えるための手段で、100% 駆除できるものではありません。[[ffpri4]] [[tokyo]]</p>
<div class="box key"><p>国の防除戦略では、新しく被害が見つかった「飛び地」のような地域では、伐倒・伐根を第一に、短い期間で地域から根絶することを最優先にしています。[[senryaku]] 見つかったばかりの川崎市は、この考え方に近い位置にあると見られます。[[est]]</p></div>
<h2>方法ごとの比較</h2>
<p>「手引書」は、大阪府立環境農林水産総合研究所の「被害対策の手引書（改訂第 6 版、2026-04）」です。[[osaka]]</p>
<div class="table-wrap"><table>
<thead><tr><th>方法</th><th>何に効くか</th><th>効果の目安</th><th>時期</th></tr></thead>
<tbody>
<tr><td><strong>伐倒・伐根＋処分</strong>（砕く・燃やす・燻蒸）</td><td>木の中の幼虫・さなぎすべて</td><td>いちばん高い [[ffpri4]]</td><td>9 月〜翌 4 月</td></tr>
<tr><td>伐根できない切り株を覆う</td><td>切り株の幼虫</td><td>ネット・シートで二重に覆い約 2 年（手引書）</td><td>伐倒と同時</td></tr>
<tr><td>幼虫の掘り取り・針金で刺す</td><td>樹皮の下の若い幼虫</td><td>数値なし。持ち主の同意が必ず要る（手引書）</td><td>4〜11 月</td></tr>
<tr><td>フラスの出る穴に薬を入れる</td><td>穴の奥の幼虫</td><td>成功率は約 5 割 [[ffpri4]]</td><td>4〜11 月</td></tr>
<tr><td>樹幹注入（根元に穴をあけて薬を入れる）</td><td>木全体の幼虫</td><td>2 週間以内に穴の 72% でフラスが止まった（ソメイヨシノ 5 本の試験）[[ffpri2020]]。くり返すと木を傷めるので 1 回だけ（手引書）</td><td>4 月下旬〜9 月（6 月までが最良）</td></tr>
<tr><td>ネット巻き（被害木から成虫を出さない）</td><td>出てきた成虫</td><td>数値なし。中の成虫はこまめに殺す必要がある（手引書）</td><td>10〜5 月に巻き、8〜9 月に外す</td></tr>
<tr><td>すき間をあけたネット（被害のない木に卵を産ませない）</td><td>産卵</td><td>数値なし。ネットは野外で 5 年以上もつ（手引書）</td><td>10〜5 月に巻く</td></tr>
<tr><td>成虫が出る穴をふさぐ</td><td>これから出る成虫</td><td>約 6 割の脱出を防ぐ（手引書）</td><td>1〜5 月</td></tr>
<tr><td>薬の散布</td><td>成虫</td><td><strong>川・水路のそばでは行わない</strong>（手引書）</td><td>6〜8 月</td></tr>
<tr><td>燻蒸（伐った木をシートで覆いガスで殺す）</td><td>伐った木の中の幼虫</td><td>14 日以上（手引書）</td><td>9〜3 月</td></tr>
<tr><td>成虫をその場でつぶす</td><td>成虫</td><td>防除の効果は高くないが、関心を広げる効果がある [[ffpri4]]</td><td>6〜8 月</td></tr>
<tr><td>（研究中）ボトル型の毒餌</td><td>ネットの中の成虫</td><td>駆除率 22〜53%（2 本の試験）。まだ使えない [[ffpri_bottle]]</td><td>—</td></tr>
</tbody></table></div>
<p>試験の数値は、方法ごとに測ったものが違い、試験の本数も少ないため、目安として見てください。農薬は登録どおりに使う必要があります。最新の登録は [[pesticide]] で確かめられます。</p>
<h2>被害の程度による使い分け</h2>
<div class="table-wrap"><table>
<thead><tr><th>程度（フラスの出ている穴の数）</th><th>被害が広がった地域での考え方</th></tr></thead>
<tbody>
<tr><td>なし（0）</td><td>見回りを続ける。予防のための樹幹注入は勧められていない [[ffpri4]]</td></tr>
<tr><td>軽い（1〜3）</td><td>掘り取り・穴に薬 [[ffpri4]] [[saitama]]</td></tr>
<tr><td>中くらい（4〜9）</td><td>樹幹注入（1 回だけ）＋ネット [[ffpri4]] [[osaka]]</td></tr>
<tr><td>重い（10 以上）・枯れかけ</td><td>伐倒（枝が落ちる・倒れる危険もある）[[ffpri4]] [[saitama]]</td></tr>
</tbody></table></div>
<p>見つかったばかりの地域では、軽い木でも伐倒・伐根を第一に考えるのが基本です。[[senryaku]]</p>
<h2 id="water">用水のそばで: 魚と水の虫を守るために</h2>
<p class="lead">魚にはほとんど効かない薬でも、オイカワのえさになる水の虫には強く効くことがあります。</p>
<div class="stats">
<div class="stat"><div class="stat-label">ジノテフラン（樹幹注入の薬の成分）で、ユスリカの幼虫の半数が動けなくなる濃度</div><div class="stat-value">36<span class="stat-unit">µg/L</span></div><div class="stat-sub">魚（コイなど）は 97,260 µg/L を超えても半数が死なない [[env_dino]]</div></div>
<div class="stat"><div class="stat-label">ペルメトリン（ピレスロイド系の殺虫成分の一例）の基準値</div><div class="stat-value">0.17<span class="stat-unit">µg/L</span></div><div class="stat-sub">魚にもミジンコにも強く効く [[env_perm]]</div></div>
</div>
<p class="takeaway">ジノテフランは、水の虫が魚より 2,700 倍以上弱い計算になります。オイカワは水の虫を食べるので、魚が無事でも、えさが減るおそれがあります。用水沿いでは散布をせず、伐倒・伐根とネットを中心に考えるのがよいと考えています。</p>
<ul>
<li>薬を使うかどうかは、管理者（市）が決めます。</li>
<li>薬の準備や詰め替えは水路から離れた場所で行い、余った薬・空き容器は持ち帰り、器具を水路で洗わない。雨の前後は避ける。[[est]]</li>
<li>伐倒のときも、切りくず・フラスを用水に落とさないようシートを敷き、護岸を崩さないようにする。オイカワが卵を産む初夏は、できれば作業を避ける。[[est]]</li>
<li>「水から何 m 離せば安全」という公式の距離は、見つかっていません。</li>
</ul>
<h2>費用と補助</h2>
<ul>
<li><strong>公共の木</strong>（公園・街路・用水）は管理者（市など）が、<strong>私有の木</strong>は持ち主が費用を負担するのが基本です。[[senryaku]]</li>
<li><strong>国の交付金</strong>: 自治体の防除事業に、費用の 1/2 以内を交付します。市町村や民間団体が行う防除への補助も対象に含まれます。[[env_jigyo]] 詳しくは「<a href="@/sakura/kubiaka/rules.html#money">お金の仕組み</a>」へ。</li>
<li><strong>自治体の補助の例</strong>: 加須市（埼玉）は私有の木の防除費用の 1/2 を補助（各経費の上限 10 万円）。[[kazo]] 山梨県は、緊急に薬をまいた費用を全額補助しています。[[yamanashi]]</li>
<li><strong>川崎市・神奈川県の補助</strong>: {asof} 時点で、見つけられませんでした。<span class="tbc">要確認</span></li>
<li>伐倒・樹幹注入の 1 本あたりの費用は、公的な資料に金額が見つかりませんでした。樹幹注入の薬の量は幹の太さで決まるので、太い老木ほど高くなります。[[osaka]]</li>
</ul>
<h2>伐った後の植え替え</h2>
<p>地域に虫が残っていると、同じサクラの若木を植えても、育ってからまたやられます。防除を続ける手間と費用をかけられないなら、バラ科以外の木を考えます。サクラ・モモ・ウメ・スモモ・アンズは避けます。[[osaka]] 「この木がよい」と名前を挙げた公式の資料はありません。「桜の名所」である二ヶ領用水では、景観・護岸への影響・地域の合意をふまえて決めることになります。[[est]]</p>
""".replace("{asof}", ASOF)))

# ---------------- 法律と仕組み ----------------
pages.append(dict(path=K + "rules.html", title="法律と国・県・市の仕組み", section="sakura", theme="theme-sakura",
    crumbs=KCRUMB2, pager=kpager(4),
    desc="クビアカツヤカミキリに関する外来生物法などの法律と、国・神奈川県・川崎市の役割、2026 年秋の国の動き。",
    body="""<h1>法律と国・県・市の仕組み</h1>
<p class="page-meta">{asof} 時点</p>
<p class="intro">生きたまま「飼う・運ぶ・放す・人にあげる」のは、悪気がなくても法律違反です。防除をするのは木の持ち主・管理者で、二ヶ領用水の桜なら川崎市です。</p>
<h2>外来生物法（特定外来生物）</h2>
<ul>
<li><strong>2018-01-15 に指定</strong>されました。[[funabashi]] [[env_info]]</li>
<li><strong>禁止されること</strong>: 生きたまま、飼う・しまっておく・運ぶ・輸入する・人にあげる/売る・野外に放す。虫かごで飼うのも違反です。[[env_info]] [[kawa_0701]]</li>
<li><strong>見つけたら</strong>: 写真を撮り、その場で踏みつぶすなどして殺し、市に知らせます。捕まえて役所に持っていくのは「運ぶ」に当たるおそれがあるので、写真で知らせるのが安全です。[[kawa_page]]</li>
<li><strong>伐った被害木を運ぶとき</strong>: 幼虫が木の中にいる時期に、処分のために運ぶことなどについて、環境省の通知・告示で扱いが決められています。ボランティアが小さな規模で行う場合も、事前の公表などの要件があります。[[osaka]]</li>
</ul>
<div class="table-wrap"><table>
<thead><tr><th>してしまったこと</th><th>個人</th><th>法人</th></tr></thead>
<tbody>
<tr><td>許可なく飼う（ペット・観察の目的）</td><td>1 年以下の拘禁刑 または 100 万円以下の罰金</td><td>5,000 万円以下の罰金</td></tr>
<tr><td>許可なく飼う（売る・配る目的）、許可のない人に売る・配る</td><td>3 年以下の拘禁刑 または 300 万円以下の罰金</td><td>1 億円以下の罰金</td></tr>
<tr><td>許可なく野外に放す・輸入する</td><td>3 年以下の拘禁刑 または 300 万円以下の罰金</td><td>1 億円以下の罰金</td></tr>
</tbody></table></div>
<p>2025-06-01 から「懲役」は「拘禁刑」に名前が変わりました。[[lawtrans]] [[env_bassoku]]</p>
<h2>ほかの法律</h2>
<ul>
<li><strong>外来生物法の改正（2023-04）</strong>: 都道府県には対策をとる責務、市町村には同じことに努める責務、国には自治体を支える責務ができました。[[env_yobihi]]</li>
<li><strong>植物防疫法</strong>: 2023-04 に「指定有害動植物」になりました（主に農地のウメ・モモなどに関わります）。[[senryaku]]</li>
<li><strong>農薬取締法</strong>: 登録どおりに使います。他人の木・公共の木に、許可なく薬を入れてはいけません。[[osaka]]</li>
<li><strong>私有地の木</strong>: 防除は持ち主がするのが基本です。持ち主が対応できない・分からないときは、国・自治体が手続を経て防除できます。[[senryaku]]</li>
</ul>
<h2>国・県・市の役割</h2>
<div class="layer"><b>国（クビアカツヤカミキリ対策本部。本部長は農林水産大臣・環境大臣）</b><p>防除戦略を決める（2026-09-11）。2030 年度をめどに、被害地域を小さくしていく道筋をつける。環境省は外来生物法と交付金、農林水産省は植物防疫法と果樹の支援を受け持つ。国が管理する施設では率先して防除する [[env_honbu]] [[senryaku]] [[env_matters]]</p>
<div class="layer"><b>神奈川県（環境農政局 緑政部 自然環境保全課 045-210-4310）</b><p>県の「地域防除戦略」をつくる役（{asof} 時点で公表されていない）。確認情報の一覧を公表 [[kanagawa]] [[senryaku]]</p>
<div class="layer"><b>川崎市（環境局 総務部 企画課 044-200-3720）</b><p>住民からの発見情報を最初に受けて確かめる役。公園・河川などの木は、それぞれの管理者として防除する [[kawa_page]] [[senryaku]]</p>
<div class="layer"><b>市民</b><p>見回り・写真で通報・成虫をその場でつぶす。木を傷つける作業・薬は管理者に任せる</p></div>
</div></div></div>
<h3 id="zoning">ゾーニング（市町村ごとの区分）</h3>
<p>国の防除戦略は、市町村を 4 つに分けて、それぞれに合った対策をとるとしています。[[senryaku]]</p>
<div class="table-wrap"><table>
<thead><tr><th>区分</th><th>考え方</th></tr></thead>
<tbody>
<tr><td>未被害地域</td><td>まだ確認されていない。見張りを続ける</td></tr>
<tr><td><strong>飛び地的被害地域</strong></td><td>すでに被害がある地域に接していないのに、新しく確認された。<strong>最優先</strong>で、伐倒・伐根を徹底し、短い期間で地域から根絶する</td></tr>
<tr><td>被害最前線地域</td><td>被害が広がっている地域の外側。広がりを食い止める</td></tr>
<tr><td>まん延地域</td><td>被害が広がっている。被害を減らしながら守る</td></tr>
</tbody></table></div>
<p>川崎市がどの区分になるかは、神奈川県の地域防除戦略が出るまで決まりません。2026 年に初めて確認されたことから、「飛び地的被害地域」に近いと見られます。[[est]]</p>
<h2>場所ごとに「だれが防除するか」</h2>
<div class="table-wrap"><table>
<thead><tr><th>場所</th><th>防除をする人（管理者）</th></tr></thead>
<tbody>
<tr><td>二ヶ領用水（円筒分水から下流・宿河原線・上河原線）</td><td>川崎市（建設緑政局 道路河川整備部 河川課 044-200-2903）[[kawa_kihon]] [[kawa_iji]]</td></tr>
<tr><td>二ヶ領本川（県管理区間）</td><td>工事と維持は県と市の協定で市が行う。樹木の管理者は<span class="tbc">要確認</span> [[kawa_honsen]]</td></tr>
<tr><td>市の公園・緑地</td><td>川崎市（建設緑政局 緑政部 みどりの保全整備課 044-200-0349）[[kawa_0701]]</td></tr>
<tr><td>街路樹・学校</td><td>道路の管理者・学校の設置者 [[est]]</td></tr>
<tr><td>私有地（庭・マンション・社寺）</td><td>持ち主 [[senryaku]]</td></tr>
</tbody></table></div>
<p>どこの木でも、市民が知らせる先は <strong>川崎市 環境局 総務部 企画課</strong>（フォーム・メール・電話）で大丈夫です。施設の管理者に知らせてもよいとされています。[[kawa_page]]</p>
<h2 id="money">お金の仕組み</h2>
<div class="stats">
<div class="stat"><div class="stat-label">予備費（環境省分、2026-10-06 閣議決定）</div><div class="stat-value">27.04<span class="stat-unit">億円</span></div><div class="stat-sub">農林水産省分と合わせて約 32 億円 [[env_yobihi]] [[nikkei]]</div></div>
<div class="stat"><div class="stat-label">自治体の防除事業への交付率</div><div class="stat-value">1/2<span class="stat-unit">以内</span></div><div class="stat-sub">早期防除計画は定額 250 万円、地域防除戦略は定額 500 万円 [[env_jigyo]]</div></div>
<div class="stat"><div class="stat-label">交付金の追加公募</div><div class="stat-value">11/6<span class="stat-unit">まで</span></div><div class="stat-sub">2026-10-06〜11-06 [[env_koubo]]</div></div>
</div>
<ul>
<li>交付金を受けない、自治体だけの事業には、特別交付税の措置があります。[[env_info]]</li>
<li>2027 年度の予算要求で、環境省は外来種対策に 67 億円、そのうち自治体のクビアカツヤカミキリ対策に約 50 億円を求める案と報じられています。[[sakigake]]</li>
</ul>
<h2>2026 年の主な動き</h2>
<ol class="timeline" aria-label="2026 年の主な動き">
<li class="done"><time>2026-06</time><b>川崎市宮前区・横浜市青葉区・小田原市で確認</b><p>[[kanagawa]]</p></li>
<li class="done"><time>2026-07-31</time><b>国のクビアカツヤカミキリ対策本部ができる（第 1 回）</b><p>[[env_honbu]]</p></li>
<li class="done"><time>2026-09-11</time><b>国の防除戦略を決定（第 2 回）</b><p>[[senryaku]]</p></li>
<li class="done"><time>2026-09-17</time><b>松田町が、成虫 1 匹につき 1,000 円の報奨金を始める（〜10-30、県内初）</b><p>[[townnews_matsuda]]</p></li>
<li class="done"><time>2026-10-06</time><b>予備費の使用を閣議決定。交付金の追加公募が始まる</b><p>[[env_yobihi]] [[env_koubo]]</p></li>
<li class="done"><time>2026-10-07</time><b>防除戦略の関東ブロック説明会</b><p>[[maff_honbu]]</p></li>
<li class="done"><time>2026-10-09</time><b>小田原市曽我でウメを試行伐採（幹の中から幼虫 2 匹）</b><p>[[townnews_odawara]]</p></li>
<li class="done"><time>2026-10-13</time><b>環境省の情報収集システム「クビアカ発見・通報ネット（仮称）」の試行が始まる（〜11-30）</b><p>[[env_net]]</p></li>
<li class="done"><time>2026-10-15</time><b>第 3 回対策本部。国の施設で率先して防除し、自治体を技術とお金で支えると申し合わせ</b><p>[[env_matters]]</p></li>
<li class="now"><span class="badge">今</span><time>{asof}</time></li>
<li class="key"><span class="badge">締切</span><time>2026-11-06</time><b>交付金の追加公募の締切</b><p>[[env_koubo]]</p></li>
<li><time>2027-04（予定）</time><b>通報ネットの本格運用</b><p>[[env_net]]</p></li>
<li><time>2030 年度（目標）</time><b>被害地域を小さくしていく道筋をつける</b><p>[[senryaku]]</p></li>
</ol>
""".replace("{asof}", ASOF)))

# ---------------- 見つけたら ----------------
pages.append(dict(path=K + "found.html", title="見つけたら（できること・できないこと）", section="sakura", theme="theme-sakura",
    crumbs=KCRUMB2, pager=kpager(5),
    desc="クビアカツヤカミキリを見つけたときの手順と通報先、市民・子どもができること・してはいけないこと。",
    body="""<h1>見つけたら（できること・できないこと）</h1>
<p class="page-meta">{asof} 時点。連絡先は、必ず川崎市の公式ページで確かめてください [[kawa_page]]</p>
<p class="intro">市民がするのは「見る・撮る・記録する・知らせる」までです。木を傷つけること、薬、高い所の作業、生きた虫を運ぶことはしません。</p>
<h2>見つけたときの手順</h2>
<ol class="steps">
<li><b>写真を撮る</b>成虫、根元のフラス（近く）、木の全体、場所の分かる目印（公園名・施設名の看板など）。人・車のナンバー・表札は写さない。</li>
<li><b>成虫はその場でつぶす</b>生きたまま持ち帰る・飼う・運ぶのは外来生物法で禁止されています。[[kawa_0701]] 子どもは素手で触らず、大人に任せます。</li>
<li><b>日時と場所を記録する</b>公園・通り・用水の区間の名前など。</li>
<li><b>川崎市に知らせる</b>下の窓口へ。迷ったら「疑い」として知らせれば十分です。</li>
</ol>
<div class="box key">
<h3>川崎市の窓口（環境局 総務部 企画課）</h3>
<ul>
<li>WEB: <a href="https://logoform.jp/f/uCGbM" target="_blank" rel="noopener noreferrer">クビアカツヤカミキリ・フラス発見報告フォーム</a> [[kawa_form]]</li>
<li>メール: 30kikaku@city.kawasaki.jp [[kawa_page]]</li>
<li>電話: 044-200-3720（平日 8:30〜17:00）[[kawa_page]] [[kawa_0714]]</li>
<li>見つけた場所の施設の管理者に知らせてもよいとされています。[[kawa_page]]</li>
</ul>
<p>農地（ウメ・モモなど）で見つけたときは、神奈川県の農業技術センターにも相談できます。県全体の窓口は、環境農政局 緑政部 自然環境保全課（045-210-4310）です。[[kanagawa]]</p>
</div>
<h2>できること・してはいけないこと</h2>
<div class="table-wrap"><table>
<thead><tr><th>やってよいこと</th><th>やってはいけないこと（理由）</th></tr></thead>
<tbody>
<tr><td class="ok">公共の場所で、根元から目の高さまでを見て、フラスや成虫の写真を撮る</td><td class="ng"><strong>生きた成虫・幼虫を持ち帰る・飼う・運ぶ・放す</strong>（外来生物法違反）[[kawa_0701]]</td></tr>
<tr><td class="ok">日時・場所・写真を記録して、市に知らせる</td><td class="ng"><strong>他人の木・公共の木に、勝手に薬を入れる・まく</strong>（持ち主の同意と、登録どおりの使い方が必要。用水に流れ込むおそれもある）[[osaka]]</td></tr>
<tr><td class="ok">見つけた成虫を、大人がその場でつぶす</td><td class="ng"><strong>ノミ・針金・ドリル・のこぎりで幹を削る・刺す</strong>（けがをする。木を傷つける。すべての木には管理者がいる）[[osaka]]</td></tr>
<tr><td class="ok">ネットが巻かれた木で成虫を見つけたら、管理者に伝える</td><td class="ng"><strong>脚立・木登り</strong>、弱った木の下に長くいること（落ちる。枝が落ちてくる）</td></tr>
<tr><td class="ok">「被害なし」も記録する</td><td class="ng">ネットを外す、ネットの中の成虫を逃がす・持ち帰る [[osaka]]</td></tr>
<tr><td></td><td class="ng">伐った木・枝を持ち帰る（中に幼虫がいることがある）</td></tr>
<tr><td></td><td class="ng">私有地・立入禁止の場所に入る</td></tr>
</tbody></table></div>
<h2>子どもと見回るときは</h2>
<ul>
<li>大人が付き添い、2 人以上で動きます。用水の水辺側と車道側の転落、夏の熱中症に気をつけます。</li>
<li>成虫は素手で触らず、持ち帰りません。死んだ虫を標本にして持ち運んでよいかは、確かめられていないので、勧めません。</li>
<li>写すのは幹とフラスだけにします。SNS などに載せるときは、写真の位置情報を消し、人の顔・名前を出さないようにします。</li>
<li>学校・子ども会などの活動で行うときは、保護者の同意を得てください。</li>
</ul>
<h2>ほかの通報の仕組み</h2>
<p>環境省は「クビアカ発見・通報ネット（仮称）」を試行しています（2026-10-13〜11-30、2027-04 に本格運用の予定）。[[env_net]] 川崎市の窓口との関係（どちらに出せばよいか）は、{asof} 時点で確かめられていません。<span class="tbc">要確認</span> このサイトでは、まず川崎市の窓口に知らせることを勧めます。</p>
""".replace("{asof}", ASOF)))

# ---------------- みんなでできること ----------------
pages.append(dict(path="action/index.html", title="みんなでできること", section="action", theme="theme-leaf",
    crumbs=[("index.html", "ホーム")],
    desc="二ヶ領用水の桜並木の見回り・記録・通報を、地域で続けるための考え方と、まだ分かっていないこと。",
    body="""<h1>みんなでできること</h1>
<p class="page-meta">準備中のページです（{asof} 時点）</p>
<p class="intro">桜並木を守るには、早く見つけて、確実に市に届けることがいちばん大切です。散歩のついでの見回りでも力になります。地域の人と無理なく続けられる仕組みを、これから作っていきます。</p>
<h2>見回りの考え方</h2>
<ul>
<li><strong>時期</strong>: 4〜8 月、とくにお盆過ぎ（8 月下旬）。[[ffpri4]] → <a href="@/sakura/kubiaka/identify.html#calendar">見回りカレンダー</a></li>
<li><strong>見るところ</strong>: 桜の根元を一周、目の高さまで。</li>
<li><strong>記録すること</strong>: 日付、区、場所（公園・施設・用水の区間の名前）、木の目印、症状（フラス・成虫・穴・枝枯れ）、写真の有無、通報した日、市の返事。「被害なし」も記録します。</li>
<li><strong>グループで見回るとき</strong>: 見つけた人は写真を仲間に送り、市への通報は担当の 1 人がまとめて行うと、同じ木を何度も通報せずに済みます。</li>
</ul>
<h2>記録を公開するときの決まり</h2>
<div class="box note">
<ul>
<li>公開するのは、<strong>公共の場所（公園・緑地・街路・河川沿い）の木</strong>の記録だけです。場所は区と施設名の単位までにします。</li>
<li>私有地の木の位置、個人の名前・連絡先、人の顔・車のナンバー・表札が写った写真は公開しません。写真の位置情報（EXIF）は消します。</li>
<li>市・県のページの文章や地図の画像はそのまま転載せず、リンクで示します。[[kawa_policy]] 確認された市町村などの事実は、出典と時点を添えて書きます。</li>
<li>「確認」と「疑い」を分け、いつの情報かを必ず書きます。</li>
</ul>
</div>
<h2>ほかの地域の例</h2>
<ul>
<li>埼玉県は、スマホの投稿フォームと公開地図で、県民から発見情報を集めています。「被害がない」という報告も受け付けています。[[saitama_survey]]</li>
<li>群馬県の「ぐんまクビアカネット」は、成虫・フラス・穴の発見情報を投稿し、地図で見られるようにしています。[[gunma_net]]</li>
<li>横浜市は、見つかった公園のまわりの公園・街路樹・川を調べ、その結果を公表しました。[[yokohama]]</li>
</ul>
<h2>まだ分かっていないこと</h2>
<p>このサイトで公開資料を調べても分からなかったことです。分かりしだい、このサイトに反映します。</p>
<ul>
<li>菅生緑地の被害木のその後と、周りの調査の結果</li>
<li>二ヶ領用水沿いの桜 1 本ずつの管理者（川の土地・緑道・道路のどれか）と、点検・見回りの計画</li>
<li>市民の見回りと市との協働の形（たとえば川崎市の河川愛護ボランティア制度で、桜の見回りを活動に含められるか）<span class="tbc">要確認</span></li>
<li>国の通報ネットと川崎市の窓口の関係</li>
<li>神奈川県の地域防除戦略と、川崎市の区分</li>
<li>川崎市に、私有の木の防除への補助があるか</li>
</ul>
<h2>用水の清掃に参加する</h2>
<p>一斉清掃・河川愛護ボランティア制度・ゴミの記録のしかたは、「<a href="@/water/litter.html#join">用水のゴミ問題</a>」にまとめています。</p>
<h2>これからやること</h2>
<ul>
<li>見回りの記録のしかた（記録の項目・写真の撮り方）をまとめる</li>
<li>二ヶ領用水の水と生きもののページをつくる</li>
<li>地域の人と一緒に続けられる見回り・観察の場をつくる</li>
</ul>
""".replace("{asof}", ASOF)))

# ---------------- このサイトについて ----------------
pages.append(dict(path="about.html", title="このサイトについて", section="about",
    crumbs=[("index.html", "ホーム")],
    desc="このサイトの目的、情報の扱い方、出典の示し方、ライセンス。",
    body="""<h1>このサイトについて</h1>
<p class="intro">「武蔵小杉の二ヶ領用水にもオイカワを」は、神奈川県川崎市の二ヶ領用水をきれいにし、そこに暮らす生きものと水辺の自然、用水沿いの桜並木を守るための、市民による非公式のプロジェクトです。川崎市・神奈川県などの公式のサイトではありません。</p>
<h2>情報の扱い方</h2>
<ul>
<li>国・自治体・研究機関の公開資料を、まず確かめてから書いています。それぞれの記述に出典を付け、取得した日を示しています。</li>
<li>情報は、各ページに書いた時点のものです。制度・連絡先・確認状況は変わることがあるので、使う前に元のページで確かめてください。</li>
<li>公開資料で確かめられなかったことは「要確認」、公開資料からの推定は「推定」と書き、事実と分けています。</li>
<li>公式の資料の PDF・画像は転載せず、リンクで示しています。</li>
</ul>
<h2>出典の印</h2>
<div class="table-wrap"><table>
<thead><tr><th>印</th><th>意味</th></tr></thead>
<tbody>
<tr><td><span class="src official">公式</span></td><td>国・自治体・研究機関などのページ</td></tr>
<tr><td><span class="src web">Web</span></td><td>報道など、公式以外のページ</td></tr>
<tr><td><span class="src est">推定</span></td><td>公開資料からの推定。確かめられていないこと</td></tr>
<tr><td><span class="tbc">要確認</span></td><td>公開資料では確かめられず、関係機関に確かめる必要があること</td></tr>
</tbody></table></div>
<h2>個人の情報について</h2>
<p>このサイトには、私有地の木の位置、個人の名前・連絡先、人の顔などが分かる写真を載せません。場所は、公共の場所の名前と区の単位までにしています。</p>
<h2>間違いを見つけたら</h2>
<p>内容の誤りや古くなった情報は、<a href="https://github.com/otajisan/nikaryo-oikawa/issues" target="_blank" rel="noopener noreferrer">GitHub の Issue</a> でお知らせください。</p>
<h2>ライセンス</h2>
<ul>
<li>このサイトの文章: <a href="https://github.com/otajisan/nikaryo-oikawa/blob/main/LICENSE-docs" target="_blank" rel="noopener noreferrer">CC BY 4.0</a>（出典の表示をすれば、自由に使えます）</li>
<li>サイトのコード: <a href="https://github.com/otajisan/nikaryo-oikawa/blob/main/LICENSE" target="_blank" rel="noopener noreferrer">MIT License</a></li>
<li>引用した公式資料の権利は、それぞれの発行元にあります。</li>
</ul>
"""))

# ---------------- 404 ----------------
pages.append(dict(path="404.html", title="ページが見つかりません", section="", crumbs=None,
    desc="ページが見つかりません。",
    body="""<h1>ページが見つかりません</h1>
<p>お探しのページは、移動したか、まだありません。<a href="@/index.html">ホーム</a>から探してください。</p>
"""))

for p in pages:
    page(**p)
left = []
for root, _, files in os.walk(OUT):
    for name in files:
        if name.endswith(".html"):
            text = open(os.path.join(root, name), encoding="utf-8").read()
            if re.search(r"\{asof\}|\[\[[a-z0-9_]+\]\]|href=\"@/", text):
                left.append(name)
if left:
    sys.exit(f"置換されずに残ったトークンがあります: {left}")
print("pages:", len(pages))
