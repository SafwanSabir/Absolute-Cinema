import streamlit as st
from datetime import datetime, timedelta, timezone
import streamlit.components.v1 as components
import api_client

def render_home(go_to_page):
    st.header("Now Showing")
    movies = api_client.get_upcoming_movies()
    
    if not movies:
        st.info("No upcoming movies at the moment.")
    else:
        for movie in movies:
            with st.container(border=True):
                m_col1, m_col2 = st.columns([3, 1])
                with m_col1:
                    st.subheader(movie["name"])
                    # Parse ISO format datetime returned by FastAPI
                    start_time = datetime.fromisoformat(movie["start_time"])
                    st.write(f"**Starts at:** {start_time.strftime('%Y-%m-%d %H:%M UTC')}")
                    st.write(f"**Duration:** {movie['duration_minutes']} mins")
                with m_col2:
                    st.write("") # Spacing
                    if st.button("Book Seats", key=f"book_{movie['id']}", use_container_width=True):
                        st.session_state.selected_movie = movie["id"]
                        go_to_page("Movie Details")

def render_login(go_to_page):
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            st.write("") # Spacing
            if st.button("Login", key="action_login", use_container_width=True):
                data = api_client.login(username, password)
                if data and "access_token" in data:
                    st.session_state.token = data["access_token"]
                    st.success("Logged in successfully!")
                    go_to_page("Home")
                else:
                    st.error("Invalid username or password")
            
            st.write("---")
            if st.button("Forgot Password?", key="goto_forgot", use_container_width=True):
                go_to_page("Forgot Password")
            
            st.write("")
            if st.button("Don't have an account? Register", key="goto_register", use_container_width=True):
                go_to_page("Register")

def render_register(go_to_page):
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center;'>Register</h2>", unsafe_allow_html=True)
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            st.write("") # Spacing
            if st.button("Register", key="action_register", use_container_width=True):
                success = api_client.register(username, email, password)
                if not success:
                    st.error("Username or email already exists")
                else:
                    st.success("Registered successfully! Please login.")
                    go_to_page("Login")
            
            st.write("---")
            if st.button("Already have an account? Login", key="goto_login", use_container_width=True):
                go_to_page("Login")

def render_forgot_password(go_to_page):
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center;'>Forgot Password</h2>", unsafe_allow_html=True)
            email = st.text_input("Enter your registered email")
            
            if st.button("Send Reset Link", key="action_send_reset", use_container_width=True):
                if api_client.request_password_reset(email):
                    st.success("If your email is registered, a reset link has been sent!")
                else:
                    st.error("Failed to send reset link. Please try again later.")
            
            st.write("---")
            if st.button("Back to Login", key="back_to_login", use_container_width=True):
                go_to_page("Login")

def render_reset_password(go_to_page, token):
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center;'>Reset Password</h2>", unsafe_allow_html=True)
            
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.button("Update Password", key="action_update_pwd", use_container_width=True):
                if new_password != confirm_password:
                    st.error("Passwords do not match!")
                elif len(new_password) < 4:
                    st.error("Password too short.")
                else:
                    if api_client.reset_password(token, new_password):
                        st.success("Password updated successfully! Please login.")
                        st.query_params.clear()
                        go_to_page("Login")
                    else:
                        st.error("Error resetting password. Token may be invalid or expired.")

def render_movie_details(go_to_page, user):
    if not st.session_state.selected_movie:
        go_to_page("Home")
        return
    
    movie = api_client.get_movie_details(st.session_state.selected_movie)
    if not movie:
        st.error("Movie not found")
        go_to_page("Home")
        return
    
    start_time = datetime.fromisoformat(movie["start_time"])
    st.header(f"Book Seats for {movie['name']}")
    st.write(f"Starts at: {start_time.strftime('%Y-%m-%d %H:%M UTC')} | Duration: {movie['duration_minutes']} mins")
    
    st.subheader("Available Seats")
    seats = api_client.get_all_seats()
    
    rows = {}
    for seat in seats:
        if seat["row"] not in rows:
            rows[seat["row"]] = []
        rows[seat["row"]].append(seat)
        
    for r, row_seats in rows.items():
        st.write(f"**Row {r}**")
        cols = st.columns(len(row_seats))
        for idx, seat in enumerate(row_seats):
            with cols[idx]:
                is_available = api_client.is_seat_available(movie["id"], seat["id"])
                price = 15.0 if seat["is_corner"] else 10.0
                
                if is_available:
                    if st.button(f"{seat['row']}{seat['number']} (${price})", key=f"seat_{seat['id']}"):
                        if not user:
                            st.warning("Please login to book a seat.")
                            st.session_state.current_page = "Login"
                            st.rerun()
                        else:
                            res = api_client.book_seat_pending(movie["id"], seat["id"])
                            if res:
                                st.session_state.reservation_id = res["id"]
                                go_to_page("Checkout")
                            else:
                                st.error("Failed to book seat.")
                else:
                    st.button(f"{seat['row']}{seat['number']} (Taken)", key=f"seat_{seat['id']}", disabled=True)
    
    if st.button("Back to Movies"):
        go_to_page("Home")

