import streamlit as st

# 全局網頁設定 (必須放在最前面)
st.set_page_config(page_title="智慧捷運路徑規劃", layout="wide")

import app_user
import app_dev
from ui_theme import apply_app_theme, render_header

apply_app_theme()

# 初始化 Session State
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "home"
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False


def get_dev_password():
    try:
        return st.secrets.get("DEV_PASSWORD", "admin")
    except Exception:
        return "admin"


# 路由控制
if st.session_state.current_mode == "home":
    render_header(
        "TRANSIT OPERATIONS",
        "智慧捷運路徑規劃",
        "選擇使用者查詢或資料後台。系統支援台北與高雄捷運路網、票價資料、AI 文字解析與互動地圖選站。",
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class="choice-card">
                <strong>乘客路線查詢</strong>
                <span>使用 AI 文字、下拉選單或地圖點擊選站，取得路線、票價、站數與 Google Maps 輔助。</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("進入路線查詢", type="primary", use_container_width=True):
            st.session_state.current_mode = "user"
            st.rerun()

    with col2:
        st.markdown(
            """
            <div class="choice-card">
                <strong>資料後台監控</strong>
                <span>檢查路網 JSON 與票價矩陣載入狀態，快速確認資料庫內容與筆數。</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("進入資料後台", use_container_width=True):
            st.session_state.current_mode = "dev_login"
            st.rerun()

elif st.session_state.current_mode == "user":
    app_user.run()
    st.sidebar.divider()
    if st.sidebar.button("返回入口大廳"):
        st.session_state.current_mode = "home"
        st.rerun()

elif st.session_state.current_mode == "dev_login":
    render_header(
        "ADMIN ACCESS",
        "開發者權限驗證",
        "後台提供資料檔讀取狀態與 JSON 檢視。正式部署時請在 Streamlit secrets 設定 DEV_PASSWORD。",
    )
    pwd_input = st.text_input("開發者密碼", type="password")

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("登入"):
            if pwd_input == get_dev_password():
                st.session_state.is_authenticated = True
                st.session_state.current_mode = "dev_dashboard"
                st.rerun()
            else:
                st.error("密碼錯誤，請重新輸入。")

    with col2:
        if st.button("取消"):
            st.session_state.current_mode = "home"
            st.rerun()

elif st.session_state.current_mode == "dev_dashboard" and st.session_state.is_authenticated:
    app_dev.run()
    st.sidebar.divider()
    if st.sidebar.button("登出系統"):
        st.session_state.current_mode = "home"
        st.session_state.is_authenticated = False
        st.rerun()
