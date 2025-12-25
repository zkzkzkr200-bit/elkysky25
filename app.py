import streamlit as st
import replicate
import random
import io
import requests

# --- 페이지 설정 ---
st.set_page_config(
    page_title="K-Web Pro Studio (Update)",
    page_icon="🎨",
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

# --- 유틸리티 함수: 한글(영어)에서 영어만 추출 ---
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
    
    # 고급: 안전 필터
    use_safety = st.toggle("안전 필터 사용 (Safety Filter)", value=False)
    st.info("Tip: 필터를 끄면 자유도가 높아지지만 책임은 본인에게 있습니다.")

# ===========================
# 2. 메인 화면: 디테일 UI
# ===========================
st.title("🎨 K-Web Pro Studio")
st.caption("원하는 스타일과 의상을 자유롭게 선택하세요.")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("1️⃣ 스타일 & 캐릭터")
    
    # [A] 화풍 선택 (업데이트됨!)
    with st.container(border=True):
        st.markdown("#### 🎨 화풍 (Art Style)")
        art_category = st.radio("장르 선택", ["📸 실사 (Photorealistic)", "🖌️ 2D/일러스트 (Anime & Art)"], horizontal=True)
        
        # 장르에 따른 세부 스타일 변경
        if "실사" in art_category:
            style_detail = st.selectbox("분위기 선택", 
                ["영화 같은 (Cinematic)", "인스타그램 감성 (Candid, SNS)", "스튜디오 조명 (Studio lighting)", "폴라로이드 (Polaroid)", "흑백 사진 (B&W)"]
            )
            # 실사 전용 프롬프트
            style_prompt = "photorealistic, realistic, 8k uhd, raw photo, dslr"
        else:
            style_detail = st.selectbox("화풍 선택", 
                ["웹툰 스타일 (Webtoon)", "일본 애니메이션 (Anime)", "지브리 감성 (Studio Ghibli)", "수채화 (Watercolor)", "사이버펑크 (Cyberpunk)", "유화 (Oil Painting)"]
            )
            # 2D 전용 프롬프트
            style_prompt = "2D, illustration, painting, flat color, anime style, digital art"

    # [B] 캐릭터 외모
    with st.expander("👤 캐릭터 외모 설정 (열기)", expanded=True):
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
        
        body_type = st.select_slider("체형", options=["마름", "보통", "글래머/근육질"], value="보통")
        eng_body = {"마름": "slim", "보통": "fit", "글래머/근육질": "curvy/muscular"}[body_type]

with col_right:
    st.subheader("2️⃣ 의상 & 배경")
    
    # [C] 의상 설정 (업데이트됨! 직접 입력 추가)
    with st.container(border=True):
        st.markdown("#### 👗 의상 (Fashion)")
        
        # 의상 목록
        outfit_options = [
            "캐주얼 (Casual T-shirt and jeans)", 
            "오피스룩 (White shirt and skirt)", 
            "파티 드레스 (Elegant evening dress)", 
            "후드티 & 레깅스 (Hoodie and leggings)",
            "수영복 (Bikini)", 
            "교복 (School uniform)",
            "한복 (Hanbok, Korean traditional)",
            "✨ 직접 입력 (Custom)"
        ]
        
        selected_outfit = st.selectbox("의상 선택", outfit_options)
        
        # '직접 입력' 선택 시 텍스트 입력창 표시
        final_outfit = ""
        if "직접 입력" in selected_outfit:
            custom_outfit = st.text_input("원하는 의상을 영어로 적어주세요", placeholder="예: Red leather jacket, White yoga pants")
            final_outfit = custom_outfit if custom_outfit else "Casual clothes" # 비어있으면 기본값
        else:
            final_outfit = extract_eng(selected_outfit)
            
    # [D] 배경 설정
    background_text = st.text_area("배경 묘사 (한글 가능)", placeholder="예: 벚꽃이 흩날리는 공원, 비 내리는 도시 밤거리, 럭셔리 호텔 침실", height=100)
    
    # [E] 이미지 업로드 (Img2Img)
    with st.expander("📸 사진 변형 (Img2Img)", expanded=False):
        uploaded_file = st.file_uploader("참조 이미지 업로드", type=["jpg", "png", "jpeg"])
        strength_val = 0.65
        if uploaded_file:
            st.image(uploaded_file, width=200)
            strength_val = st.slider("변경 강도", 0.1, 1.0, 0.65)

    st.divider()
    generate_btn = st.button("✨ 이미지 생성 (Generate)")

# ===========================
# 3. 로직: 프롬프트 조립 및 생성
# ===========================
if generate_btn:
    # 1. 프롬프트 조립
    eng_gender = extract_eng(gender)
    eng_hair = f"{extract_eng(hair_style)} hair, {extract_eng(hair_color)} color"
    eng_style_detail = extract_eng(style_detail)
    
    # 최종 프롬프트 (Style Prompt가 앞에 붙어서 화풍을 결정함)
    full_prompt = (
        f"Best quality, masterpiece, {style_prompt}, {eng_style_detail}. "
        f"{eng_gender}, {eng_hair}, {eng_body} body. "
        f"wearing {final_outfit}. "
        f"Background is {background_text}."
    )
    
    # 2. API 호출
    try:
        with st.spinner("AI가 그림을 그리고 있습니다... 🎨"):
            
            # 모델 ID: RealVisXL V4.0 Lightning (검증된 버전)
            model_id = "adirik/realvisxl-v4.0-lightning:2ef27001faad83347bf7a4186c7a39bb162380c5d7fd1d0bf29fe08410229559"
            
            input_data = {
                "prompt": full_prompt,
                "negative_prompt": "nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry",
                "width": 768, 
                "height": 1152,
                "seed": st.session_state.seed_value,
                "scheduler": "DPM++_SDE_Karras",
                "guidance_scale": 2.0,
                "num_inference_steps": 6,
                "disable_safety_checker": not use_safety
            }

            if uploaded_file:
                input_data["image"] = uploaded_file
                input_data["prompt_strength"] = strength_val

            # 결과 받기
            output = replicate.run(model_id, input=input_data)
            
            # 결과 처리
            image_data = None
            if output:
                result_item = output[0] if isinstance(output, list) else output

                if hasattr(result_item, "read"):
                    image_data = result_item.read()
                elif isinstance(result_item, str) and result_item.startswith("http"):
                    image_data = requests.get(result_item).content
                
                if image_data:
                    st.balloons()
                    st.image(image_data, use_container_width=True)
                    st.success(f"완성! (Style: {art_category})")
                    
                    st.download_button(
                        label="⬇️ 이미지 저장",
                        data=io.BytesIO(image_data),
                        file_name=f"kweb_{st.session_state.seed_value}.png",
                        mime="image/png"
                    )
                    
                    with st.expander("🔍 프롬프트 확인"):
                        st.code(full_prompt)

    except Exception as e:
        st.error(f"에러 발생: {e}")
