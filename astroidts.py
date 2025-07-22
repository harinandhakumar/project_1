import streamlit as st
import pandas as pd
from datetime import datetime
import mysql.connector
from streamlit_option_menu import option_menu

# --- MySQL Connection ---
connection = mysql.connector.connect(
    host='gateway01.ap-southeast-1.prod.aws.tidbcloud.com',
    port=4000,
    user='2sMd98h2CXNeL3Y.root',
    password='sdT7ISwZV0yAGWAU',
    database='nasa_data'
)
cursor = connection.cursor()

# --- Page Setup ---
st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center; color: #4B8BBE;'>🚀 NASA Asteroid Tracker 🌠</h1>", unsafe_allow_html=True)
st.divider()

# --- Sidebar Menu ---
with st.sidebar:
    selected = option_menu(
        menu_title="Asteroid Approaches",
        options=["Filter Criteria", "Queries"],
        icons=["funnel", "search"],
        menu_icon="cast",
        default_index=0
    )

# --- Filter Criteria Section ---
if selected == "Filter Criteria":
    c1, a, c2, b, c3 = st.columns([0.2, 0.1, 0.2, 0.1, 0.2])

    with c1:
        mag_min = st.slider("Magnitude Range", 13.8, 32.61, (13.8, 32.61))
        diam_min = st.slider("Min Estimated Diameter (km)", 0.00, 4.62, (0.00, 4.62))
        diam_max = st.slider("Max Estimated Diameter (km)", 0.00, 10.33, (0.00, 10.33))

    with c2:
        velocity = st.slider("Relative Velocity (kmph)", 1418.21, 173071.83, (1418.21, 173071.83))
        astro = st.slider("Astronomical Unit", 5.16453e-05, 0.4999515747)
        hazardous = st.selectbox("Potentially Hazardous?", options=[0, 1], index=0)

    with c3:
        start_date = st.date_input("Start Date", datetime(2024, 1, 1))
        end_date = st.date_input("End Date", datetime(2025, 4, 13))

    if st.button("Apply Filter"):
        query = """
            SELECT
                a.id, a.name, a.absolute_magnitude_h,
                a.estimated_diameter_min_km, a.estimated_diameter_max_km,
                a.is_potentially_hazardous_asteroid,
                c.neo_reference_id, c.close_approach_date,
                c.relative_velocity_kmph, c.astronomical_unit,
                c.miss_distance_kilometers, c.miss_distance_km, c.orbiting_body
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE a.absolute_magnitude_h BETWEEN %s AND %s
              AND a.estimated_diameter_min_km BETWEEN %s AND %s
              AND a.estimated_diameter_max_km BETWEEN %s AND %s
              AND c.relative_velocity_kmph BETWEEN %s AND %s
              AND c.close_approach_date BETWEEN %s AND %s
              AND a.is_potentially_hazardous_asteroid = %s
        """
        params = [
            mag_min[0], mag_min[1],
            diam_min[0], diam_min[1],
            diam_max[0], diam_max[1],
            velocity[0], velocity[1],
            start_date, end_date,
            hazardous
        ]
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        st.subheader("🛰️ Filtered Asteroids")
        st.dataframe(df, use_container_width=True)

