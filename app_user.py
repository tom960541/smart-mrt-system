        # --- 階段 2：驗證 AI 結果 ---
        if response and response.text:
            match = re.search(r'\{.*\}', response.text.strip(), re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                s_id, e_id = data.get("start_id"), data.get("end_id")
                # 這次系統就能成功認出 AI 回傳的代碼了！
                if s_id in system.stations and e_id in system.stations:
                    return s_id, e_id, "成功 (來自 Gemini 雲端 AI)"

        # AI 失敗！拋出例外以觸發本地端備援機制
        raise Exception(f"API 無法服務 ({last_error})")

    except Exception as fallback_reason: 
        # ==========================================
        # 🚀 階段 3：本地端 NLP 備援機制 (Local Fallback)
        # ==========================================
        found_stations = []
        
        sorted_stations = sorted(system.stations.values(), key=lambda s: len(s.name), reverse=True)
        
        for st in sorted_stations:
            if st.name in user_text:
                found_stations.append((st.sid, user_text.find(st.name)))
        
        if len(found_stations) >= 2:
            found_stations.sort(key=lambda x: x[1])
            s_id = found_stations[0][0]
            e_id = found_stations[-1][0]
            return s_id, e_id, f"成功 (✨ 觸發系統本地端文字比對備援)"
            
        return None, None, f"AI 連線失敗且無法由文字比對出站點。原因：{str(fallback_reason)}"

def generate_speech_audio(start_name, end_name, fare):
    text = f"已為您規劃從{start_name}到{end_name}的路徑。總票價{fare}元。"
    tts = gTTS(text=text, lang='zh-tw')
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    return audio_fp

# ==========================================
# UI 介面
# ==========================================
def run():
    try: st.set_page_config(page_title="智慧捷運路徑規劃系統", layout="wide")
    except: pass

    st.title("🚆 智慧捷運路徑規劃系統 (2.0 Flash 雙引擎版)")

    selected_map = st.selectbox("🗺️ 選擇路網", list(MAP_DATABASE.keys()))
    config = MAP_DATABASE[selected_map]

    sys_data = load_json_data(config["json"])
    fare_data = load_json_data(config["fare_json"])
    mrt = TransitSystem(sys_data, fare_data, config["fare_func"])

    if not sys_data:
        st.error("地圖資料載入失敗")
        return

    names = mrt.get_all_display_names()
    if 'start_st' not in st.session_state: st.session_state.start_st = names[0]
    if 'end_st' not in st.session_state: st.session_state.end_st = names[0]
    if 'next_click_is_start' not in st.session_state: st.session_state.next_click_is_start = True
    if 'last_click' not in st.session_state: st.session_state.last_click = None

    col_ui, col_map = st.columns([1, 2.5])

    with col_ui:
        st.subheader("✨ AI 語音/文字助理")
        
        with st.form(key="ai_form"):
            user_input = st.text_input("你想去哪？", placeholder="例如：從高鐵站搭到愛河之心")
            submit_btn = st.form_submit_button("🤖 AI 規劃", use_container_width=True)
            
        if submit_btn:
            with st.spinner("AI 腦力激盪中..."):
                sid_s, sid_e, msg = get_stations_from_ai(user_input, mrt)
                
                if sid_s and sid_e:
                    st.session_state.start_st = mrt.get_station(sid_s).display_name
                    st.session_state.end_st = mrt.get_station(sid_e).display_name
                    st.success(f"✅ 解析成功！狀態：{msg}")
                    st.rerun() 
                else:
                    st.error(f"❌ 解析失敗：{msg}")

        # 🧹 已清理乾淨的 UI 區塊
        st.divider()
        idx_s = names.index(st.session_state.start_st) if st.session_state.start_st in names else 0
        idx_e = names.index(st.session_state.end_st) if st.session_state.end_st in names else 0

        sel_start = st.selectbox("出發站", names, index=idx_s)
        sel_end = st.selectbox("終點站", names, index=idx_e)

        st.session_state.start_st = sel_start
        st.session_state.end_st = sel_end

        search_mode = st.radio("⚙️ 選擇路徑規劃策略", ["最少站數 (BFS)", "最省票價 (Dijkstra)"], horizontal=True)

        if st.button("🔍 查詢路徑", type="primary", use_container_width=True):
            if sel_start == sel_end:
                st.warning("起終點相同")
            else:
                id_s, id_e = mrt.get_sid_by_name(sel_start), mrt.get_sid_by_name(sel_end)
                
                if "最少站數" in search_mode:
                    path = find_shortest_path(mrt, id_s, id_e)
                else:
                    path = find_cheapest_path(mrt, id_s, id_e)
                    
                if path:
                    fare, details = get_fare_and_details(mrt, path)
                    st.success(f"**系統報價：{fare} 元** | **總站數：{len(path)} 站**")
                    st.text_area("路徑詳情", details, height=130)
                    
                    path_display = " ➔ ".join([f"[{mrt.get_station(i).line_type}] {mrt.get_station(i).name}" for i in path])
                    st.info(f"建議路徑：\n{path_display}")
                    
                    audio = generate_speech_audio(sel_start, sel_end, fare)
                    st.audio(audio, format="audio/mp3", autoplay=True)
                else:
                    st.error("找不到相連路徑")

    with col_map:
        st.subheader("🗺️ 互動地圖")
        if st.session_state.next_click_is_start: st.info("👆 請在地圖點擊 **出發站**")
        else: st.warning("👆 請在地圖點擊 **終點站**")

        try:
            img = Image.open(config["img"])
            w_orig, h_orig = img.size

            TARGET_WIDTH = 450
            scale_ratio = TARGET_WIDTH / w_orig  

            click = streamlit_image_coordinates(
                img, 
                width=TARGET_WIDTH, 
                key="map_click"
            )

            if click:
                cx, cy = click["x"], click["y"]
                if st.session_state.last_click != (cx, cy):
                    st.session_state.last_click = (cx, cy)
                    closest, min_dist = None, float('inf')

                    for s in mrt.stations.values():
                        scaled_x = s.coords[0] * scale_ratio
                        scaled_y = s.coords[1] * scale_ratio

                        dist = math.sqrt((cx - scaled_x)**2 + (cy - scaled_y)**2)
                        if dist < min_dist: 
                            min_dist, closest = dist, s

                    threshold = 130 * scale_ratio

                    if closest and min_dist < threshold:
                        if st.session_state.next_click_is_start:
                            st.session_state.start_st = closest.display_name
                            st.session_state.next_click_is_start = False
                        else:
                            st.session_state.end_st = closest.display_name
                            st.session_state.next_click_is_start = True
                        st.rerun()
        except Exception as e:
            st.error(f"地圖元件錯誤: {e}")

    render_google_maps_widget(st.session_state.start_st, st.session_state.end_st, config)

if __name__ == "__main__":
    run()
