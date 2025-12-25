import streamlit as st
import replicate
import random
import io
import requests

# --- 페이지 설정 ---
st.set_page_config(
    page_title="K-Web Pro Studio",
    page_icon="📸",
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
    .stSelectbox, .stTextInput {
        font-size: 1.1em;
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
    st.caption("이 번호를 기억하면 같은 얼굴을 다시 부를 수 있습니다.")
    
    st.divider()
    
    # 고급: 안전 필터
    use_safety = st.toggle("안전 필터 사용 (Safety Filter)", value=False)
    st.info("Tip: 필터를 끄면 검열이 사라지지만 책임은 본인에게 있습니다.")

# ===========================
# 2. 메인 화면: 디테일 UI
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
    if uploaded_file:
        st.image(uploaded_file, width=200)
        strength_val = st.slider("변경 강도", 0.1, 1.0, 0.65)

    st.divider()
    
    # [F] 최종 생성 버튼
    generate_btn = st.button("✨ 스튜디오 촬영 시작 (Generate)")

# ===========================
# 3. 로직: 프롬프트 조립 및 생성
# ===========================
if generate_btn:
    # 1. 프롬프트 생성 (안전하게 변수 분리)
    eng_gender = extract_eng(gender)
    eng_hair = f"{extract_eng(hair_style)} hair, {extract_eng(hair_color)} color"
    eng_body = extract_eng(body_type)
    eng_fashion = f"{extract_eng(fashion_style)}, {clothes_detail}"
    eng_camera = f"{extract_eng(view_angle)}, {extract_eng(lighting)} lighting"
    
    # 최종 문장 합치기
    full_prompt = (
        f"Best quality, masterpiece, photorealistic, 8k uhd, raw photo. "
        f"{eng_gender}, {eng_hair}, {eng_body} body. "
        f"wearing {eng_fashion}. {eng_camera}. "
        f"Background is {background_text}."
    )
    
    # 2. API 호출
    try:
        with st.spinner("AI 모델 섭외 중... (첫 시도는 1분 정도 걸릴 수 있습니다) 📸"):
            
            # 모델 ID: RealVisXL V4.0 Lightning (공식 검증 버전)
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
            
            # 결과 처리 (URL이든 파일이든 모두 대응)
            image_data = None
            if output:
                # 결과가 리스트라면 첫 번째 것만 가져옴
                result_item = output[0] if isinstance(output, list) else output

                # (1) 파일 객체인 경우
                if hasattr(result_item, "read"):
                    image_data = result_item.read()
                # (2) URL 주소인 경우
                elif isinstance(result_item, str) and result_item.startswith("http"):
                    image_data = requests.get(result_item).content
                
                # 이미지 표시
                if image_data:
                    st.balloons()
                    st.image(image_data, use_container_width=True)
                    st.success(f"촬영 완료! (Seed: {st.session_state.seed_value})")
                    
                    st.download_button(
                        label="⬇️ 원본 다운로드",
                        data=io.BytesIO(image_data),
                        file_name=f"kweb_studio_{st.session_state.seed_value}.png",
                        mime="image/png"
                    )
                    
                    with st.expander("🔍 AI가 받은 실제 주문서(Prompt) 보기"):
                        st.code(full_prompt)

    except replicate.exceptions.ReplicateError as e:
        st.error(f"API 에러: {e}")
        st.warning("팁: 결제 카드가 등록되어 있는지, 혹은 한도가 초과되지 않았는지 확인해주세요.")
    except Exception as e:
        st.error(f"시스템 에러: {e}")
