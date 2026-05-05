import streamlit as st
import app_user  
import app_dev   

# 全局網頁設定 (必須放在最前面)
st.set_page_config(page_title="智慧捷運路徑規劃", layout="wide")

# 初始化 Session State
if 'current_mode' not in st.session_state: 
    st.session_state.current_mode = "home"
if 'is_authenticated' not in st.session_state: 
    st.session_state.is_authenticated = False

DEV_PASSWORD = "admin" # 開發者密碼

# 路由控制
if st.session_state.current_mode == "home":
    st.title("🏢 系統入口大廳")
    st.write("請選擇您的身份以進入系統：")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧑‍💻 我是使用者 (進入捷運系統)", use_container_width=True):
            st.session_state.current_mode = "user"
            st.rerun()
    with col2:
        if st.button("⚙️ 我是開發者 (進入後台管理)", use_container_width=True):
            st.session_state.current_mode = "dev_login"
            st.rerun()

elif st.session_state.current_mode == "user":
    app_user.run() 
    st.sidebar.divider()
    if st.sidebar.button("🚪 返回入口大廳"):
        st.session_state.current_mode = "home"
        st.rerun()

elif st.session_state.current_mode == "dev_login":
    st.title("🔒 開發者權限驗證")
    pwd_input = st.text_input("請輸入密碼：", type="password")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("登入"):
            if pwd_input == DEV_PASSWORD:
                st.session_state.is_authenticated = True
                st.session_state.current_mode = "dev_dashboard"
                st.rerun()
            else:
                st.error("密碼錯誤！")
    with col2:
        if st.button("取消"):
            st.session_state.current_mode = "home"
            st.rerun()

elif st.session_state.current_mode == "dev_dashboard" and st.session_state.is_authenticated:
    app_dev.run() 
    st.sidebar.divider()
    if st.sidebar.button("登出系統 (Log Out)"):
        st.session_state.current_mode = "home"
        st.session_state.is_authenticated = False
        st.rerun()