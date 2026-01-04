import streamlit as st
import graphviz
from supabase import create_client

# --- 1. CẤU HÌNH KẾT NỐI (Lấy từ Secrets) ---
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except:
    st.error("Chưa cấu hình Secrets trên Streamlit Cloud!")
    st.stop()

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

# --- 2. GIAO DIỆN WEB ---
st.set_page_config(page_title="Gia Phả Dòng Họ Lê", layout="wide", page_icon="zk")

# CSS tùy chỉnh để làm đẹp giao diện Streamlit (ẩn bớt viền thừa, font chữ to rõ)
st.markdown("""
<style>
    .stApp {
        background-color: #f5f5f5; /* Màu nền xám nhẹ dịu mắt */
    }
    h1 {
        color: #8B0000; /* Màu đỏ mận truyền thống */
        text-align: center;
        font-family: 'Times New Roman', serif;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🔍 Tra cứu thành viên")
    search_name = st.text_input("Nhập tên:", placeholder="Ví dụ: Lê Văn...")
    st.info("💡 **Mẹo:**\n- Dùng chuột lăn để phóng to/thu nhỏ.\n- Bấm giữ chuột trái để kéo di chuyển cây.")

# Tiêu đề chính
st.title("GIA PHẢ DÒNG HỌ LÊ - CHI LỘC")
st.markdown("<p style='text-align: center; color: gray;'>Cây gia phả hiển thị theo ngôi thứ từ trên xuống dưới</p>", unsafe_allow_html=True)

# Lấy dữ liệu
response = supabase.table("members").select("*").execute()
members = response.data

if not members:
    st.warning("Đang tải dữ liệu hoặc chưa có thành viên nào...")
else:
    # --- 3. VẼ CÂY GIA PHẢ (Phong cách Truyền thống & Hiện đại) ---
    
    # rankdir='TB': Top to Bottom (Trên xuống Dưới) - Chuẩn truyền thống
    # splines='ortho': Đường kẻ vuông góc (Giống sơ đồ trong ảnh bạn gửi)
    graph = graphviz.Digraph(format='svg')
    graph.attr(rankdir='TB', splines='ortho')
    
    # Tăng khoảng cách để cây không bị dính chùm
    graph.attr(nodesep='0.5', ranksep='0.8')
    
    # Cấu hình chung cho Ô Tên (Node)
    # shape='box': Hình hộp chữ nhật (giống ảnh cũ)
    # style='filled,rounded': Tô màu nền và bo tròn góc (nét hiện đại)
    graph.attr('node', shape='box', style='filled,rounded', 
               fontname='Arial', fontsize='13', penwidth='1.5')
    
    # Cấu hình đường nối (Edge) - Màu xám đậm cho trang trọng
    graph.attr('edge', color='#444444', arrowsize='0.6', penwidth='1.2')

    for member in members:
        # --- PHÂN MÀU THEO THẾ HỆ (Để dễ nhìn ngôi thứ) ---
        gen = member['generation']
        
        # Mặc định
        fill_color = '#ffffff' 
        font_color = 'black'
        border_color = 'black'
        
        # Logic màu sắc (Mô phỏng bảng màu phong thủy/truyền thống)
        if gen == 1: 
            fill_color = '#FFD700' # Vàng kim (Thủy tổ)
            border_color = '#B8860B'
        elif gen == 2: 
            fill_color = '#FFDEAD' # Màu da người/Cam nhạt
        elif gen is not None and gen < 15: 
            fill_color = '#F0F8FF' # Xanh nhạt (Các cụ xưa)
        else: 
            fill_color = '#FFFFFF' # Trắng (Đời nay cho sạch sẽ)
            border_color = '#2E8B57' # Viền xanh lá cây (như nhánh Lộc Chi trong ảnh)

        # Highlight khi tìm kiếm (Đổi sang màu Đỏ Đậm)
        if search_name and search_name.lower() in member['full_name'].lower():
            fill_color = '#DC143C' # Đỏ thắm
            font_color = 'white'
            border_color = '#8B0000'

        # Nội dung hiển thị (Tên + Đời in nhỏ)
        # Sử dụng HTML label để format chữ đẹp hơn
        label = f'<{member["full_name"]}<BR/><FONT POINT-SIZE="10" COLOR="#555555">Đời thứ {gen}</FONT>>'
        
        graph.node(str(member['id']), label=label, 
                   fillcolor=fill_color, fontcolor=font_color, color=border_color)

        # Vẽ đường nối
        if member['father_id']:
            graph.edge(str(member['father_id']), str(member['id']))

    # Hiển thị biểu đồ
    st.graphviz_chart(graph, use_container_width=True)

    # Bảng dữ liệu (để ẩn cho gọn, ai cần mới mở)
    with st.expander("📖 Xem danh sách chi tiết"):
        st.dataframe(members)
