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
st.title("🔥 K-Web Pro Ultimate")
st.caption("RealVisXL V4.0 (High Quality)")

col_left, col_right = st.columns([1, 1])

# 변수 초기화
style_prompt = ""
final_pose = ""
final_outfit = ""
custom_face = ""
eng_body = ""

with col_left:
    st.subheader("1️⃣ 스타일 & 캐릭터")
    
    with st.container(border=True):
        st.markdown("#### 🎨 화풍 (Art Style)")
        
        art_category = st.radio("장르 선택", 
            ["📸 실사 (Photorealistic)", "🖌️ 2D/일러스트 (Anime)"], 
            horizontal=True
        )
        
        # 19금 모드 (중복 선택 가능)
        is_nsfw = st.checkbox("🔞 19금 모드 적용 (Enable NSFW)", value=False)
        
        if "실사" in art_category:
            style_detail = st.selectbox("분위기", ["영화 같은 (Cinematic)", "SNS 감성 (Candid)", "스튜디오 조명 (Studio lighting)"])
            base_style = "photorealistic, realistic, 8k uhd, raw photo, dslr, soft lighting, high quality, film grain"
            nsfw_keywords = "nsfw, sexy, nude, erotic, raw photo, realistic skin texture, detailed skin" if is_nsfw else ""
        else:
            style_detail = st.selectbox("분위기", ["웹툰 (Webtoon)", "일본 애니 (Anime)", "지브리 (Ghibli)", "유화 (Oil Painting)"])
            base_style = "2D, illustration, anime style, flat color, digital art"
            nsfw_keywords = "nsfw, hentai, ecchi, anime style, explicit" if is_nsfw else ""

        if is_nsfw:
            st.warning("🔥 수위 제한 해제됨")

    with st.expander("👤 캐릭터 외모 설정 (열기)", expanded=True):
        gender = st.radio("성별/나이", 
            [
                "10대 소녀 (Teenage Girl)", "10대 소년 (Teenage Boy)", 
                "20대 여성 (20yo Woman)", "20대 남성 (20yo Man)", 
                "30대 여성 (30yo Woman)"
            ], 
            horizontal=True
        )
        
        c1, c2 = st.columns(2)
        with c1:
            hair_style = st.selectbox("머리 모양", ["긴 생머리 (Long straight)", "웨이브 (Wavy)", "단발 (Bob cut)", "포니테일 (Ponytail)", "똥머리 (Bun)"])
        with c2:
            hair_color = st.selectbox("머리색", ["갈색 (Brown)", "검정 (Black)", "금발 (Blonde)", "은발 (Silver)", "빨강 (Red)"])
        
        body_type = st.select_slider("체형", options=["마름", "보통", "글래머/근육질"], value="보통")
        eng_body = {"마름": "slim", "보통": "fit", "글래머/근육질": "curvy, voluptuous, muscular"}[body_type]
        
        custom_face = st.text_input("✨ 외모 직접 입력 (선택사항)", placeholder="예: Blue eyes, flushing face, sweaty skin")

