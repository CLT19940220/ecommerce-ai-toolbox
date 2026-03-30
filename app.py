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

# ---------------------- 页面配置 ----------------------
st.set_page_config(
    page_title="电商AI美工工具箱 - AI抠图|换白底|高清修复|智能扩图",
    page_icon="🛠️",
    layout="wide"
)

# ---------------------- 主界面 ----------------------
st.title("🛠️ 电商AI美工工具箱 · 主图一键搞定")
st.markdown("免费每日3次 | 会员无限次使用 | 无水印 | 高清下载")

# ---------------------- 功能代码 ----------------------
def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": SECRET_KEY
    }
    res = requests.post(url, params=params)
    return res.json().get("access_token")

def ai_matting(image_bytes):
    token = get_access_token()
    url = f"https://aip.baidubce.com/rest/2.0/image-classify/v1/matting?access_token={token}"
    img_base64 = base64.b64encode(image_bytes).decode("utf-8")
    data = {"image": img_base64, "type": "2"}
    res = requests.post(url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=data)
    if "foreground" in res.json():
        return Image.open(BytesIO(base64.b64decode(res.json()["foreground"]))).convert("RGBA")
    else:
        st.error(f"抠图失败：{res.json().get('error_msg')}")
        return None

def replace_background(image_bytes):
    fg_img = ai_matting(image_bytes)
    if not fg_img: return None
    bg = Image.new("RGBA", fg_img.size, (255,255,255,255))
    return Image.alpha_composite(bg, fg_img).convert("RGB")

def enhance_image(image_bytes):
    token = get_access_token()
    url = f"https://aip.baidubce.com/rest/2.0/image-process/v1/super_resolution?access_token={token}"
    img_base64 = base64.b64encode(image_bytes).decode("utf-8")
    data = {"image": img_base64, "scaling": 2}
    res = requests.post(url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=data)
    if "image" in res.json():
        return Image.open(BytesIO(base64.b64decode(res.json()["image"])))
    else:
        st.error(f"修复失败：{res.json().get('error_msg')}")
        return None

def expand_image(image_bytes):
    token = get_access_token()
    url = f"https://aip.baidubce.com/rest/2.0/image-process/v1/expand_image?access_token={token}"
    img_base64 = base64.b64encode(image_bytes).decode("utf-8")
    data = {"image": img_base64, "expand": 200, "fill_type": 1}
    res = requests.post(url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=data)
    if "image" in res.json():
        return Image.open(BytesIO(base64.b64decode(res.json()["image"])))
    else:
        st.error(f"扩图失败：{res.json().get('error_msg')}")
        return None

def image_to_bytes(img):
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf.getvalue()

# ---------------------- 按钮 ----------------------
col1, col2, col3, col4 = st.columns(4)
with col1: st.button("月卡 12元")
with col2: st.button("季卡 28元")
with col3: st.button("年卡 68元")
with col4: st.button("终身 168元")

# ---------------------- 上传 + 功能 ----------------------
uploaded = st.file_uploader("上传商品图", type=["jpg","png"])
if uploaded:
    img_bytes = uploaded.read()
    st.image(img_bytes, "原图")
    opt = st.selectbox("选择功能", ["AI抠图","AI换白底","高清修复","智能扩图"])
    if st.button("开始处理"):
        with st.spinner("处理中..."):
            if opt == "AI抠图":
                out = ai_matting(img_bytes)
            elif opt == "AI换白底":
                out = replace_background(img_bytes)
            elif opt == "高清修复":
                out = enhance_image(img_bytes)
            else:
                out = expand_image(img_bytes)
            
            if out:
                st.image(out, "处理完成")
                st.download_button("下载", image_to_bytes(out), "result.jpg")

# ---------------------- 底部 ----------------------
st.markdown("---")
st.markdown("© 2026 电商AI美工工具箱")

# ---------------------- VERCEL 必须入口 ----------------------
from http.server import BaseHTTPRequestHandler
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Ecommerce AI Toolbox Running")