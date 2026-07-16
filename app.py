from flask import Flask, render_template, request, jsonify
import urllib.request
import urllib.parse
import json
import re

# [방법 1 적용] template_folder='.'을 추가하여 templates 폴더 없이 
# 루트 디렉토리에 있는 index.html을 바로 찾을 수 있도록 설정합니다.
app = Flask(__name__, template_folder='.')

# ------------------------------------------------------------------
# 아이돌 실제 사진 조회 (저작권 안전 버전)
#
# 인스타그램/구글 이미지 검색 결과를 그대로 긁어와 우리 서비스에 올리면
# 저작권/초상권 문제가 생길 수 있습니다. 대신 위키미디어 커먼즈
# (Wikimedia Commons)를 사용합니다. 커먼즈는 정책상 "재사용이 허용된
# 자유 라이선스(퍼블릭 도메인, CC-BY, CC-BY-SA 등)" 사진만 올릴 수 있는
# 곳이라, 여기서 찾은 사진은 출처(저작자)만 표기하면 우리 서비스에
# 그대로 가져와 보여줘도 안전합니다.
# ------------------------------------------------------------------

COMMONS_API = 'https://commons.wikimedia.org/w/api.php'


def _fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'StyleMatchApp/1.0 (idol OOTD demo; contact: dev@yourdomain.com)'})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _strip_html(value):
    if not value:
        return ''
    return re.sub('<[^<]+?>', '', value).strip()


def find_commons_photo(name):
    """이름으로 커먼즈에서 자유 라이선스 사진을 검색해 1건 반환합니다.
    못 찾으면 None을 반환하고, 프론트엔드는 기존 스톡 이미지로 대체합니다."""
    name = (name or '').strip()
    if not name:
        return None

    try:
        # 1) 파일(namespace 6) 검색
        search_url = COMMONS_API + '?' + urllib.parse.urlencode({
            'action': 'query', 'list': 'search', 'srsearch': name,
            'srnamespace': 6, 'format': 'json', 'srlimit': 5
        })
        search_data = _fetch_json(search_url)
        results = search_data.get('query', {}).get('search', [])
        if not results:
            return None
        title = results[0]['title']

        # 2) 해당 파일의 URL + 라이선스/저작자 메타데이터 조회
        info_url = COMMONS_API + '?' + urllib.parse.urlencode({
            'action': 'query', 'titles': title, 'prop': 'imageinfo',
            'iiprop': 'url|extmetadata', 'iiurlwidth': 700, 'format': 'json'
        })
        info_data = _fetch_json(info_url)
        pages = info_data.get('query', {}).get('pages', {})
        page = next(iter(pages.values()), None)
        if not page or 'imageinfo' not in page:
            return None
        info = page['imageinfo'][0]
        meta = info.get('extmetadata', {})

        license_short = meta.get('LicenseShortName', {}).get('value', '')
        # 비자유 라이선스(예: 위키백과 전용 fair-use)는 재사용하지 않고 걸러냅니다.
        if not license_short or 'non-free' in license_short.lower():
            return None

        return {
            'found': True,
            'imageUrl': info.get('thumburl') or info.get('url'),
            'sourceUrl': 'https://commons.wikimedia.org/wiki/' + urllib.parse.quote(title.replace(' ', '_')),
            'license': license_short,
            'artist': _strip_html(meta.get('Artist', {}).get('value', '')),
        }
    except Exception:
        # 네트워크 오류 등 어떤 이유로든 실패하면 그냥 "못 찾음" 처리합니다.
        return None


@app.route('/api/idol-photo')
def idol_photo():
    name = request.args.get('name', '')
    result = find_commons_photo(name)
    if not result:
        return jsonify({'found': False})
    return jsonify(result)


@app.route('/')
def index():
    # 1. 인스타그램 공식 공유하기 -> '임베드 코드 복사'로 얻은 실제 코드 예시
    # ※ 주의: 보안 정책상 원본 인스타그램 주소 뒤에 /embed/를 붙인 iframe 형식이 안전하게 로드됩니다.
    sample_embed_code = """
    <iframe src="https://instagram.com" 
            width="100%" height="480" frameborder="0" scrolling="no" allowtransparency="true">
    </iframe>
    """
    
    # 2. 템플릿에 전달할 가상 가성비 매칭 데이터 (DB에서 조회해올 데이터 구조)
    matching_items = [
        {
            "category": "Outer",
            "brand": "MUSINSA STANDARD",
            "name": "오버사이즈 비건 레더 자켓 Black",
            "price": "79,900원",
            "image": "https://unsplash.com", # 예시 상품 이미지
            "shop_link": "https://musinsa.com"
        },
        {
            "category": "Pants",
            "brand": "TOFFEE",
            "name": "와이드 생지 데님 팬츠 딥블루",
            "price": "45,000원",
            "image": "https://unsplash.com",
            "shop_link": "https://musinsa.com"
        }
    ]
    
    # 루트에 있는 index.html을 로드하면서 데이터를 전달합니다.
    return render_template('index.html', 
                           idol_name="카리나", 
                           group_name="에스파", 
                           embed_code=sample_embed_code, 
                           products=matching_items)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)