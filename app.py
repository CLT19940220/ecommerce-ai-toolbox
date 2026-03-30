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

# ---------------------- 页面 ----------------------
st.set_page_config(
    page_title="电商AI美工工具箱",
    page_icon="🛠️",
    layout="wide"
)

st.title("🛠️ 电商AI美工工具箱")
st.subheader("AI抠图｜换白底｜高清修复｜智能扩图")

# ---------------------- 功能 ----------------------
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
        st.error("抠图失败")
        return None

def replace_bg(image_bytes):
    fg = ai_matting(image_bytes)
    if not fg: return None
    bg = Image.new("RGBA", fg.size, (255,255,255,255))
    return Image.alpha_composite(bg, fg).convert("RGB")

def enhance(image_bytes):
    token = get_access_token()
    url = f"https://aip.baidubce.com/rest/2.0/image-process/v1/super_resolution?access_token={token}"
    data = {"image": base64.b64encode(image_bytes).decode("utf-8"), "scaling": 2}
    res = requests.post(url, data=data)
    if "image" in res.json():
        return Image.open(BytesIO(base64.b64decode(res.json()["image"])))
    else:
        st.error("修复失败")

def expand(image_bytes):
    token = get_access_token()
    url = f"https://aip.baidubce.com/rest/2.0/image-process/v1/expand_image?access_token={token}"
    data = {"image": base64.b64encode(image_bytes).decode("utf-8"), "expand": 200}
    res = requests.post(url, data=data)
    if "image" in res.json():
        return Image.open(BytesIO(base64.b64decode(res.json()["image"])))

# ---------------------- 界面 ----------------------
uploaded = st.file_uploader("上传图片", type=["jpg","png"])
if uploaded:
    b = uploaded.read()
    st.image(b, "原图")
    choice = st.selectbox("选择功能", ["AI抠图", "换白底", "高清修复", "智能扩图"])
    if st.button("开始处理"):
        with st.spinner("处理中..."):
            if choice == "AI抠图":
                res = ai_matting(b)
            elif choice == "换白底":
                res = replace_bg(b)
            elif choice == "高清修复":
                res = enhance(b)
            else:
                res = expand(b)
            if res:
                st.image(res, "完成")
                buf = BytesIO()
                res.save(buf, format="JPEG", quality=95)
                st.download_button("下载", buf.getvalue(), "result.jpg")

# ---------------------- 【重要】VERCEL 运行入口 ----------------------
# 下面这段代码 不能删！删了就报错！
from http.server import BaseHTTPRequestHandler
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type','text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'正在启动 Streamlit 应用，请稍候...\n如果长时间未打开，说明 Vercel 不支持 Streamlit 运行模式。')
        return