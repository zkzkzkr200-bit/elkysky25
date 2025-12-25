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

# 변수 초기화 (에러 방지용)
style_prompt = ""
is_nsfw_mode = False
final_pose = ""
final_outfit = ""
custom_face = ""
eng_body = ""

with col_left:
    st.subheader("1️⃣ 스타일 & 캐릭터")
    
    # [A] 화풍 선택 (19금 옵션 통합)
    with st.container(border=True):
        st.markdown("#### 🎨 화풍 (Art Style)")
        art_category = st.radio("장르 선택", 
            ["📸 실사 (Photorealistic)", "🖌️ 2D/일러스트 (Anime)", "🔞 19+ (NSFW)"], 
            horizontal=True
        )
        
        if "실사" in art_category:
            style_detail = st.selectbox("분위기", ["영화 같은 (Cinematic)", "SNS 감성 (Candid)", "스튜디오 조명 (Studio lighting)"])
            style_prompt = "photorealistic, realistic, 8k uhd, raw photo, dslr"
            
        elif "2D" in art_category:
            style_detail = st.selectbox("분위기", ["웹툰 (Webtoon)", "일본 애니 (Anime)", "지브리 (Ghibli)", "유화 (Oil Painting)"])
            style_prompt = "2D, illustration, anime style, flat color, digital art"
            
        elif "19+" in art_category:
            is_nsfw_mode = True
            st.warning("🔞 19금 모드: 안전 필터 해제 & 수위 높은 묘사 허용")
            style_detail = st.selectbox("19+ 스타일", ["실사 야동 스타일 (AV Style, Real)", "성인 웹툰 (Hentai, 2D)"])
            
            if "Real" in style_detail:
                style_prompt = "nsfw, sexy, nude, erotic, raw photo, realistic skin texture, 8k uhd"
            else:
                style_prompt = "nsfw, hentai, ecchi, anime style, explicit"

    # [B] 캐릭터 외모 (10대 옵션 복구 완료!)
    with st.expander("👤 캐릭터 외모 설정 (열기)", expanded=True):
        gender = st.radio("성별/나이", 
            [
                "10대 소녀 (Teenage Girl)", 
                "10대 소년 (Teenage Boy)", 
                "20대 여성 (20yo Woman)", 
                "20대 남성 (20yo Man)", 
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
        
        # [NEW] 외모 직접 입력
        custom_face = st.text_input("✨ 외모 직접 입력 (선택사항)", placeholder="예: Blue eyes, flushing face, sweaty skin")

with col_right:
    st.subheader("2️⃣ 포즈 & 패션")
    
    # [C] 자세 설정
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

    # [D] 의상 설정
    with st.expander("👗 의상 (Fashion) - 열기", expanded=True):
        outfit_options = [
            "캐주얼 (Casual clothes)", "오피스룩 (Office wear)", "파티 드레스 (Evening dress)",
            "비키니 (Bikini)", "란제리 (Lingerie)", "교복 (School uniform)", "✨ 직접 입력 (Custom)"
        ]
        selected_outfit = st.selectbox("의상 선택", outfit_options)
        
        if "직접 입력" in selected_outfit:
            custom_outfit = st.text_input("의상 영어로 입력", placeholder="예: See-through shirt, micro skirt")
            final_outfit = custom_outfit if custom_outfit else "Casual clothes"
        else:
            final_outfit = extract_eng(selected_outfit)

    # [E] 배경 및 업로드
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
# 3. 로직: 프롬프트 조립
# ===========================
if generate_btn:
    # 영어 추출
    eng_gender = extract_eng(gender)
    eng_hair = f"{extract_eng(hair_style)} hair, {extract_eng(hair_color)} color"
    
    # 19금 모드일 때 부정 프롬프트 조정
    if is_nsfw_mode:
        base_negative = "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"
    else:
        base_negative = "nsfw, nude, naked, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"

    # 최종 프롬프트 합체
    full_prompt = (
        f"Best quality, masterpiece, {style_prompt}. "
        f"{eng_gender}, {eng_hair}, {eng_body} body. "
        f"{custom_face}. "
        f"{final_pose}, "
        f"wearing {final_outfit}. "
        f"Background is {background_text}."
    )
    
    # API 호출
    try:
        with st.spinner("AI가 생성 중입니다... 🎨"):
            
            # 모델: RealVisXL V4.0 Lightning
            model_id = "adirik/realvisxl-v4.0-lightning:2ef27001faad83347bf7a4186c7a39bb162380c5d7fd1d0bf29fe08410229559"
            
            input_data = {
                "prompt": full_prompt,
                "negative_prompt": base_negative,
                "width": 768, 
                "height": 1152,
                "seed": st.session_state.seed_value,
                "scheduler": "DPM++_SDE_Karras",
                "guidance_scale": 2.0,
                "num_inference_steps": 6,
                "disable_safety_checker": is_nsfw_mode
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
                    st.success(f"완성! (Mode: {art_category})")
                    
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
