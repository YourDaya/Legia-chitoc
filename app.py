import streamlit as st
import graphviz
from supabase import create_client

# --- 1. KẾT NỐI (Giữ nguyên) ---
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

# CSS để ẩn bớt khoảng trắng thừa, tối ưu cho màn hình ngang
st.markdown("""
<style>
    .stApp { background-color: #fdfcf0; } /* Màu nền giấy cũ */
    h1 { color: #800000; font-family: 'Times New Roman'; text-align: center; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🔍 Tìm kiếm")
    search_name = st.text_input("Nhập tên thành viên:", placeholder="Ví dụ: Lê Văn...")
    st.divider()
    st.write("Dữ liệu lấy từ nhánh: **Lộc Chi**")

st.title("GIA PHẢ DÒNG HỌ LÊ - CHI LỘC")

# --- 3. XỬ LÝ DỮ LIỆU ---
response = supabase.table("members").select("*").execute()
members = response.data

if members:
    # --- 4. VẼ CÂY PHONG CÁCH TRUYỀN THỐNG ---
    # splines='ortho': Bắt buộc đường kẻ vuông góc
    # nodesep, ranksep: Chỉnh khoảng cách để cây gọn hơn
    graph = graphviz.Digraph(format='svg')
    graph.attr(rankdir='TB', splines='ortho', nodesep='0.2', ranksep='0.5')
    
    # Cấu hình chung cho Node (Ô tên)
    # shape='rect': Hình chữ nhật
    # fontname: Font có chân cho trang trọng
    graph.attr('node', shape='rect', style='filled,bold', 
               fontname='Times-Bold', fontsize='11', penwidth='1')
    
    # Cấu hình đường nối (Màu đen, mảnh)
    graph.attr('edge', color='black', arrowsize='0.5', penwidth='0.8')

    for member in members:
        gen = member['generation']
        full_name = member['full_name']
        
        # --- LOGIC MÀU SẮC (Mô phỏng ảnh gia phả mẫu) ---
        # Mặc định (Trắng)
        fill_color = '#ffffff'
        font_color = 'black'
        
        # Đời 15, 16, 17 (Cụ Luật, Dư, Minh...) -> Màu Tím/Xanh đậm (như ảnh)
        if gen and gen <= 17:
            fill_color = '#483D8B' # Dark Slate Blue
            font_color = 'white'
            
        # Đời 18 (Cụ Kiệm, Cần...) -> Màu Vàng/Cam
        elif gen == 18:
            fill_color = '#FFD700' # Gold
            font_color = 'black'
            
        # Đời 19 (Cụ Khuyên...) -> Màu Xanh lá
        elif gen == 19:
            fill_color = '#2E8B57' # Sea Green
            font_color = 'white'
            
        # Đời 20 (Cụ Làng, Miên...) -> Màu Đỏ (Các ô dọc trong ảnh)
        elif gen == 20:
            fill_color = '#B22222' # Firebrick
            font_color = 'white'
            
        # Đời 21 trở đi -> Màu vàng nhạt hoặc trắng
        elif gen >= 21:
            fill_color = '#FFFACD' # Lemon Chiffon
            font_color = 'black'

        # Nếu đang tìm kiếm -> Tô màu hồng đậm để nổi bật
        if search_name and search_name.lower() in full_name.lower():
            fill_color = '#FF1493'
            font_color = 'white'

        # --- TẠO NHÃN (LABEL) ---
        # Dùng HTML để ngắt dòng đẹp hơn
        label = f'''<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0">
            <TR><TD><B>{full_name}</B></TD></TR>
            <TR><TD><FONT POINT-SIZE="9">Đời {gen}</FONT></TD></TR>
        </TABLE>
        >'''

        graph.node(str(member['id']), label=label, 
                   fillcolor=fill_color, fontcolor=font_color)

        # Vẽ đường nối
        if member['father_id']:
            graph.edge(str(member['father_id']), str(member['id']))

    # Hiển thị
    st.graphviz_chart(graph, use_container_width=True)
    
    with st.expander("📄 Xem danh sách dạng bảng"):
        st.dataframe(members)

else:
    st.info("Đang tải dữ liệu...")
