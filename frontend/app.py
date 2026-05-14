# pyrefly: ignore [missing-import]
import streamlit as st
import base64
from backend.database import SessionLocal, User, Reservation
from backend import services
from frontend import ui_pages

st.set_page_config(page_title="Absolute Cinema", page_icon="assets/tab-transparent.png", layout="wide")

# Custom CSS for premium aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Headers */
    h1, h2, h3, h4 {
        color: #F8F9FA !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    
    /* Top banner */
    .main-header {
        text-align: center;
        padding: 0;
        background-color: #161B22;
        border-bottom: 1px solid #30363D;
        margin-bottom: 32px;
    }
    
    .main-header h1 {
        font-weight: 700 !important;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    
    /* Hide Streamlit Deploy Button and Toolbar */
    .stDeployButton, [data-testid="stToolbar"], [data-testid="stHeader"] {
        display: none !important;
    }
    
    header {
        visibility: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None
if "reservation_id" not in st.session_state:
    st.session_state.reservation_id = None

db = SessionLocal()

try:
    # Handle Stripe redirect or Browser Back Button navigation
    if "res_id" in st.query_params:
        res_id = st.query_params.get("res_id")
        status = st.query_params.get("status")
        
        if res_id:
            # Restore the user's session
            reservation = db.query(Reservation).filter(Reservation.id == int(res_id)).first()
            if reservation:
                st.session_state.user_id = reservation.user_id
            
            if status == "success":
                if services.confirm_payment(db, res_id):
                    st.success("Payment Successful! Seat Confirmed.")
                st.query_params.clear()
                st.session_state.reservation_id = None
                st.session_state.current_page = "Home"
            elif status == "cancel":
                st.warning("Payment cancelled. Your seat is still reserved for a few minutes.")
                st.query_params.clear()
                st.session_state.reservation_id = int(res_id)
                st.session_state.current_page = "Checkout"
            else:
                # Returned via browser back button directly to checkout URL
                st.session_state.reservation_id = int(res_id)
                st.session_state.current_page = "Checkout"

    def get_current_user():
        if st.session_state.user_id:
            return db.query(User).filter(User.id == st.session_state.user_id).first()
        return None

    user = get_current_user()

    # Custom navigation control
    def go_to_page(page_name):
        st.session_state.current_page = page_name
        if "res_id" in st.query_params:
            st.query_params.clear()
        st.rerun()

    # --- Navigation & Header ---
    def get_base64_of_bin_file(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
        
    try:
        logo_b64 = get_base64_of_bin_file("assets/AC-logo-c.jpg")
        header_html = f'<div class="main-header"><img src="data:image/jpeg;base64,{logo_b64}" style="max-width: 230px; height: auto; margin: 10px 0; mix-blend-mode: screen; filter: invert(1); object-fit: contain;" /></div>'
    except FileNotFoundError:
        header_html = '<div class="main-header"><h1>Absolute Cinema</h1></div>'
        
    st.markdown(header_html, unsafe_allow_html=True)

    nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns(5)

    with nav_col1:
        if st.button("Home", key="nav_home", use_container_width=True):
            go_to_page("Home")

    if user:
        with nav_col2:
            if st.button("Logout", key="nav_logout", use_container_width=True):
                st.session_state.user_id = None
                st.session_state.current_page = "Home"
                st.rerun()
        if user.is_admin:
            with nav_col3:
                if st.button("Admin Dashboard", key="nav_admin", use_container_width=True):
                    go_to_page("Admin Dashboard")
        with nav_col4:
            if st.button("My Bookings", key="nav_bookings", use_container_width=True):
                go_to_page("My Bookings")
    else:
        with nav_col2:
            if st.button("Login", key="nav_login", use_container_width=True):
                go_to_page("Login")
        with nav_col3:
            if st.button("Register", key="nav_register", use_container_width=True):
                go_to_page("Register")

    st.write("---")
    if user:
        st.write(f"**Logged in as:** {user.username}")

    page = st.session_state.current_page

    # --- Page Routing ---
    if "token" in st.query_params:
        token = st.query_params.get("token")
        ui_pages.render_reset_password(db, go_to_page, token)
    elif page == "Home":
        ui_pages.render_home(db, go_to_page)
    elif page == "Login":
        ui_pages.render_login(db, go_to_page)
    elif page == "Register":
        ui_pages.render_register(db, go_to_page)
    elif page == "Forgot Password":
        ui_pages.render_forgot_password(db, go_to_page)
    elif page == "Movie Details":
        ui_pages.render_movie_details(db, go_to_page, user)
    elif page == "Checkout":
        ui_pages.render_checkout(db, go_to_page, user)
    elif page == "Admin Dashboard":
        ui_pages.render_admin(db, user)
    elif page == "My Bookings":
        ui_pages.render_my_bookings(db, user)

finally:
    db.close()
