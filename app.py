import streamlit as st
import replicate
import random
import io
import requests

# --- 페이지 설정 ---
st.set_page_config(
    page_title="K-Web Pro Ultimate",
    page_icon="🔥",
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
    /* 입력창 강조 */
    div[data-baseweb="input"] {
        border-color: #FF4B4B !important;
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
    
    # API 키 상태 표시
    if "REPLICATE_API_TOKEN" in st.secrets:
        st.success("API 연결됨 (Replicate) ✅")
    else:
        st.error("API 키가 없습니다! 🚨")
        st.stop()
        
    st.divider()
    
    # 시드 제어
    st.subheader("🎲 캐릭터 고정 (Seed)")
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("New"):
            st.session_state.seed_value = random.randint(0, 999999)
            st.rerun()
    with col2:
        st.number_input("Seed 번호", value=st.session_state.seed_value, disabled=True)
    st.caption("이 번호를 기억하면 같은 캐릭터를 다시 부를 수 있습니다.")
    
    st.divider()
    st.info("Tip: '19+ 모드'를 선택하면 자동으로 검열이 해제됩니다.")

# ===========================
# 2. 메인 화면
# ===========================
st.title("🔥 K-Web Pro Ultimate")
st.caption("화풍, 자세, 외모, 의상을 내 마음대로.")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("1️⃣ 스타일 & 캐릭터")
    
    # [A] 화풍 선택 (19금 옵션 추가)
    with st.container(border=True):
        st.markdown("#### 🎨 화풍 (Art Style)")
        # 19금 옵션을 라디오 버튼에 직접 추가
        art_category = st.radio("장르 선택", 
            ["📸 실사 (Photorealistic)", "🖌️ 2D/일러스트 (Anime)", "🔞 19+ (NSFW)"], 
            horizontal=True
        )
        
        # 스타일에 따른 세부 설정
        style_prompt = ""
        is_nsfw_mode = False

        if "실사" in art_category:
            style_detail = st.selectbox("분위기", ["영화 같은 (Cinematic)", "SNS 감성 (Candid)", "스튜디오 조명 (Studio lighting)"])
            style_prompt = "photorealistic, realistic, 8k uhd, raw photo, dslr"
            
        elif "2D" in art_category:
            style_detail = st.selectbox("분위기", ["웹툰 (Webtoon)", "일본 애니 (Anime)", "지브리 (Ghibli)", "유화 (Oil Painting)"])
            style_prompt = "2D, illustration, anime style, flat color, digital art"
            
        elif "19+" in art_category:
            is_nsfw_mode = True
            st.warning("🔞 19금 모드 활성화: 안전 필터가 해제되고 수위 높은 묘사가 허용됩니다.")
            style_detail = st.selectbox("19+ 스타일", ["실사 야동 스타일 (AV Style, Real)", "성인 웹툰 (Hentai, 2D)"])
            
            if "Real" in style_detail:
                style_prompt = "nsfw, sexy, nude, erotic, raw photo, realistic skin texture, 8k uhd"
            else:
                style_prompt = "nsfw, hentai, ecchi, anime style, explicit"

    # [B] 캐릭터 외모 (직접 입력 추가)
    with st.expander("👤 캐릭터 외모 설정 (열기)", expanded=True):
        gender = st.radio("성별", ["20대 여성 (20yo Woman)", "20대 남성 (20yo Man)", "30대 여성 (30yo Woman)"], horizontal=True)
        
        c1, c2 = st.columns(2)
        with c1:
            hair_style = st.selectbox("머리 모양", ["긴 생머리 (Long straight)", "웨이브 (Wavy)", "단발 (Bob cut)", "포니테일 (Ponytail)", "똥머리 (Bun)"])
        with c2:
            hair_color = st.selectbox("머리색", ["갈색 (Brown)", "검정 (Black)", "금발 (Blonde)", "은발 (Silver)", "빨강 (Red)"])
        
        body_type = st.select_slider("체형", options=["마름", "보통", "글래머/근육질"], value="보통")
        eng_body = {"마름": "slim", "보통": "fit", "글래머/근육질": "curvy, voluptuous, muscular"}[body_type]
        
        # [NEW] 외모 직접 입력 기능
        custom_face = st.text_input("✨ 외모 직접 입력 (선택사항)", placeholder="예: Blue eyes, mole on cheek, elf ears, glossy skin")

with col_right:
    st.subheader("2️⃣ 포즈 & 패션")
    
    # [C] 자세 설정 (NEW 탭 추가)
    with st.container(border=True):
        st.markdown("#### 🧘 자세 (Pose)")
        pose_options = [
            "서 있는 (Standing)",
            "앉아 있는 (Sitting)",
            "누워 있는 (Lying down)",
            "무릎 꿇은 (Kneeling)",
            "네발 기기 (All fours)",
            "뒤태 (Back view)",
            "다리 꼬기 (Crossed legs)",
            "셀카 찍는 (Taking a selfie)",
            "✨ 직접 입력 (Custom)"
        ]
        selected_pose = st.selectbox("자세 선택", pose_options)
        
        final_pose = ""
        if "직접 입력" in selected_pose:
            final_pose = st.text_input("원하는 자세 영어로 입력", placeholder="예: Stretching legs, squatting")
        else:
            final_pose = extract_eng(selected_pose)

    # [D] 의상 설정
    with st.expander("👗 의상 (Fashion) - 열기", expanded=True):
        outfit
