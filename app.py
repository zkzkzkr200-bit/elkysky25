import streamlit as st
import replicate
import random
import io
import requests

# --- 페이지 설정 ---
st.set_page_config(
    page_title="K-Web Pro: Dual Engine",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 스타일 ---
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        padding: 20px;
        font-weight: bold;
        font-size: 20px;
        border-radius: 12px;
        background: linear-gradient(90deg, #3B82F6 0%, #8B5CF6 100%);
        color: white;
        border: none;
    }
    .stSelectbox, .stTextInput, .stRadio { font-size: 1.1em; }
</style>
""", unsafe_allow_html=True)

# --- 유틸리티 ---
def extract_eng(text):
    if "(" in text and ")" in text: return text.split("(")[1].split(")")[0]
    return text

# --- 세션 ---
if 'seed_value' not in st.session_state:
    st.session_state.seed_value = random.randint(0, 999999)

# ===========================
# 1. 사이드바
# ===========================
with st.sidebar:
    st.title("⚙️ 설정")
    if "REPLICATE_API_TOKEN" in st.secrets:
        st.success("API 연결됨 ✅")
    else:
        st.error("API 키 없음 🚨")
        st.stop()
    
    st.divider()
    if st.button("🎲 새로운 시드(New Seed)"):
        st.session_state.seed_value = random.randint(0, 999999)
        st.rerun()
    st.caption(f"현재 시드: {st.session_state.seed_value}")

# ===========================
# 2. 메인 화면
# ===========================
st.title("🎨 K-Web Pro: Dual Engine")
st.caption("실사 전문 엔진 vs 애니메이션 전문 엔진 자동 전환")

col_left, col_right = st.columns([1, 1])

# 변수 초기화
final_style_keywords = ""
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
        st.markdown("#### 🎨 화풍")
        art_category = st.radio("장르", ["📸 실사 (Realistic)", "🖌️ 2D/일러스트 (Anime)"], horizontal=True)
        
        if "2D" in art_category:
            is_anime_mode = True
            st.info("🖌️ 애니메이션 전문 엔진이 가동됩니다.")
            style_detail = st.selectbox("분위기", ["일본 애니 (Anime)", "지브리 (Ghibli)", "웹툰 (Webtoon)", "유화 (Oil Painting)"])
            eng_detail = extract_eng(style_detail)
            
            # [2D 전문 프롬프트 강화]
            if "Anime" in eng_detail:
                 final_style_keywords = "masterpiece, best quality, Japanese anime style, anime screencap, vibrant colors, sharp outline, 2D"
            elif "Ghibli" in eng_detail:
                 final_style_keywords = "masterpiece, best quality, Studio Ghibli style, Hayao Miyazaki, watercolor texture, soft pastel colors, pictorial, beautiful scenery, 2D"
            elif "Webtoon" in eng_detail:
                final_style_keywords = "masterpiece, best quality, Korean webtoon style, manhwa, digital illustration, clean lines, 2D"
            elif "Oil Painting" in eng_detail:
                 final_style_keywords = "masterpiece, best quality, oil painting, textured, brushstrokes, impasto, traditional media"
        else:
            is_anime_mode = False
            st.info("📸 실사 전문 엔진(고속)이 가동됩니다.")
            style_detail = st.selectbox("분위기", ["영화 같은 (Cinematic)", "SNS 감성 (Candid)", "스튜디오 조명 (Studio lighting)"])
            final_style_keywords = f"photorealistic, realistic, 8k uhd, raw photo, sharp focus, dslr, high quality, {extract_eng(style_detail)}"

    with st.expander("👤 캐릭터 외모", expanded=True):
        gender = st.radio("성별", ["10대 소녀", "10대 소년", "20대 여성", "20대 남성", "30대 여성"], horizontal=True)
        eng_gender_map = {
            "10대 소녀": "teenage girl", "10대 소년": "teenage boy",
            "20대 여성": "20yo woman", "20대 남성": "20yo man", "30대 여성": "30yo woman"
        }
        
        c1, c2 = st.columns(2)
        with c1:
            hair_style = st.selectbox("머리", ["긴 생머리 (Long straight)", "웨이브 (Wavy)", "단발 (Bob cut)", "포니테일 (Ponytail)", "똥머리 (Bun)"])
        with c2:
            hair_color = st.selectbox("색상", ["갈색 (Brown)", "검정 (Black)", "금발 (Blonde)", "은발 (Silver)", "빨강 (Red)"])
        
        body_type = st.select_slider("체형", options=["마름", "보통", "글래머/근육질"], value="보통")
        
        final_gender = eng_gender_map[gender]
        final_hair = f"{extract_eng(hair_style)} hair, {extract_eng(hair_color)} color"
        final_body = {"마름": "slim", "보통": "fit", "글래머/근육질": "curvy, voluptuous, muscular"}[body_type]
        custom_face = st.text_input("외모 직접 입력", placeholder="예: Blue eyes, blushing face")

with col_right:
    st.subheader("2️⃣ 포즈 & 패션")
    
    with st.container(border=True):
        view_angle = st.selectbox("🎥 앵글", ["정면 (Front view)", "측면 (Side view)", "로우 앵글 (Low angle)", "하이 앵글 (High angle)", "뒤태 (Back view)"])
        final_view_angle = extract_eng(view_angle)

    with st.container(border=True):
        pose_options = ["서 있는 (Standing)", "앉아 있는 (Sitting)", "누워 있는 (Lying down)", "무릎 꿇은 (Kneeling)", "네발 기기 (All fours)", "다리 꼬기 (Crossed legs)", "✨ 직접 입력"]
        selected_pose = st.selectbox("🧘 자세", pose_options)
        if "직접 입력" in selected_pose:
            final_pose = st.text_input("자세 입력 (영어)", placeholder="예: Squatting, legs apart")
        else:
            final_pose = extract_eng(selected_pose)

    with st.expander("👗 의상", expanded=True):
        # 안전한 의상 옵션 (나체 제외)
        outfit_options = ["캐주얼", "오피스룩", "파티 드레스", "비키니", "란제리", "교복", "✨ 직접 입력"]
        selected_outfit = st.selectbox("의상 선택", outfit_options)
        
        eng_outfit_map = {
            "캐주얼": "casual clothes", "오피스룩": "office wear", "파티 드레스": "evening dress",
            "비키니": "bikini", "란제리": "lingerie", "교복": "school uniform"
        }
        
        if "직접 입력" in selected_outfit:
            final_outfit = st.text_input("의상 입력 (영어)", placeholder="예: See-through shirt")
            if not final_outfit: final_outfit = "casual clothes"
        else:
            final_outfit = eng_outfit_map[selected_outfit]

    background_text = st.text_area("배경", placeholder="예: 침실, 호텔, 해변, 지브리 스타일 언덕", height=80)
    
    with st.expander("📸 사진 변형 (Img2Img)"):
        uploaded_file = st.file_uploader("이미지 업로드", type=["jpg", "png", "jpeg"])
        strength_val = st.slider("변경 강도", 0.1, 1.0, 0.65)

    st.divider()
    generate_btn = st.button("🚀 이미지 생성 (Generate)")

# ===========================
# 3. 로직 (듀얼 엔진)
# ===========================
if generate_btn:
    
    # 기본 부정 프롬프트
    base_negative = "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, ugly, deformed"
    
    # 19금 방어 (필터 통과용)
    base_negative = "nsfw, nude, naked, explicit, " + base_negative

    # 모드별 추가 부정 프롬프트
    if is_anime_mode:
        base_negative += ", photorealistic, realistic, 3d, photo" # 애니메이션에서 실사 느낌 제거
    else:
        base_negative += ", painting, drawing, anime, cartoon, sketch" # 실사에서 그림 느낌 제거

    full_prompt = (
        f"{final_style_keywords}. "
        f"{final_view_angle}, {final_pose}, " 
        f"{final_gender}, {final_hair}, {final_body} body. "
        f"{custom_face}. "
        f"wearing {final_outfit}. "
        f"Background is {background_text}."
    )
    
    try:
        # ==============================================================================
        # [핵심] 듀얼 엔진 시스템: 선택한 장르에 따라 다른 모델과 설정을 사용합니다.
        # ==============================================================================
        if is_anime_mode:
            engine_name = "🖌️ 애니메이션 전문 엔진 (Animagine XL)"
            # 2D 전문 모델 주소 (공식 안정화 버전)
            model_id = "cjwbw/animagine-xl-3.1:6afe2e6b27dad2d6f480b59195c221884b6acc589ff4d05ff0e5fc058690fbb9"
            # 애니메이션 모델 전용 설정 (높은 스텝, 높은 가이던스)
            input_data = {
                "prompt": full_prompt,
                "negative_prompt": base_negative,
                "width": 832, "height": 1216, # 애니메이션에 최적화된 비율
                "seed": st.session_state.seed_value,
                "guidance_scale": 7.0, 
                "num_inference_steps": 28
            }
        else:
            engine_name = "📸 실사 전문 엔진 (RealVisXL Lightning)"
            # 실사 전문 모델 주소 (공식 안정화 버전)
            model_id = "adirik/realvisxl-v4.0-lightning:2ef27001faad83347bf7a4186c7a39bb162380c5d7fd1d0bf29fe08410229559"
            # 실사 라이트닝 모델 전용 설정 (낮은 스텝, 낮은 가이던스)
            input_data = {
                "prompt": full_prompt,
                "negative_prompt": base_negative,
                "width": 768, "height": 1152,
                "seed": st.session_state.seed_value,
                "guidance_scale": 2.0,
                "num_inference_steps": 6
            }
        # ==============================================================================

        with st.spinner(f"🚀 {engine_name} 가동 중..."):
            
            if uploaded_file:
                input_data["image"] = uploaded_file
                input_data["prompt_strength"] = strength_val

            output = replicate.run(model_id, input=input_data)
            
            if output:
                item = output[0] if isinstance(output, list) else output
                if hasattr(item, "read"): data = item.read()
                elif isinstance(item, str) and item.startswith("http"): data = requests.get(item).content
                else: data = None

                if data:
                    st.balloons()
                    st.image(data, use_container_width=True)
                    st.success(f"완성! ({engine_name})")
                    st.download_button("⬇️ 다운로드", io.BytesIO(data), f"img_{st.session_state.seed_value}.png", "image/png")

    except Exception as e:
        st.error(f"에러 발생: {e}")
