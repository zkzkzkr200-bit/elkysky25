import streamlit as st
import replicate
import random
import io
import requests
import time

# --- 페이지 설정 ---
st.set_page_config(
    page_title="K-Web Pro Final",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 스타일 (다크모드 & 모바일 최적화) ---
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        padding: 20px;
        font-weight: bold;
        font-size: 20px;
        border-radius: 12px;
        background: linear-gradient(90deg, #FF4B4B 0%, #FF914D 100%);
        color: white;
        border: none;
    }
    .stSelectbox, .stTextInput, .stRadio {
        font-size: 1.1em;
    }
    div[data-baseweb="input"] {
        border-color: #FF4B4B !important;
    }
    label[data-baseweb="checkbox"] {
        font-weight: bold;
        color: #FF4B4B;
    }
</style>
""", unsafe_allow_html=True)

# --- 유틸리티 함수 ---
def extract_eng(text):
    if "(" in text and ")" in text:
        return text.split("(")[1].split(")")[0]
    return text

# --- 세션 관리 ---
if 'seed_value' not in st.session_state:
    st.session_state.seed_value = random.randint(0, 999999)

# ===========================
# 1. 사이드바: 설정 및 시드
# ===========================
with st.sidebar:
    st.title("⚙️ 스튜디오 설정")
    
    if "REPLICATE_API_TOKEN" in st.secrets:
        st.success("API 연결됨 (Replicate) ✅")
    else:
        st.error("API 키가 없습니다! 🚨")
        st.stop()
        
    st.divider()
    
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("New"):
            st.session_state.seed_value = random.randint(0, 999999)
            st.rerun()
    with col2:
        st.number_input("Seed 번호", value=st.session_state.seed_value, disabled=True)
    
    st.caption("고유 번호가 같으면 같은 캐릭터가 나옵니다.")

# ===========================
# 2. 메인 화면
# ===========================
st.title("👑 K-Web Pro Final")
st.caption("Dual Engine (실사 & 2D 전문 모델 자동 전환)")

col_left, col_right = st.columns([1, 1])

# [변수 초기화] - NameError 방지
final_style_keywords = "" 
nsfw_keywords = ""
final_view_angle = ""
final_gender = ""
final_hair = ""
final_body = ""
final_pose = ""
final_outfit = ""
custom_face = ""
is_anime_mode = False 

with col_left:
    st.subheader("1️⃣ 스타일 & 캐릭터")
    
    with st.container(border=True):
        st.markdown("#### 🎨 화풍 (Art Style)")
        
        art_category = st.radio("장르 선택", 
            ["📸 실사 (Photorealistic)", "🖌️ 2D/일러스트 (Anime)"], 
            horizontal=True
        )
        
        is_nsfw = st.checkbox("🔞 19금 모드 적용 (Enable NSFW)", value=False)
        
        # 2D/실사 모드에 따른 키워드 최적화
        if "2D" in art_category:
            is_anime_mode = True
            style_detail = st.
