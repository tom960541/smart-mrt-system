import streamlit as st
import json

def run():
    st.title("🔧 系統後台管理與資料庫監控")
    st.warning("⚠️ 您目前處於開發者模式。")
    
    st.subheader("📂 捷運路線與票價資料庫狀態")
    
    target_file = st.selectbox("選擇要檢查的地圖資料：", 
        ["krt_data.json", "tpi_data.json", "krt_real_fare.json", "tpi_real_fare.json"])
    
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        st.success(f"成功讀取 {target_file}，共包含 {len(data)} 筆主鍵資料。")
        with st.expander("點此展開檢視原始 JSON 節點資料"):
            st.json(data)
            
    except FileNotFoundError:
        st.error(f"找不到檔案 {target_file}，請確認檔案存在。")
        
    st.divider()
    st.info("💡 提示：本區塊為系統展示。若需更新官方票價，請於本地端執行 update_tdx_fare.py 爬蟲腳本後，再推送至伺服器。")