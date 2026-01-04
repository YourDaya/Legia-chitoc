import streamlit as st
import graphviz
from supabase import create_client

# --- 1. KẾT NỐI SUPABASE ---
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except:
    st.error("Chưa cấu hình Secrets!")
    st.stop()

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

# --- 2. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Gia Phả Lê Tộc", layout="wide", page_icon="📜")

st.markdown("""
<style>
    .stApp { background-color: #fdfcf0; }
    h1 { color: #800000; font-family: 'Times New Roman'; text-align: center; }
    svg a text { text-decoration: none !important; }
    
    /* CSS cho khung thời gian (Timeline Badge) */
    .timeline-badge {
        background-color: #e8eaf6;
        color: #1a237e;
        padding: 8px 15px;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 15px;
        border: 1px solid #c5cae9;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HÀM XỬ LÝ NGÀY THÁNG THÔNG MINH ---
def format_lifespan(dob, dod):
    # Trường hợp 1: Không có dữ liệu
    if not dob and not dod:
        return "Năm sinh/mất: Đang cập nhật..."
    
    start = dob if dob else "?"
    
    # Trường hợp 2: Đã mất (Có ngày mất)
    if dod:
        return f"🗓 {start} — {dod} (Đã tạ thế ⚱️)"
    
    # Trường hợp 3: Còn sống (Không có ngày mất)
    else:
        return f"🌱 Sinh năm {start} — Nay (Còn sống)"

# --- 4. POPUP CHI TIẾT ---
@st.dialog("HỒ SƠ THÀNH VIÊN", width="large")
def show_popup(member_id, all_members):
    member = next((m for m in all_members if str(m['id']) == str(member_id)), None)
    
    if member:
        father_name = "Không rõ (Thủy tổ)"
        if member['father_id']:
            father = next((m for m in all_members if m['id'] == member['father_id']), None)
            if father: father_name = father['full_name']

        # Xử lý dòng thời gian
        timeline_str = format_lifespan(member.get('dob_lunar'), member.get('dod_lunar'))

        col_img, col_info = st.columns([1, 2], gap="medium")
        
        with col_img:
            st.write("") 
            if member.get('avatar_url'):
                st.image(member.get('avatar_url'), use_column_width=True)
            else:
                st.markdown("""
                <div style="background-color: #eee; border-radius: 10px; padding: 40px; text-align: center;">
                    <h1 style="font-size: 60px; margin: 0;">👤</h1>
                </div>
                """, unsafe_allow_html=True)

        with col_info:
            # Tên thành viên to rõ
            st.markdown(f"<h2 style='margin-top:0; color:#B22222;'>{member['full_name']}</h2>", unsafe_allow_html=True)
            
            # Dòng thời gian nổi bật (Đã tối ưu vào đây)
            st.markdown(f"<div class='timeline-badge'>{timeline_str}</div>", unsafe_allow_html=True)
            
            # Thông tin hành chính
            st.write(f"🏆 **Đời thứ:** {member['generation']}")
            st.write(f"👴 **Con ông:** {father_name}")
            
            if member.get('note'):
                st.info(f"📌 {member.get('note')}")

        st.divider()
        
        # Tabs nội dung
        tab1, tab2 = st.tabs(["📜 **TIỂU SỬ CHI TIẾT**", "🏆 **VINH DANH**"])
        
        with tab1:
            if member.get('biography'):
                st.write(member['biography'])
            else:
                st.markdown("<em>Chưa có dữ liệu tiểu sử.</em>", unsafe_allow_html=True)
                
        with tab2:
            if member.get('achievements'):
                st.success(member['achievements'])
            else:
                st.markdown("<em>Chưa có ghi nhận thành tích.</em>", unsafe_allow_html=True)
        
        if st.button("Đóng hồ sơ", use_container_width=True):
            st.rerun()

# --- 5. LOGIC CHÍNH ---
response = supabase.table("members").select("*").execute()
members = response.data

# Bắt sự kiện click ID từ URL
if "id" in st.query_params:
    show_popup(st.query_params["id"], members)

# Vẽ cây
st.title("GIA PHẢ DÒNG HỌ LÊ - CHI LỘC")
st.caption("💡 Bấm vào ô tên để xem chi tiết.")

if members:
    graph = graphviz.Digraph(format='svg')
    graph.attr(rankdir='TB', splines='ortho', nodesep='0.2', ranksep='0.5')
    graph.attr('node', shape='rect', style='filled,bold', fontname='Times-Bold', fontsize='11', penwidth='1')
    graph.attr('edge', color='black', arrowsize='0.5', penwidth='0.8')

    for member in members:
        gen = member['generation']
        fill_color = '#ffffff'; font_color = 'black'
        if gen and gen <= 17: fill_color = '#483D8B'; font_color = 'white'
        elif gen == 18: fill_color = '#FFD700'; font_color = 'black'
        elif gen == 19: fill_color = '#2E8B57'; font_color = 'white'
        elif gen == 20: fill_color = '#B22222'; font_color = 'white'
        elif gen >= 21: fill_color = '#FFFACD'; font_color = 'black'

        node_url = f"?id={member['id']}"
        
        # Nhãn hiển thị đơn giản trên cây
        label = f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0">
            <TR><TD><B>{member['full_name']}</B></TD></TR>
            <TR><TD><FONT POINT-SIZE="9">Đời {gen}</FONT></TD></TR>
        </TABLE>>'''

        graph.node(str(member['id']), label=label, fillcolor=fill_color, fontcolor=font_color, URL=node_url, target="_self")

        if member['father_id']:
            graph.edge(str(member['father_id']), str(member['id']))

    st.graphviz_chart(graph, use_container_width=True)
else:
    st.info("Đang tải dữ liệu...")
