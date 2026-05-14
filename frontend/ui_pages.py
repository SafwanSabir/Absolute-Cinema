# pyrefly: ignore [missing-import]
import streamlit as st
from datetime import datetime, timedelta, timezone
# pyrefly: ignore [missing-import]
import streamlit.components.v1 as components
from backend import services

def render_home(db, go_to_page):
    st.header("Now Showing")
    movies = services.get_upcoming_movies(db)
    
    if not movies:
        st.info("No upcoming movies at the moment.")
    else:
        for movie in movies:
            with st.container(border=True):
                m_col1, m_col2 = st.columns([3, 1])
                with m_col1:
                    st.subheader(movie.name)
                    st.write(f"**Starts at:** {movie.start_time.strftime('%Y-%m-%d %H:%M UTC')}")
                    st.write(f"**Duration:** {movie.duration_minutes} mins")
                with m_col2:
                    st.write("") # Spacing
                    if st.button("Book Seats", key=f"book_{movie.id}", use_container_width=True):
                        st.session_state.selected_movie = movie.id
                        go_to_page("Movie Details")

def render_login(db, go_to_page):
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            st.write("") # Spacing
            if st.button("Login", key="action_login", use_container_width=True):
                user_id = services.authenticate_user(db, username, password)
                if user_id:
                    st.session_state.user_id = user_id
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

def render_register(db, go_to_page):
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center;'>Register</h2>", unsafe_allow_html=True)
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            st.write("") # Spacing
            if st.button("Register", key="action_register", use_container_width=True):
                success = services.register_new_user(db, username, email, password)
                if not success:
                    st.error("Username already exists")
                else:
                    st.success("Registered successfully! Please login.")
                    go_to_page("Login")
            
            st.write("---")
            if st.button("Already have an account? Login", key="goto_login", use_container_width=True):
                go_to_page("Login")

def render_forgot_password(db, go_to_page):
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center;'>Forgot Password</h2>", unsafe_allow_html=True)
            email = st.text_input("Enter your registered email")
            
            if st.button("Send Reset Link", key="action_send_reset", use_container_width=True):
                if services.send_reset_email(email):
                    st.success("If your email is registered, a reset link has been sent!")
                else:
                    st.error("Failed to send reset link. Please try again later.")
            
            st.write("---")
            if st.button("Back to Login", key="back_to_login", use_container_width=True):
                go_to_page("Login")

def render_reset_password(db, go_to_page, token):
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center;'>Reset Password</h2>", unsafe_allow_html=True)
            
            from backend.auth import verify_reset_token
            email = verify_reset_token(token)
            
            if not email:
                st.error("Invalid or expired reset token.")
                if st.button("Go to Login", use_container_width=True):
                    st.query_params.clear()
                    go_to_page("Login")
            else:
                st.write(f"Resetting password for: {email}")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                
                if st.button("Update Password", key="action_update_pwd", use_container_width=True):
                    if new_password != confirm_password:
                        st.error("Passwords do not match!")
                    elif len(new_password) < 4:
                        st.error("Password too short.")
                    else:
                        if services.reset_user_password(db, email, new_password):
                            st.success("Password updated successfully! Please login.")
                            st.query_params.clear()
                            go_to_page("Login")
                        else:
                            st.error("Error resetting password.")

def render_movie_details(db, go_to_page, user):
    if not st.session_state.selected_movie:
        go_to_page("Home")
        return
    
    movie = services.get_movie_details(db, st.session_state.selected_movie)
    if not movie:
        st.error("Movie not found")
        go_to_page("Home")
        return
    
    st.header(f"Book Seats for {movie.name}")
    st.write(f"Starts at: {movie.start_time.strftime('%Y-%m-%d %H:%M UTC')} | Duration: {movie.duration_minutes} mins")
    
    st.subheader("Available Seats")
    seats = services.get_all_seats(db)
    
    # Lay out seats in columns to look like a cinema row
    rows = {}
    for seat in seats:
        if seat.row not in rows:
            rows[seat.row] = []
        rows[seat.row].append(seat)
        
    for r, row_seats in rows.items():
        st.write(f"**Row {r}**")
        cols = st.columns(len(row_seats))
        for idx, seat in enumerate(row_seats):
            with cols[idx]:
                is_available = services.is_seat_available(db, movie.id, seat.id)
                price = services.CORNER_SEAT_PRICE if seat.is_corner else services.REGULAR_SEAT_PRICE
                
                if is_available:
                    if st.button(f"{seat.row}{seat.number} (${price})", key=f"seat_{seat.id}"):
                        if not user:
                            st.warning("Please login to book a seat.")
                            st.session_state.current_page = "Login"
                            st.rerun()
                        else:
                            res = services.book_seat_pending(db, user.id, movie.id, seat.id)
                            st.session_state.reservation_id = res.id
                            go_to_page("Checkout")
                else:
                    st.button(f"{seat.row}{seat.number} (Taken)", key=f"seat_{seat.id}", disabled=True)
    
    if st.button("Back to Movies"):
        go_to_page("Home")

