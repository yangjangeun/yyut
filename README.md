# YouTube 자막 추출기

YouTube 동영상의 자막을 추출할 수 있는 웹 애플리케이션입니다.

## 기능

- YouTube 동영상 URL 입력
- 사용 가능한 자막 언어 목록 표시
- 선택한 언어의 자막 추출
- 추출된 자막 텍스트 파일 다운로드

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 애플리케이션 실행:
```bash
streamlit run app.py
```

## 사용 방법

1. 웹 브라우저에서 애플리케이션 열기
2. YouTube 동영상 URL 입력
3. 사용 가능한 자막 언어 중 선택
4. "자막 추출" 버튼 클릭
5. 추출된 자막 확인 및 다운로드

## 지원하는 URL 형식

- https://www.youtube.com/watch?v=VIDEO_ID
- https://youtu.be/VIDEO_ID 