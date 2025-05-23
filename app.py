import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re

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

def get_available_languages(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        return [
            (t.language_code, t.language, t.is_generated, t)
            for t in transcript_list if t.is_translatable or t.is_generated or t.is_manually_created
        ]
    except Exception as e:
        return f"자막 언어를 가져오는 중 오류가 발생했습니다: {str(e)}"

def get_subtitles(video_id, language_code):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])
        formatter = TextFormatter()
        return formatter.format_transcript(transcript), None
    except Exception as e:
        return None, f"자막을 가져오는 중 오류가 발생했습니다: {str(e)}"

st.title("YouTube 자막 추출기")
st.write("YouTube 동영상 URL을 입력하면 자막을 추출해드립니다.")

col1, col2 = st.columns([5, 1])
with col1:
    url = st.text_input("YouTube URL을 입력하세요:", key="url_input")
with col2:
    fetch_lang = st.button("확 인", key="fetch_lang_btn")

if 'languages' not in st.session_state:
    st.session_state['languages'] = []
if 'video_id' not in st.session_state:
    st.session_state['video_id'] = None
if 'lang_error' not in st.session_state:
    st.session_state['lang_error'] = ''

if fetch_lang:
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
    if 'Subtitles are disabled' in lang_error:
        st.error('이 영상에는 자막이 제공되지 않습니다.')
    else:
        st.error(lang_error)

if languages:
    language_options = {f"{lang[1]} ({lang[0]})": lang[0] for lang in languages}
    selected_language = st.selectbox(
        "자막 언어를 선택하세요:",
        options=list(language_options.keys()),
        key="lang_select"
    )
    if st.button("자막 추출", key="extract_btn"):
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
                st.error(err or "해당 언어로 자막을 추출할 수 없습니다.")
else:
    st.info("URL을 입력하고 '언어 불러오기' 버튼을 눌러 자막 언어를 확인하세요.")
