from flask import Flask, render_template

# [방법 1 적용] template_folder='.'을 추가하여 templates 폴더 없이 
# 루트 디렉토리에 있는 index.html을 바로 찾을 수 있도록 설정합니다.
app = Flask(__name__, template_folder='.')

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
