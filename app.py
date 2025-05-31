import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re

# 유튜브 URL에서 video_id 추출 함수
def extract_video_id(url):
    video_id = None
    if 'youtube.com' in url:
        video_id = re.search(r'v=([^&]+)', url)
        if video_id:
            return video_id.group(1)
    elif 'youtu.be' in url:
        video_id = re.search(r'youtu.be/([^?]+)', url)
        if video_id:
            return video_id.group(1)
    return None

# 자막 언어 리스트 가져오기
def get_available_languages(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        return [
            (t.language_code, t.language, t.is_generated, t)
            for t in transcript_list
        ]
    except Exception as e:
        return f"자막 언어를 가져오는 중 오류가 발생했습니다: {str(e)}"

# 실제 자막 추출 함수
def get_subtitles(video_id, language_code):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])
        formatter = TextFormatter()
        return formatter.format_transcript(transcript), None
    except Exception as e:
        return None, f"자막을 가져오는 중 오류가 발생했습니다: {str(e)}"

# Streamlit 페이지 설정
st.set_page_config(
    page_title="YouTube 자막 추출기",
    page_icon="🎥",
    layout="wide"
)

# 안내 메시지
st.info(
    "⚠️ 일부 자동 생성 자막은 유튜브 정책에 따라 추출이 불가능할 수 있습니다. "
    "웹에서 자막이 보이더라도, 프로그램에서는 추출이 안 될 수 있습니다. "
    "자막이 꼭 필요한 경우, 여러 영상으로 시도해보세요."
)

st.title("🎥 YouTube 자막 추출기")
st.write("YouTube 동영상 URL을 입력하면 자막을 추출해드립니다.")

# URL 입력
url = st.text_input("YouTube URL을 입력하세요:")

if 'languages' not in st.session_state:
    st.session_state['languages'] = []
if 'video_id' not in st.session_state:
    st.session_state['video_id'] = None
if 'lang_error' not in st.session_state:
    st.session_state['lang_error'] = ''

if st.button("확인"):
    st.session_state['languages'] = []
    st.session_state['video_id'] = None
    st.session_state['lang_error'] = ''
    if url:
        video_id = extract_video_id(url)
        if video_id:
            langs = get_available_languages(video_id)
            if isinstance(langs, str):
                st.session_state['lang_error'] = langs
            elif langs:
                st.session_state['languages'] = langs
                st.session_state['video_id'] = video_id
            else:
                st.session_state['lang_error'] = "이 동영상에서 사용 가능한 자막을 찾을 수 없습니다."
        else:
            st.session_state['lang_error'] = "올바른 YouTube URL을 입력해주세요."
    else:
        st.session_state['lang_error'] = "YouTube URL을 입력해주세요."

languages = st.session_state.get('languages', [])
video_id = st.session_state.get('video_id', None)
lang_error = st.session_state.get('lang_error', '')

if lang_error:
    if 'Subtitles are disabled' in lang_error or "사용 가능한 자막을 찾을 수 없습니다" in lang_error:
        st.error('이 영상에는 자막이 제공되지 않습니다. (유튜브 정책 또는 영상 설정에 따라 추출이 불가능할 수 있습니다.)')
    else:
        st.error(lang_error)

if languages:
    st.markdown("---")
    language_options = {f"{lang[1]} ({'자동 생성' if lang[2] else '수동'}) [{lang[0]}]": lang[0] for lang in languages}
    selected_language = st.selectbox(
        "자막 언어를 선택하세요:",
        options=list(language_options.keys())
    )
    if st.button("자막 추출"):
        with st.spinner("자막을 추출하는 중..."):
            subtitles, err = get_subtitles(video_id, language_options[selected_language])
            if subtitles:
                st.text_area("추출된 자막:", subtitles, height=400)
                st.download_button(
                    label="자막 다운로드",
                    data=subtitles,
                    file_name=f"subtitles_{video_id}_{language_options[selected_language]}.txt",
                    mime="text/plain"
                )
            else:
                if err and 'no element found' in err:
                    st.error("이 영상의 자동 생성 자막은 유튜브 정책상 추출이 불가능합니다. 다른 영상으로 시도해보세요.")
                else:
                    st.error(err or "해당 언어로 자막을 추출할 수 없습니다.")
else:
    st.info("URL을 입력하고 '확인' 버튼을 눌러 자막 언어를 확인하세요.")

st.markdown("---")
st.info("앱이 멈췄거나 절전 모드였다면 새로고침 해보세요.")
if st.button("앱 새로고침"):
    st.rerun()
