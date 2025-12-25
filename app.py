import streamlit as st
import replicate
import random
import io
from PIL import Image

# --- 페이지 설정 ---
st.set_page_config(
    page_title="K-Web Pro (Uncensored)",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 스타일 (모바일/PC 공용) ---
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        padding: 15px;
        font-weight: bold;
        font-size: 18px;
        border-radius: 10px;
        background: linear-gradient(45deg, #FF4B4B, #FF914D);
        color: white;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# --- 세션 관리 ---
if 'seed_value' not in st.session_state:
    st.session_state.seed_value = random.randint(0, 999999)

# ===========================
# 1. 사이드바 설정
# ===========================
with st.sidebar:
    st.header("⚙️ 스튜디오 설정")
    
    # [시드 제어]
    st.subheader("🎲 시드 (Seed)")
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("랜덤"):
            st.session_state.seed_value = random.randint(0, 999999)
            st.rerun()
    with col2:
        st.session_state.seed_value = st.number_input("Seed", value=st.session_state.seed_value, label_visibility="collapsed")
    st.caption(f"Current Seed: {st.session_state.seed_value}")
    
    st.divider()
    st.info("Tip: RealVisXL V4.0 Lightning 모델 사용 중 (검열이 적고 실사에 강력함)")

# ===========================
# 2. 메인 화면
# ===========================
st.title("⚡ K-Web Pro")
st.caption("Replicate API 기반 / 고화질 / 자유 생성")

# API 키 체크
if "REPLICATE_API_TOKEN" not in st.secrets:
    st.error("🚨 치명적 오류: Secrets에 API 토큰이 없습니다.")
    st.info("Streamlit 대시보드에서 'REPLICATE_API_TOKEN'을 설정해주세요.")
    st.stop()

st.divider()

# [A] 이미지 업로드 (Img2Img)
with st.expander("📸 [선택] 사진 업로드하여 변형하기 (Img2Img)", expanded=False):
    uploaded_file = st.file_uploader("참조할 이미지를 선택하세요", type=["jpg", "png", "jpeg", "webp"])
    strength_val = 0.65
    
    if uploaded_file:
        st.image(uploaded_file, caption="참조 이미지", use_container_width=True)
        strength_val = st.slider("변형 강도 (Strength)", 0.1, 1.0, 0.65, help="낮으면 원본 유지, 높으면 창의적 변형")

st.divider()

# [B] 프롬프트 입력
base_prompt = "Best quality, masterpiece, photorealistic, 8k uhd, raw photo, realistic lighting, "
user_prompt = st.text_area("주문 내용 (영어 입력 권장)", placeholder="e.g. A portrait of a woman in black dress, city night background", height=100)
negative_prompt = "nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"

# [C] 생성 버튼
if st.button("🚀 이미지 생성 (Start)"):
    if not user_prompt:
        st.warning("내용을 입력해주세요!")
    else:
        try:
            with st.spinner("AI가 그리는 중... (약 10초)"):
                
                # 1. 모델 ID (RealVisXL V4.0 Lightning)
                model_id = "lucataco/realvisxl-v4.0-lightning:7d04e4c25143093238964724451662c53a819c4d922097e887e07675f91753c1"
                
                # 2. 입력 데이터 구성
                input_data = {
                    "prompt": base_prompt + user_prompt,
                    "negative_prompt": negative_prompt,
                    "width": 768,
                    "height": 1152,
                    "seed": st.session_state.seed_value,
                    "scheduler": "K_EULER_ANCESTRAL",
                    "guidance_scale": 3.0, # Lightning 모델은 낮은 수치가 자연스러움
                    "num_inference_steps": 20
                }

                # 3. 이미지 업로드 처리 (호환성 강화)
                if uploaded_file:
                    input_data["image"] = uploaded_file
                    input_data["prompt_strength"] = strength_val
                
                # 4. API 호출
                output = replicate.run(model_id, input=input_data)
                
                # 5. 결과 출력
                if output:
                    image_url = output[0]
                    st.success("완성!")
                    st.image(image_url, use_container_width=True)
                    
                    # 다운로드 버튼
                    st.download_button(
                        label="⬇️ 이미지 다운로드",
                        data=io.BytesIO(replicate.httpx.get(image_url).content),
                        file_name=f"kweb_{st.session_state.seed_value}.png",
                        mime="image/png"
                    )

        except replicate.exceptions.ReplicateError as e:
            st.error(f"Replicate API 오류: {e}")
            if "NSFW" in str(e):
                st.warning("모델의 기본 필터에 감지되었습니다. 프롬프트를 약간 수정해보세요.")
        except Exception as e:
            st.error(f"시스템 오류: {e}")