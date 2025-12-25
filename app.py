import streamlit as st
import replicate
import random
import io
from PIL import Image

# --- 페이지 설정 ---
st.set_page_config(
    page_title="K-Web Pro Master",
    page_icon="📸",
    layout="wide", # 가로로 넓게 보기
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
    .stSelectbox, .stTextInput {
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

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
    st.caption("이 번호를 기억하면 같은 얼굴을 다시 부를 수 있습니다.")
    
    st.divider()
    
    # 고급: 안전 필터
    use_safety = st.toggle("안전 필터 사용 (Safety Filter)", value=False)
    st.info("Tip: 필터를 끄면 검열이 사라지지만 책임은 본인에게 있습니다.")

# ===========================
# 2. 메인 화면: 디테일 UI 복원
# ===========================
st.title("📸 K-Web Pro Studio")
st.caption("선택만 하세요. 프롬프트는 AI가 만듭니다.")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("1️⃣ 모델 설정 (Identity)")
    
    # [A] 기본 외모
    with st.container(border=True):
        st.markdown("#### 👤 헤어 및 외모")
        
        gender = st.radio("성별/나이대", 
            ["20대 여성 (20yo Woman)", "20대 남성 (20yo Man)", "10대 소녀 (Teenage Girl)", "30대 여성 (30yo Woman)"], 
            horizontal=True
        )
        
        c1, c2 = st.columns(2)
        with c1:
            hair_style = st.selectbox("머리 모양", 
                ["긴 생머리 (Long straight)", "웨이브 펌 (Wavy perm)", "단발 (Bob cut)", "포니테일 (Ponytail)", "똥머리 (Bun)", "땋은 머리 (Braids)"]
            )
        with c2:
            hair_color = st.selectbox("머리색", 
                ["자연 갈색 (Brown)", "검정 (Black)", "금발 (Blonde)", "은발 (Silver)", "빨강 (Red)", "파스텔 핑크 (Pink)"]
            )
            
        body_type = st.select_slider("체형 선택", options=["마름 (Slim)", "보통 (Fit)", "글래머 (Curvy)", "근육질 (Muscular)"], value="보통 (Fit)")

    # [B] 패션 스타일
    with st.expander("👗 패션 (Fashion) - 열기", expanded=False):
        fashion_style = st.selectbox("스타일 테마", 
            ["캐주얼 (Casual)", "오피스룩 (Office)", "스트릿 패션 (Street)", "파티 드레스 (Party Dress)", "수영복 (Swimwear)", "판타지 갑옷 (Fantasy Armor)", "교복 (School Uniform)"]
        )
        clothes_detail = st.text_input("의상 디테일 (선택)", placeholder="예: 흰색 셔츠, 청바지, 빨간 목도리")

    # [C] 구도 및 시선
    with st.expander("🎥 구도 및 시선 (Camera)", expanded=False):
        view_angle = st.selectbox("촬영 앵글", ["정면 (Front view)", "측면 (Side view)", "로우 앵글 (Low angle)", "셀카 구도 (Selfie)"])
        lighting = st.selectbox("조명 분위기", ["자연광 (Natural)", "스튜디오 조명 (Studio)", "네온 사인 (Neon)", "노을 (Sunset)"])

with col_right:
    st.subheader("2️⃣ 배경 및 추가요소")
    
    # [D] 배경 설정
    background_text = st.text_area("배경 묘사 (한글 가능)", placeholder="예: 벚꽃이 흩날리는 공원, 비 내리는 강남대로, 고급 호텔 로비", height=100)
    
    # [E] 이미지 업로드 (Img2Img)
    st.markdown("#### 📸 사진 변형 (선택사항)")
    uploaded_file = st.file_uploader("참조 이미지를 올리면 변형합니다.", type=["jpg", "png", "jpeg"])
    strength_val = 0.65
    if uploaded