def render_checkout(go_to_page, user):
    if not st.session_state.reservation_id:
        go_to_page("Home")
        return
        
    reservation = api_client.get_reservation(st.session_state.reservation_id)
    if not reservation:
        st.error("Reservation not found.")
        if st.button("Go Home"):
            go_to_page("Home")
        return
    
    if reservation["status"] == "confirmed":
        st.success("Already Paid! Seat Confirmed.")
        if st.button("Go Home"):
            go_to_page("Home")
        return

    now = datetime.now(timezone.utc)
    created_at = datetime.fromisoformat(reservation["created_at"]).replace(tzinfo=timezone.utc)
    timeout_threshold = now - timedelta(minutes=5)
    
    if created_at < timeout_threshold:
        st.error("Reservation Expired (5 minutes passed).")
        if st.button("Go Home"):
            go_to_page("Home")
        return

    price = 15.0 if reservation["seat"]["is_corner"] else 10.0
    
    st.query_params["res_id"] = str(reservation["id"])
    
    st.header("Checkout")
    st.write(f"**Movie**: {reservation['movie']['name']}")
    st.write(f"**Seat**: {reservation['seat']['row']}{reservation['seat']['number']}")
    st.write(f"**Total Price**: ${price}")
    
    expire_time_ms = int((created_at + timedelta(minutes=5)).timestamp() * 1000)
    html_code = f"""
    <div style="
        font-family: 'Inter', sans-serif;
        background-color: rgba(255, 189, 69, 0.1);
        color: #ffbd45;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid rgba(255, 189, 69, 0.3);
        display: flex;
        align-items: center;
        font-size: 16px;
    ">
        <span style="margin-right: 10px; font-size: 20px;">⏳</span> 
        <span id="timer">Calculating remaining time...</span>
    </div>
    <script>
        var countDownDate = {expire_time_ms};
        var x = setInterval(function() {{
            var now = new Date().getTime();
            var distance = countDownDate - now;
            if (distance < 0) {{
                clearInterval(x);
                document.getElementById("timer").innerHTML = "Reservation Expired! Please refresh the page.";
                window.parent.location.reload();
            }} else {{
                var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                document.getElementById("timer").innerHTML = "You have <strong>" + minutes + " minutes and " + seconds + " seconds</strong> left to complete this purchase.";
            }}
        }}, 1000);
    </script>
    """
    components.html(html_code, height=75)
    
    if st.button("Pay with Stripe"):
        try:
            url = api_client.create_checkout_session(reservation["id"])
            if url:
                st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
            else:
                st.error("Error creating Checkout session.")
        except Exception as e:
            st.error(f"Error creating Stripe Checkout session: {str(e)}")

def render_admin(user):
    if not user or not user.get("is_admin"):
        st.error("Unauthorized access")
        st.stop()
        
    st.header("Admin Dashboard")
    
    st.subheader("Add New Movie")
    with st.form("add_movie_form"):
        name = st.text_input("Movie Name")
        start_date = st.date_input("Start Date")
        start_time = st.time_input("Start Time")
        duration = st.number_input("Duration (minutes)", min_value=1, value=120)
        
        if st.form_submit_button("Add Movie"):
            if api_client.add_movie(name, start_date, start_time, duration):
                st.success("Movie added successfully!")
                st.rerun()
            else:
                st.error("Failed to add movie.")
            
    st.write("---")
    st.subheader("Manage Movies")
    movies = api_client.get_all_movies()
    for m in movies:
        col1, col2 = st.columns([4, 1])
        start_dt = datetime.fromisoformat(m["start_time"])
        with col1:
            st.write(f"**{m['name']}** | Starts: {start_dt.strftime('%Y-%m-%d %H:%M')} | {m['duration_minutes']} mins")
        with col2:
            if st.button("Delete", key=f"del_{m['id']}"):
                api_client.delete_movie(m["id"])
                st.rerun()

def render_my_bookings(user):
    if not user:
        st.error("Please log in to view your bookings.")
        return
        
    st.header("My Bookings")
    
    reservations = api_client.get_my_reservations()
    # Filter for confirmed bookings
    reservations = [r for r in reservations if r["status"] == "confirmed"]
    
    now = datetime.now(timezone.utc)
    
    upcoming = []
    past = []
    for r in reservations:
        movie_start = datetime.fromisoformat(r["movie"]["start_time"]).replace(tzinfo=timezone.utc)
        if movie_start >= now:
            upcoming.append(r)
        else:
            past.append(r)
    
    # Sort by date descending
    upcoming.sort(key=lambda r: datetime.fromisoformat(r["movie"]["start_time"]), reverse=True)
    past.sort(key=lambda r: datetime.fromisoformat(r["movie"]["start_time"]), reverse=True)
    
    st.subheader("Upcoming Bookings")
    if not upcoming:
        st.info("No upcoming bookings.")
    else:
        for r in upcoming:
            with st.container(border=True):
                movie_start = datetime.fromisoformat(r["movie"]["start_time"]).replace(tzinfo=timezone.utc)
                created_at = datetime.fromisoformat(r["created_at"]).replace(tzinfo=timezone.utc)
                st.write(f"**Movie**: {r['movie']['name']}")
                st.write(f"**Date & Time**: {movie_start.strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Seat**: {r['seat']['row']}{r['seat']['number']}")
                st.write(f"**Booked On**: {created_at.strftime('%Y-%m-%d')}")
                
    st.subheader("Past Bookings")
    if not past:
        st.info("No past bookings.")
    else:
        for r in past:
            with st.container(border=True):
                movie_start = datetime.fromisoformat(r["movie"]["start_time"]).replace(tzinfo=timezone.utc)
                created_at = datetime.fromisoformat(r["created_at"]).replace(tzinfo=timezone.utc)
                st.write(f"**Movie**: {r['movie']['name']}")
                st.write(f"**Date & Time**: {movie_start.strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Seat**: {r['seat']['row']}{r['seat']['number']}")
                st.write(f"**Booked On**: {created_at.strftime('%Y-%m-%d')}")
