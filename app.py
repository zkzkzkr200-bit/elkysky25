import streamlit as st
import replicate
import random
import io
import requests
import time

# --- 페이지 설정 ---
st.set_page_config(
    page_title="K-Web Pro HQ",
    page_icon="💎",
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
st.title("💎 K-Web Pro HQ")
st.caption("Dual Engine System (실사/2D 전문 모델 자동 전환)")

col_left, col_right = st.columns([1, 1])

# [변수 초기화]
final_style_keywords = "" 
nsfw_keywords = ""
final_view_angle = ""
final_gender = ""
final_hair = ""
final_body = ""
final_pose = ""
final_outfit = ""
custom_face = ""
# 2D/실사 구분용 플래그
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
        
        if "2D" in art_category:
            is_anime_mode = True # 2D 모드 활성화
            
            style_detail = st.selectbox("분위기", ["웹툰 스타일 (Webtoon)", "일본 애니메이션 (Anime)", "지브리 스튜디오 (Studio Ghibli)", "유화 (Oil Painting)"])
            eng_detail = extract_eng(style_detail)

            # [2D 전용 프롬프트 강화]
            if "Webtoon" in eng_detail:
                final_style_keywords = "masterpiece, best quality, Korean webtoon style, manhwa, sharp lines, vibrant colors, digital art"
            elif "Anime" in eng_detail:
                 final_style_keywords = "masterpiece, best quality, Japanese anime style, anime screencap, cel shading, high quality animation"
            elif "Ghibli" in eng_detail:
                 final_style_keywords = "masterpiece, best quality, Studio Ghibli style, Hayao Miyazaki, watercolor style, scenic, soft lighting, fantasy"
            elif "Oil Painting" in eng_detail:
                 final_style_keywords = "masterpiece, best quality, oil painting, textured, traditional medium, impasto"

            if is_nsfw:
                nsfw_keywords = "nsfw, hentai, ecchi, explicit, uncensored"
            else:
                nsfw_keywords = ""
                
        else: # 실사 모드
            is_anime_mode = False
            
            style_detail = st.selectbox("분위기", ["영화 같은 (Cinematic)", "SNS 감성 (Candid)", "스튜디오 조명 (Studio lighting)"])
            final_style_keywords = f"photorealistic, realistic, 8k uhd, raw photo, sharp focus, dslr, high quality, film grain, {extract_eng(style_detail)}"
            
            if is_nsfw:
                nsfw_keywords = "nsfw, sexy, nude, erotic, raw photo, realistic skin texture, detailed skin"
            else:
                nsfw_keywords = ""

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
        
        final_gender = extract_eng(gender)
        final_hair = f"{extract_eng(hair_style)} hair, {extract_eng(hair_color)} color"
        final_body = {"마름": "slim", "보통": "fit", "글래머/근육질": "curvy, voluptuous, muscular"}[body_type]
        
        custom_face = st.text_input("✨ 외모 직접 입력 (선택사항)", placeholder="예: Blue eyes, flushing face, detailed skin")

with col_right:
    st.subheader("2️⃣ 포즈 & 패션")
    
    with st.container(border=True):
        st.markdown("#### 🎥 시점 (Viewpoint)")
        view_angle = st.selectbox("카메라 앵글", 
            ["정면 (Front view)", "측면 (Side view)", "로우 앵글 (Low angle, from below)", "하이 앵글 (High angle, from above)", "셀카 구도 (Selfie shot)", "전신 샷 (Full body shot)"]
        )
        final_view_angle = extract_eng(view_angle)

    with st.container(border=True):
        st.markdown("#### 🧘 자세 (Pose)")
        pose_options = [
            "서 있는 (Standing)", "앉아 있는 (Sitting)", "누워 있는 (Lying down)",
            "무릎 꿇은 (Kneeling)", "네발 기기 (All fours)", "뒤태 (Back view)",
            "다리 꼬기 (Crossed legs)", "✨ 직접 입력 (Custom)"
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

    background_text = st.text_area("배경 묘사", placeholder="예: 침실, 호텔, 해변, 비 내리는 거리, 디테일한 배경", height=80)
    
    with st.expander("📸 사진 변형 (Img2Img)", expanded=False):
        uploaded_file = st.file_uploader("참조 이미지", type=["jpg", "png", "jpeg"])
        strength_val = 0.65
        if uploaded_file:
            st.image(uploaded_file, width=200)
            strength_val = st.slider("변경 강도", 0.1, 1.0, 0.65)

    st.divider()
    generate_btn = st.button("💎 초고화질 이미지 생성 (Generate HQ)")

# ===========================
# 3. 로직 및 실행
# ===========================
if generate_btn:
    
    # 1. 부정 프롬프트 설정 (실사 vs 2D에 따라 다르게)
    common_negative = "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name, ugly, deformed"
    
    if is_anime_mode:
        # 2D일 때는 '실사 느낌'을 부정 프롬프트에 추가해서 그림처럼 나오게 유도
        base_negative = common_negative + ", photorealistic, realistic, 3d, photograph"
    else:
        # 실사일 때는 '그림 느낌'을 부정 프롬프트에 추가
        base_negative = common_negative + ", painting, drawing, illustration, 2d, anime, cartoon, sketch"

    if not is_nsfw:
        base_negative = "nsfw, nude, naked, explicit, " + base_negative

    # 2. 최종 프롬프트 조립
    full_prompt = (
        f"{final_style_keywords}, {nsfw_keywords}. "
        f"{final_view_angle}, {final_pose}, " 
        f"{final_gender}, {final_hair}, {final_body} body. "
        f"{custom_face}. "
        f"wearing {final_outfit}. "
        f"Background is {background_text}."
    )
    
    try:
        # [듀얼 엔진 시스템]
        # 사용자의 선택에 따라 완전히 다른 전문가 모델을 호출합니다.
        
        if is_anime_mode:
            # [2D 전문] Animagine XL 3.1 (애니메이션 최강 모델)
            model_id = "cagliostrolab/animagine-xl-3.1:a1075677d54b85da26b0d911bb26484a0c201a09d6e4b986c7501b44473e6542"
            status_text = "🎨 2D/애니메이션 전문 엔진 가동 중..."
        else:
            # [실사 전문] RealVisXL V4.0 (실사 최강 모델)
            model_id = "konieshadow/realvisxl-v4.0:4f2913076880017127c59c5d070e309255a025687352f2052445e4125a25034c"
            status_text = "📸 실사 전문 엔진 가동 중..."

        with st.spinner(f"{status_text} (약 15~20초)"):
            
            input_data = {
                "prompt": full_prompt,
                "negative_prompt": base_negative,
                "width": 832, # Animagine 등 최신 모델에 최적화된 비율
                "height": 1216,
                "seed": st.session_state.seed_value,
                "scheduler": "K_EULER_ANCESTRAL", 
                "guidance_scale": 7.0, 
                "num_inference_steps": 30,
                # "disable_safety_checker": is_nsfw # 일부 모델은 이 옵션이 없어도 됨 (자동처리)
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
                    st.success(f"완성! (Mode: {'2D/Anime' if is_anime_mode else 'Realism'})")
                    
                    st.download_button(
                        label="⬇️ 고화질 이미지 저장",
                        data=io.BytesIO(image_data),
                        file_name=f"kweb_hq_{st.session_state.seed_value}.png",
                        mime="image/png"
                    )
                    
                    with st.expander("🔍 AI 주문서 확인"):
                        st.code(full_prompt)

    except replicate.exceptions.ReplicateError as e:
        if "429" in str(e) or "throttled" in str(e):
             st.error("🚦 속도 제한 (429 Error):")
             st.warning("서버가 붐빕니다. 20초만 쉬었다가 다시 눌러주세요!")
        elif "NSFW" in str(e):
             st.error("🚨 NSFW 차단됨:")
             st.warning("프롬프트 수위를 조금만 낮춰주세요.")
        else:
             st.error(f"API 에러: {e}")
    except Exception as e:
        st.error(f"시스템 에러: {e}")