with col_right:
    st.subheader("2️⃣ 포즈 & 패션")
    
    with st.container(border=True):
        st.markdown("#### 🧘 자세 (Pose)")
        pose_options = [
            "서 있는 (Standing)", "앉아 있는 (Sitting)", "누워 있는 (Lying down)",
            "무릎 꿇은 (Kneeling)", "네발 기기 (All fours)", "뒤태 (Back view)",
            "다리 꼬기 (Crossed legs)", "셀카 찍는 (Taking a selfie)", "✨ 직접 입력 (Custom)"
        ]
        selected_pose = st.selectbox("자세 선택", pose_options)
        
        if "직접 입력" in selected_pose:
            final_pose = st.text_input("원하는 자세 영어로 입력", placeholder="예: Spreading legs, squatting")
        else:
            final_pose = extract_eng(selected_pose)

    with st.expander("👗 의상 (Fashion) - 열기", expanded=True):
        outfit_options = [
            "캐주얼 (Casual clothes)", "오피스룩 (Office wear)", "파티 드레스 (Evening dress)",
            "비키니 (Bikini)", "란제리 (Lingerie)", "교복 (School uniform)", 
            "알몸/나체 (Nude, Naked) - 19금 전용",
            "✨ 직접 입력 (Custom)"
        ]
        selected_outfit = st.selectbox("의상 선택", outfit_options)
        
        if "직접 입력" in selected_outfit:
            custom_outfit = st.text_input("의상 영어로 입력", placeholder="예: See-through shirt, micro skirt")
            final_outfit = custom_outfit if custom_outfit else "Casual clothes"
        else:
            final_outfit = extract_eng(selected_outfit)

    background_text = st.text_area("배경 묘사", placeholder="예: 침실, 호텔, 해변, 비 내리는 거리", height=80)
    
    with st.expander("📸 사진 변형 (Img2Img)", expanded=False):
        uploaded_file = st.file_uploader("참조 이미지", type=["jpg", "png", "jpeg"])
        strength_val = 0.65
        if uploaded_file:
            st.image(uploaded_file, width=200)
            strength_val = st.slider("변경 강도", 0.1, 1.0, 0.65)

    st.divider()
    generate_btn = st.button("✨ 이미지 생성 (Generate)")

# ===========================
# 3. 로직
# ===========================
if generate_btn:
    eng_gender = extract_eng(gender)
    eng_hair = f"{extract_eng(hair_style)} hair, {extract_eng(hair_color)} color"
    
    # 19금 모드 ON/OFF에 따른 부정 프롬프트
    if is_nsfw:
        base_negative = "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"
    else:
        base_negative = "nsfw, nude, naked, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"

    full_prompt = (
        f"Best quality, masterpiece, {base_style}, {nsfw_keywords}. "
        f"{eng_gender}, {eng_hair}, {eng_body} body. "
        f"{custom_face}. "
        f"{final_pose}, "
        f"wearing {final_outfit}. "
        f"Background is {background_text}."
    )
    
    try:
        with st.spinner("AI가 고화질로 렌더링 중입니다... (약 10초) 🎨"):
            
            # [수정됨] 안정적인 RealVisXL V4.0 (Standard) 모델
            model_id = "konieshadow/realvisxl-v4.0:4f2913076880017127c59c5d070e309255a025687352f2052445e4125a25034c"
            
            input_data = {
                "prompt": full_prompt,
                "negative_prompt": base_negative,
                "width": 768, 
                "height": 1152,
                "seed": st.session_state.seed_value,
                "scheduler": "K_EULER_ANCESTRAL",
                "guidance_scale": 7.0, # Standard 모델 권장값
                "num_inference_steps": 30, # 퀄리티 높음
                "disable_safety_checker": is_nsfw
            }

            if uploaded_file:
                input_data["image"] = uploaded_file
                input_data["prompt_strength"] = strength_val

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
                    st.success(f"완성! (NSFW: {'ON' if is_nsfw else 'OFF'})")
                    
                    st.download_button(
                        label="⬇️ 이미지 저장",
                        data=io.BytesIO(image_data),
                        file_name=f"kweb_{st.session_state.seed_value}.png",
                        mime="image/png"
                    )
                    
                    with st.expander("🔍 AI가 받은 주문서"):
                        st.code(full_prompt)

    except replicate.exceptions.ReplicateError as e:
        # 에러 메시지 분석
        if "429" in str(e) or "throttled" in str(e):
             st.error("🚦 속도 제한 (429 Error):")
             st.warning("잠시만(10초) 기다렸다가 다시 누르세요! (또는 Replicate 결제 잔액을 확인해주세요)")
        else:
             st.error(f"API 에러: {e}")
    except Exception as e:
        st.error(f"시스템 에러: {e}")