# --- Predefined Queries Section ---
elif selected == "Queries":
    option = st.selectbox("Select your query", [
        '1.Count how many times each asteroid has approached Earth',
        '2.Average velocity of each asteroid over multiple approaches',
        '3.List top 10 fastest asteroids',
        '4.Find potentially hazardous asteroids that have approached Earth more than 3 times',
        '5.Find the month with the most asteroid approaches',
        '6.Get the asteroid with the fastest ever approach speed',
        '7.Sort asteroids by maximum estimated diameter (descending)',
        '8.An asteroid whose closest approach is getting nearer over time(Hint: Use ORDER BY close_approach_date and look at miss_distance)', 
        '9.Display the name of each asteroid along with the date and miss distance of its closest approach to Earth',
        '10.List names of asteroids that approached Earth with velocity > 50,000 km/h',
        '11.Count how many approaches happened per month',
        '12.Find asteroid with the highest brightness (lowest magnitude value)',
        '13.Get number of hazardous vs non-hazardous asteroids',
        '14.Find asteroids that passed closer than the Moon (lesser than 1 LD), along with their close approach date and distance',
        '15.Find asteroids that came within 0.05 AU(astronomical distance)',
        '16.List all asteroids with close approaches after June 1, 2024',
        '17.Group close approaches by orbiting body and count',
        '18.Find top 5 closest approaches (by km)',
        '19.Get average relative velocity of close approaches'
    ])

    if option == '1.Count how many times each asteroid has approached Earth':
        cursor.execute("""
            SELECT a.name, COUNT(c.neo_reference_id) AS approach_count
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            GROUP BY a.name
            ORDER BY approach_count DESC
        """)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=["Asteroid Name", "Approach Count"])
        st.subheader("🪨 Asteroid Approach Counts")
        st.dataframe(df, use_container_width=True)

    elif option == '2.Average velocity of each asteroid over multiple approaches':
        cursor.execute("""
            SELECT a.name, AVG(c.relative_velocity_kmph) AS avg_velocity
            FROM close_approach c
            JOIN asteroids a ON a.id = c.neo_reference_id
            GROUP BY a.name
            ORDER BY avg_velocity DESC
        """)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=["Asteroid Name", "Average Velocity (kmph)"])
        st.subheader("🚀 Average Velocity per Asteroid")
        st.dataframe(df, use_container_width=True)

    elif option == '3.List top 10 fastest asteroids':
        cursor.execute("""
            SELECT a.name, c.relative_velocity_kmph
            FROM close_approach c
            JOIN asteroids a ON a.id = c.neo_reference_id
            ORDER BY c.relative_velocity_kmph DESC
            LIMIT 10
        """)
        df = pd.DataFrame(cursor.fetchall(), columns=["Asteroid Name", "Velocity (kmph)"])
        st.subheader("⚡ Top 10 Fastest Asteroids")
        st.dataframe(df, use_container_width=True)

    elif option == '4.Find potentially hazardous asteroids that have approached Earth more than 3 times':
        cursor.execute("""
            SELECT a.name, COUNT(c.neo_reference_id) AS approach_count
            FROM close_approach c
            JOIN asteroids a ON a.id = c.neo_reference_id
            WHERE a.is_potentially_hazardous_asteroid = 1
            GROUP BY a.name
            HAVING approach_count > 3
        """)
        df = pd.DataFrame(cursor.fetchall(), columns=["Asteroid Name", "Approach Count"])
        st.subheader("☢️ Hazardous Asteroids with >3 Approaches")
        st.dataframe(df, use_container_width=True)

    elif option == '5.Find the month with the most asteroid approaches':    
        cursor.execute("""
            SELECT DATE_FORMAT(c.close_approach_date, '%Y-%m') AS month,
                   COUNT(*) AS approach_count
            FROM close_approach c
            GROUP BY month
            ORDER BY approach_count DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        st.subheader("📅 Month with Most Approaches")
        st.write(f"Month: {result[0]}, Approaches: {result[1]}")

    elif option == '6.Get the asteroid with the fastest ever approach speed':
        cursor.execute("""
            SELECT a.name, MAX(c.relative_velocity_kmph) AS max_velocity
            FROM close_approach c
            JOIN asteroids a ON a.id = c.neo_reference_id
            GROUP BY a.name
            ORDER BY max_velocity DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        st.subheader("💨 Fastest Asteroid")
        st.write(f"Asteroid: {result[0]}, Speed: {result[1]:,.2f} km/h")

    elif option == '7.Sort asteroids by maximum estimated diameter (descending)':
        cursor.execute("""
            SELECT name, estimated_diameter_max_km
            FROM asteroids
            ORDER BY estimated_diameter_max_km DESC
        """)
        df = pd.DataFrame(cursor.fetchall(), columns=["Asteroid Name", "Max Diameter (km)"])
        st.subheader("📏 Asteroids by Max Diameter")
        st.dataframe(df, use_container_width=True)

    elif option == '8.An asteroid whose closest approach is getting nearer over time(Hint: Use ORDER BY close_approach_date and look at miss_distance)':
        cursor.execute("""
            SELECT a.name, c.close_approach_date, c.miss_distance_km
            FROM close_approach c
            JOIN asteroids a ON a.id = c.neo_reference_id
            ORDER BY c.close_approach_date, c.miss_distance_km
        """)
        df = pd.DataFrame(cursor.fetchall(), columns=["Asteroid Name", "Approach Date", "Miss Distance (km)"])
        st.subheader("📉 Closest Approaches Over Time")
        st.dataframe(df, use_container_width=True)

    elif option == '9.Display the name of each asteroid along with the date and miss distance of its closest approach to Earth':
        cursor.execute("""
            SELECT a.name, c.close_approach_date, c.miss_distance_km
            FROM close_approach c
            JOIN asteroids a ON a.id = c.neo_reference_id
            ORDER BY c.miss_distance_km ASC
        """)
        df = pd.DataFrame(cursor.fetchall(), columns=["Asteroid Name", "Approach Date", "Miss Distance (km)"])
        st.subheader("🌍 Closest Approaches")
        st.dataframe(df, use_container_width=True)

    elif option == '10.List names of asteroids that approached Earth with velocity > 50,000 km/h':
        cursor.execute("""
            SELECT a.name, c.relative_velocity_kmph
            FROM close_approach c
            JOIN asteroids a ON a.id = c.neo_reference_id
            WHERE c.relative_velocity_kmph > 50000
        """)
        df = pd.DataFrame(cursor.fetchall(), columns=["Asteroid Name", "Velocity (kmph)"])
        st.subheader("⚠️ High Velocity Asteroids")
        st.dataframe(df, use_container_width=True)

    elif option == '11.Count how many approaches happened per month':
        cursor.execute("""
            SELECT DATE_FORMAT(close_approach_date, '%Y-%m') AS month,
                   COUNT(*) AS approach_count
            FROM close_approach
            GROUP BY month
            ORDER BY month
        """)
        df = pd.DataFrame(cursor.fetchall(), columns=["Month", "Approach Count"])
        st.subheader("📅 Monthly Approach Count")
        st.dataframe(df, use_container_width=True)

    elif option == '12.Find asteroid with the highest brightness (lowest magnitude value)':
        cursor.execute("""
            SELECT name, absolute_magnitude_h
            FROM asteroids
            ORDER BY absolute_magnitude_h ASC
            LIMIT 1
        """)
        result = cursor.fetchone()
        st.subheader("💡 Brightest Asteroid")
        st.write(f"Asteroid: {result[0]}, Magnitude: {result[1]}")

    elif option == '13.Get number of hazardous vs non-hazardous asteroids':
        cursor.execute("""
            SELECT is_potentially_hazardous_asteroid, COUNT(*) AS count
            FROM asteroids
            GROUP BY is_potentially_hazardous_asteroid
        """)
        df = pd.DataFrame(cursor.fetchall(), columns=["Hazardous (0=No, 1=Yes)", "Count"])
        st.subheader("☣️ Hazardous vs Non-Hazardous Count")
        st.dataframe(df, use_container_width=True)

    elif option == '14.Find asteroids that passed closer than the Moon (lesser than 1 LD), along with their close approach date and distance':
        cursor.execute("""
            SELECT a.name, c.close_approach_date, c.miss_distance_km
            FROM close_approach c
            JOIN asteroids a ON a.id = c.neo_reference_id
            WHERE c.miss_distance_km < 384400
        """)
        df = pd.DataFrame(cursor.fetchall(), columns=["Asteroid Name", "Date", "Miss Distance (km)"])
        st.subheader("🌑 Closer Than Moon")
        st.dataframe(df, use_container_width=True)

    elif option == '15.Find asteroids that came within 0.05 AU(astronomical distance)':
        cursor.execute("""
            SELECT a.name, c.close_approach_date, c.miss_distance_km
            FROM close_approach c
            JOIN asteroids a ON a.id = c.neo_reference_id
            WHERE c.miss_distance_km < (0.05 * 149597870.7)
        """)
        df = pd.DataFrame(cursor.fetchall(), columns=["Asteroid Name", "Date", "Miss Distance (km)"])
        st.subheader("📏 Within 0.05 AU")
        st.dataframe(df, use_container_width=True)

    elif option == '16.List all asteroids with close approaches after June 1, 2024':
        cursor.execute("""
            SELECT a.name, c.close_approach_date
            FROM close_approach c
            JOIN asteroids a ON a.id = c.neo_reference_id
            WHERE c.close_approach_date > '2024-06-01'
        """)
        df = pd.DataFrame(cursor.fetchall(), columns=["Asteroid Name", "Date"])
        st.subheader("📅 Approaches After June 1, 2024")
        st.dataframe(df, use_container_width=True)

    elif option == '17.Group close approaches by orbiting body and count':
        cursor.execute("""
            SELECT orbiting_body, COUNT(*) AS approach_count
            FROM close_approach
            GROUP BY orbiting_body
        """)
        df = pd.DataFrame(cursor.fetchall(), columns=["Orbiting Body", "Approach Count"])
        st.subheader("🪐 Approaches by Orbiting Body")
        st.dataframe(df, use_container_width=True)

    elif option == '18.Find top 5 closest approaches (by km)':
        cursor.execute("""
            SELECT a.name, c.miss_distance_km
            FROM close_approach c
            JOIN asteroids a ON a.id = c.neo_reference_id
            ORDER BY c.miss_distance_km ASC
            LIMIT 5
        """)
        df = pd.DataFrame(cursor.fetchall(), columns=["Asteroid Name", "Miss Distance (km)"])
        st.subheader("🔍 Top 5 Closest Approaches")
        st.dataframe(df, use_container_width=True)

    elif option == '19.Get average relative velocity of close approaches':
        cursor.execute("""
            SELECT AVG(relative_velocity_kmph) AS average_velocity
            FROM close_approach
        """)
        result = cursor.fetchone()
        st.subheader("📊 Average Relative Velocity")
        st.write(f"Average Velocity: {result[0]:,.2f} km/h")
