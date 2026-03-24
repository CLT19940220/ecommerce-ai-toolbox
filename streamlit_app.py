# streamlit_app.py （Vercel 会自动识别 Streamlit）
import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
from datetime import datetime

# ======================
# 🔑 环境变量（Vercel 后台配置）
# ======================
API_KEY = st.secrets.get("API_KEY", "RMFLacjbNJG0LWikHzI5bOjQ")
SECRET_KEY = st.secrets.get("SECRET_KEY", "tpvlSDj5vFpDSbPrzl26jgrzUtXAllYg")

# 初始化页面
st.set_page_config(
    page_title="电商AI美工工具箱 - AI抠图|换白底|高清修复|智能扩图",
    page_icon="🛠️",
    layout="wide"
)
st.title("🛠️ 电商AI美工工具箱 · 主图一键搞定")
st.markdown("免费每日3次 | 会员无限次使用 | 无水印 | 高清下载")

# 用户限流（基于IP）
def get_user_ip():
    try:
        return st.session_state.get("user_ip", "unknown")
    except:
        return "unknown"

def track_usage():
    ip = get_user_ip()
    today = datetime.now().date()
    key = f"usage_{ip}_{today}"
    count = st.session_state.get(key, 0)
    return count

def increment_usage():
    ip = get_user_ip()
    today = datetime.now().date()
    key = f"usage_{ip}_{today}"
    st.session_state[key] = st.session_state.get(key, 0) + 1

# 百度API获取access_token
def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": SECRET_KEY
    }
    res = requests.post(url, params=params)
    return res.json().get("access_token")

# 4大核心功能实现
def ai_matting(image_bytes):
    token = get_access_token()
    url = f"https://aip.baidubce.com/rest/2.0/image-classify/v1/matting?access_token={token}"
    img_base64 = base64.b64encode(image_bytes).decode("utf-8")
    data = {"image": img_base64, "type": "2"}
    res = requests.post(url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=data)
    if "foreground" in res.json():
        return Image.open(BytesIO(base64.b64decode(res.json()["foreground"]))).convert("RGBA")
    else:
        st.error(f"抠图失败：{res.json().get('error_msg', '未知错误')}")
        return None

def replace_background(image_bytes, bg_color=(255, 255, 255, 255)):
    fg_img = ai_matting(image_bytes)
    if not fg_img:
        return None
    bg_img = Image.new("RGBA", fg_img.size, bg_color)
    composite = Image.alpha_composite(bg_img, fg_img)
    return composite.convert("RGB")

def enhance_image(image_bytes):
    token = get_access_token()
    url = f"https://aip.baidubce.com/rest/2.0/image-process/v1/super_resolution?access_token={token}"
    img_base64 = base64.b64encode(image_bytes).decode("utf-8")
    data = {"image": img_base64, "scaling": 2}
    res = requests.post(url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=data)
    if "image" in res.json():
        return Image.open(BytesIO(base64.b64decode(res.json()["image"])))
    else:
        st.error(f"高清修复失败：{res.json().get('error_msg', '未知错误')}")
        return None

def expand_image(image_bytes, expand_pixels=100):
    token = get_access_token()
    url = f"https://aip.baidubce.com/rest/2.0/image-process/v1/expand_image?access_token={token}"
    img_base64 = base64.b64encode(image_bytes).decode("utf-8")
    data = {"image": img_base64, "expand": expand_pixels, "fill_type": 1}
    res = requests.post(url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=data)
    if "image" in res.json():
        return Image.open(BytesIO(base64.b64decode(res.json()["image"])))
    else:
        st.error(f"智能扩图失败：{res.json().get('error_msg', '未知错误')}")
        return None

# 图片处理与下载
def image_to_bytes(img, format="JPEG"):
    buf = BytesIO()
    img.save(buf, format=format, quality=95)
    buf.seek(0)
    return buf.getvalue()

# 会员购买按钮
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("月卡 12元"):
        st.info("购买链接（待对接支付）")
with col2:
    if st.button("季卡 28元"):
        st.info("购买链接（待对接支付）")
with col3:
    if st.button("年卡 68元"):
        st.info("购买链接（待对接支付）")
with col4:
    if st.button("终身 168元"):
        st.info("购买链接（待对接支付）")

# 功能选择区
uploaded_file = st.file_uploader("上传商品图（JPG/PNG，≤4MB）", type=["jpg", "jpeg", "png"])
if uploaded_file:
    image_bytes = uploaded_file.read()
    st.image(image_bytes, caption="原图预览", use_column_width=True)

    option = st.selectbox("选择功能", ["AI商品抠图", "AI换白底", "AI图片高清修复", "AI智能扩图"])
    process_btn = st.button("开始处理")

    if process_btn:
        usage_count = track_usage()
        if usage_count >= 3:
            st.warning("今日免费次数已用完，请购买会员解锁无限次使用")
        else:
            increment_usage()
            with st.spinner("AI处理中..."):
                try:
                    if option == "AI商品抠图":
                        result_img = ai_matting(image_bytes)
                    elif option == "AI换白底":
                        result_img = replace_background(image_bytes)
                    elif option == "AI图片高清修复":
                        result_img = enhance_image(image_bytes)
                    elif option == "AI智能扩图":
                        result_img = expand_image(image_bytes, expand_pixels=200)

                    if result_img:
                        st.image(result_img, caption="处理结果", use_column_width=True)
                        result_bytes = image_to_bytes(result_img)
                        st.download_button("下载图片", result_bytes, "result.jpg", "image/jpeg")
                except Exception as e:
                    st.error(f"处理失败：{str(e)}")
else:
    st.info("请上传图片开始处理")

# 底部信息
st.markdown("---")
st.markdown("© 2026 电商AI美工工具箱 | 专为淘宝/拼多多/抖音小店主图设计")