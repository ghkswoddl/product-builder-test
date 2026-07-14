결제 플로우 설계 (간단 가이드)

목표: 플랜별 결제(구독/일회성)를 안전하게 처리하고, 결제 성공 시 사용자에게 주문 확인 및 스타일 서비스 일정을 연결합니다.

1) 흐름 요약
- 클라이언트: 사용자가 "결제하기" 클릭 -> 백엔드 결제 세션 생성 요청 -> 백엔드에서 결제 게이트웨이(예: Stripe, Toss, KakaoPay 등) API 호출하여 결제 세션/결제 URL 생성 -> 클라이언트 리디렉션(또는 결제 위젯 오픈)
- 결제 완료: 결제 게이트웨이는 webhook으로 백엔드에 결제 완료 이벤트 전송 -> 백엔드에서 결제 상태 검증 후 서비스(컨설팅) 예약/리포트 생성 및 사용자에게 알림(이메일/SMS)

2) 엔드포인트 예시 (백엔드 필요)
- POST /api/checkout/create
  - 바디: { planId: 'pro' | 'premium' | 'starter', user: {name,email}, returnUrl }
  - 응답: { checkoutUrl }
- POST /webhook/payment
  - 결제 게이트웨이의 webhook을 받는 엔드포인트 (서명 검증 필요)

3) 데이터 모델(간단)
- Order: id, userEmail, planId, amount, currency, status(pending/paid/canceled), createdAt
- Subscription(구독 플랜인 경우): id, userEmail, planId, status, nextBillingAt

4) 보안/운영 고려사항
- 결제 webhook은 게이트웨이 서명으로 검증
- 결제 금액/통화는 서버에서 계산하여 클라이언트 입력을 신뢰하지 않음
- 개인 데이터(이메일 등)는 암호화 저장 및 접근 제어

5) 구현 참고
- Stripe Checkout: 서버에서 Checkout Session 생성 후 클라이언트에 URL 반환
- TossPayments/KakaoPay: 국가·결제 수단 고려하여 SDK 문서 참조

6) 프론트엔드 간단 예시
- 결제 버튼 클릭 -> fetch('/api/checkout/create', {method:'POST', body:{planId}}) -> 응답.checkoutUrl 로 location.href 이동

원하시면 해당 리포지토리에 간단한 서버 예제(Express + Stripe) 스캐폴딩을 생성해 드리겠습니다.