def render_checkout(db, go_to_page, user):
    if not st.session_state.reservation_id:
        go_to_page("Home")
        return
        
    reservation = services.get_reservation(db, st.session_state.reservation_id, user.id)
    if not reservation:
        st.error("Reservation not found.")
        if st.button("Go Home"):
            go_to_page("Home")
        return
    
    if reservation.status == "confirmed":
        st.success("Already Paid! Seat Confirmed.")
        if st.button("Go Home"):
            go_to_page("Home")
        return

    now = datetime.utcnow()
    timeout_threshold = now - timedelta(minutes=services.RESERVATION_TIMEOUT_MINUTES)
    
    if reservation.created_at < timeout_threshold:
        st.error("Reservation Expired (5 minutes passed).")
        if st.button("Go Home"):
            go_to_page("Home")
        return

    price = services.CORNER_SEAT_PRICE if reservation.seat.is_corner else services.REGULAR_SEAT_PRICE
    
    # Update query parameters to persist session via the URL if the browser back button is used
    st.query_params["res_id"] = str(reservation.id)
    
    st.header("Checkout")
    st.write(f"**Movie**: {reservation.movie.name}")
    st.write(f"**Seat**: {reservation.seat.row}{reservation.seat.number}")
    st.write(f"**Total Price**: ${price}")
    
    expire_time_ms = int((reservation.created_at.replace(tzinfo=timezone.utc) + timedelta(minutes=services.RESERVATION_TIMEOUT_MINUTES)).timestamp() * 1000)
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
            url = services.create_stripe_checkout(reservation)
            st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error creating Stripe Checkout session: {str(e)}")

def render_admin(db, user):
    if not user or not user.is_admin:
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
            services.add_movie(db, name, start_date, start_time, duration)
            st.success("Movie added successfully!")
            st.rerun()
            
    st.write("---")
    st.subheader("Manage Movies")
    movies = services.get_all_movies(db)
    for m in movies:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{m.name}** | Starts: {m.start_time} | {m.duration_minutes} mins")
        with col2:
            if st.button("Delete", key=f"del_{m.id}"):
                services.delete_movie(db, m.id)
                st.rerun()

def render_my_bookings(db, user):
    if not user:
        st.error("Please log in to view your bookings.")
        return
        
    st.header("My Bookings")
    
    reservations = [r for r in user.reservations if r.status == "confirmed"]
    
    now = datetime.utcnow()
    upcoming = [r for r in reservations if r.movie.start_time >= now]
    past = [r for r in reservations if r.movie.start_time < now]
    
    # Sort by date descending
    upcoming.sort(key=lambda r: r.movie.start_time, reverse=True)
    past.sort(key=lambda r: r.movie.start_time, reverse=True)
    
    st.subheader("Upcoming Bookings")
    if not upcoming:
        st.info("No upcoming bookings.")
    else:
        for r in upcoming:
            with st.container(border=True):
                st.write(f"**Movie**: {r.movie.name}")
                st.write(f"**Date & Time**: {r.movie.start_time.strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Seat**: {r.seat.row}{r.seat.number}")
                st.write(f"**Booked On**: {r.created_at.strftime('%Y-%m-%d')}")
                
    st.subheader("Past Bookings")
    if not past:
        st.info("No past bookings.")
    else:
        for r in past:
            with st.container(border=True):
                st.write(f"**Movie**: {r.movie.name}")
                st.write(f"**Date & Time**: {r.movie.start_time.strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Seat**: {r.seat.row}{r.seat.number}")
                st.write(f"**Booked On**: {r.created_at.strftime('%Y-%m-%d')}")
