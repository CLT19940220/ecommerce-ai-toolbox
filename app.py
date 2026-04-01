import os
import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
from datetime import datetime

# 环境变量
API_KEY = os.getenv("API_KEY", "RMFLacjbNJG0LWikHzI5bOjQ")
SECRET_KEY = os.getenv("SECRET_KEY", "tpvlSDj5vFpDSbPrzl26jgrzUtXAllYg")

# 页面配置
st.set_page_config(
    page_title="AI Toolbox",
    page_icon="🛠️",
    layout="wide"
)

st.title("🛠️ E-commerce AI Toolbox")
st.subheader("Matting | White Background | Enhance | Expand")

# 获取百度 token
def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": SECRET_KEY
    }
    res = requests.post(url, params=params)
    return res.json().get("access_token")

# AI抠图
def ai_matting(image_bytes):
    token = get_access_token()
    url = f"https://aip.baidubce.com/rest/2.0/image-classify/v1/matting?access_token={token}"
    img_base64 = base64.b64encode(image_bytes).decode("utf-8")
    data = {"image": img_base64, "type": "2"}
    res = requests.post(url, data=data)
    if "foreground" in res.json():
        return Image.open(BytesIO(base64.b64decode(res.json()["foreground"]))).convert("RGBA")
    else:
        st.error("Matting failed")
        return None

# 换白底
def replace_bg(image_bytes):
    fg = ai_matting(image_bytes)
    if not fg: return None
    bg = Image.new("RGBA", fg.size, (255,255,255,255))
    return Image.alpha_composite(bg, fg).convert("RGB")

# 高清修复
def enhance(image_bytes):
    token = get_access_token()
    url = f"https://aip.baidubce.com/rest/2.0/image-process/v1/super_resolution?access_token={token}"
    data = {"image": base64.b64encode(image_bytes).decode("utf-8"), "scaling": 2}
    res = requests.post(url, data=data)
    if "image" in res.json():
        return Image.open(BytesIO(base64.b64decode(res.json()["image"])))

# 智能扩图
def expand(image_bytes):
    token = get_access_token()
    url = f"https://aip.baidubce.com/rest/2.0/image-process/v1/expand_image?access_token={token}"
    data = {"image": base64.b64encode(image_bytes).decode("utf-8"), "expand": 200}
    res = requests.post(url, data=data)
    if "image" in res.json():
        return Image.open(BytesIO(base64.b64decode(res.json()["image"])))

# 界面
uploaded = st.file_uploader("Upload Image", type=["jpg","png"])
if uploaded:
    b = uploaded.read()
    st.image(b, "Original")
    choice = st.selectbox("Choose Function", ["AI Matting", "White Background", "Enhance", "Expand"])
    if st.button("Start"):
        with st.spinner("Processing..."):
            if choice == "AI Matting":
                res = ai_matting(b)
            elif choice == "White Background":
                res = replace_bg(b)
            elif choice == "Enhance":
                res = enhance(b)
            else:
                res = expand(b)
            if res:
                st.image(res, "Result")
                buf = BytesIO()
                res.save(buf, format="JPEG", quality=95)
                st.download_button("Download", buf.getvalue(), "result.jpg")