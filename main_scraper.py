import requests
import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import mimetypes

def scrape_website_enhanced(url):
    """
    指定されたURLからHTMLとCSSを取得し、完全なウェブサイトを再現する（強化版）
    """
    print(f"強化版スクレイピングを開始: {url}")

    # 保存ディレクトリの作成
    site_name = urlparse(url).netloc.replace('.', '_')
    output_dir = f"scraped_website"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(f"{output_dir}/assets", exist_ok=True)
    os.makedirs(f"{output_dir}/css", exist_ok=True)
    os.makedirs(f"{output_dir}/js", exist_ok=True)
    os.makedirs(f"{output_dir}/images", exist_ok=True)

    try:
        # HTMLの取得
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding

        html_content = response.text
        print(f"HTML取得成功: {len(html_content)} 文字")

        # BeautifulSoupで解析
        soup = BeautifulSoup(html_content, 'html.parser')

        # インラインCSSを外部ファイルに抽出
        css_content = ""
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                css_content += style_tag.string + "\n"

        # CSSファイルを保存
        if css_content.strip():
            css_filename = "styles.css"
            with open(f"{output_dir}/css/{css_filename}", 'w', encoding='utf-8') as f:
                f.write(css_content)

            # 既存のstyleタグを削除してlinkタグに置換
            for style_tag in soup.find_all('style'):
                if style_tag.string and style_tag.string.strip():
                    style_tag.decompose()

            # CSSファイルへのリンクを追加
            new_link = soup.new_tag('link', rel='stylesheet', href=f'css/{css_filename}')
            if soup.head:
                soup.head.append(new_link)

        # CSSファイルの取得と保存（外部CSSファイル）
        css_files = []
        for link in soup.find_all('link', rel='stylesheet'):
            css_url = urljoin(url, link.get('href'))
            if css_url and not css_url.startswith('data:'):
                css_files.append(css_url)
                download_file(css_url, f"{output_dir}/css/", headers)
                # HTML内のCSSリンクを相対パスに変更
                link['href'] = f"css/{os.path.basename(urlparse(css_url).path)}"

        # JavaScriptファイルの取得と保存
        for script in soup.find_all('script', src=True):
            js_url = urljoin(url, script.get('src'))
            if js_url and not js_url.startswith('data:'):
                download_file(js_url, f"{output_dir}/js/", headers)
                # HTML内のJSリンクを相対パスに変更
                script['src'] = f"js/{os.path.basename(urlparse(js_url).path)}"

        # 画像ファイルの取得と保存
        images_downloaded = set()
        for img in soup.find_all('img', src=True):
            img_url = urljoin(url, img.get('src'))
            if img_url and not img_url.startswith('data:') and img_url not in images_downloaded:
                download_file(img_url, f"{output_dir}/images/", headers)
                images_downloaded.add(img_url)
                # HTML内の画像リンクを相対パスに変更
                img['src'] = f"images/{os.path.basename(urlparse(img_url).path)}"

        # 背景画像などのCSS内のURLを取得
        css_urls = re.findall(r'url\(["\']?([^"\']+)["\']?\)', css_content)
        for css_url in css_urls:
            full_url = urljoin(url, css_url)
            if full_url and not full_url.startswith('data:') and full_url not in images_downloaded:
                download_file(full_url, f"{output_dir}/images/", headers)
                images_downloaded.add(full_url)
                # CSS内のURLを相対パスに変更
                css_content = css_content.replace(css_url, f"../images/{os.path.basename(urlparse(full_url).path)}")

                # CSSファイルを更新
                with open(f"{output_dir}/css/{css_filename}", 'w', encoding='utf-8') as f:
                    f.write(css_content)

        # その他のアセットファイルの取得（favicon, etc.）
        for link in soup.find_all('link', href=True):
            if link.get('rel') and any(icon_type in str(link.get('rel')) for icon_type in ['icon', 'shortcut']):
                asset_url = urljoin(url, link.get('href'))
                if asset_url and not asset_url.startswith('data:'):
                    download_file(asset_url, f"{output_dir}/assets/", headers)
                    link['href'] = f"assets/{os.path.basename(urlparse(asset_url).path)}"

        # HTMLファイルの保存
        with open(f"{output_dir}/index.html", 'w', encoding='utf-8') as f:
            f.write(str(soup))

        # 取得したファイルの一覧を表示
        print(f"\n=== 取得したファイル一覧 ===")
        print(f"HTML: index.html")

        css_files_total = len(css_files) + (1 if css_content.strip() else 0)
        print(f"CSSファイル: {css_files_total}個")
        if css_content.strip():
            print(f"  - styles.css (インラインCSSから抽出)")
        for css_file in css_files:
            print(f"  - {os.path.basename(urlparse(css_file).path)}")

        js_files = [f for f in os.listdir(f"{output_dir}/js") if f.endswith('.js')]
        print(f"JavaScriptファイル: {len(js_files)}個")
        for js_file in js_files:
            print(f"  - {js_file}")

        image_files = []
        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp', '.ico']:
            image_files.extend([f for f in os.listdir(f"{output_dir}/images") if f.endswith(ext)])
        print(f"画像ファイル: {len(image_files)}個")
        for img_file in image_files:
            print(f"  - {img_file}")

        asset_files = []
        for ext in ['.ico', '.png', '.jpg', '.svg']:
            asset_files.extend([f for f in os.listdir(f"{output_dir}/assets") if f.endswith(ext)])
        if asset_files:
            print(f"アセットファイル: {len(asset_files)}個")
            for asset_file in asset_files:
                print(f"  - {asset_file}")

        print(f"\n=== 完了 ===")
        print(f"ファイルは '{output_dir}' ディレクトリに保存されました")
        print(f"ブラウザで '{output_dir}/index.html' を開いて確認してください")

        return output_dir

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

def download_file(url, save_dir, headers):
    """
    指定されたURLからファイルをダウンロードして保存する
    """
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # ファイル名の取得
        filename = os.path.basename(urlparse(url).path)
        if not filename:
            filename = "index.html"

        # 拡張子がない場合は追加を試行
        if '.' not in filename:
            content_type = response.headers.get('content-type', '')
            if 'css' in content_type:
                filename += '.css'
            elif 'javascript' in content_type or 'js' in content_type:
                filename += '.js'
            elif 'html' in content_type:
                filename += '.html'
            elif 'png' in content_type:
                filename += '.png'
            elif 'jpeg' in content_type or 'jpg' in content_type:
                filename += '.jpg'
            elif 'gif' in content_type:
                filename += '.gif'
            elif 'svg' in content_type:
                filename += '.svg'
            elif 'ico' in content_type:
                filename += '.ico'

        # ファイルの保存
        filepath = os.path.join(save_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)

        print(f"ダウンロード完了: {filename}")
        return filename

    except Exception as e:
        print(f"ダウンロードエラー ({url}): {e}")
        return None

if __name__ == "__main__":
    target_url = "https://sb-preview.squadbeyond.com/articles/zrJcXiSngBrbG-KirGCmg/preview"
    scrape_website_enhanced(target_url)
