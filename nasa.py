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
        icons=["calendar", "calendar3"],
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
        velocity = st.slider("Relative Velocity ", 1418.21, 173071.83, (1418.21, 173071.83))
        astro = st.slider("Astronomical Unit", 5.16453e-05, 0.4999515747)
        hazardous = st.selectbox("Potentially Hazardous?", options=[0, 1], index=0)

    with c3:
        start_date = st.date_input("Start Date", datetime(2024, 1, 1))
        end_date = st.date_input("End Date", datetime(2025, 4, 13))
    button = st.button("Apply Filter")

    if button:
        query = """
            SELECT
                asteroids.id, asteroids.name, asteroids.absolute_magnitude_h,
                asteroids.estimated_diameter_min_km, asteroids.estimated_diameter_max_km,
                asteroids.is_potentially_hazardous_asteroid,
                close_approach.neo_reference_id,close_approach.close_approach_data,
                close_approach.relative_velocity,close_approach.astronomical_unit,
                close_approach.miss_distance_kilometers, 
                close_approach.orbiting_body
            FROM asteroids
            JOIN close_approach ON asteroids.id = close_approach.neo_reference_id
            WHERE asteroids.absolute_magnitude_h BETWEEN %s AND %s
              AND asteroids.estimated_diameter_min_km BETWEEN %s AND %s
              AND asteroids.estimated_diameter_max_km BETWEEN %s AND %s
              AND close_approach.relative_velocity BETWEEN %s AND %s
              AND close_approach.close_approach_data BETWEEN %s AND %s
              AND asteroids.is_potentially_hazardous_asteroid = %s
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
    option = st.selectbox("Select your query",[
         
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
                                            '19.Get average relative velocity of close approaches',
                                            '20.Sort asteroids by maximum estimated diameter (descending)'
                                       ], index=None)

    if option == '1.Count how many times each asteroid has approached Earth':
        cursor.execute("""
            SELECT a.name, COUNT(c.neo_reference_id) AS approach_count
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            GROUP BY a.name
            ORDER BY approach_count DESC
        """)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=["Asteroid Name", "Velocity (kmph)"])
        st.subheader(" Top 10 Fastest Asteroids")
        st.dataframe(df, use_container_width=True)
 
           
        
       
    elif option == '2.Average velocity of each asteroid over multiple approaches':
        cursor.execute("""
                SELECT a.name, AVG(c.relative_velocity) AS average_velocity
            FROM close_approach c
            JOIN asteroids a ON a.id = c.neo_reference_id
            GROUP BY a.name
            ORDER BY average_velocity DESC
            """)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=["Asteroid Name", "Approach Date"])
        st.subheader(" Asteroids Approaching After June 1, 2024")
        st.dataframe(df, use_container_width=True)

    elif option == '3.List top 10 fastest asteroids':
        cursor.execute("""
            SELECT asteroids.name, close_approach.relative_velocity
            FROM close_approach
            JOIN asteroids ON asteroids.id = close_approach.neo_reference_id
            ORDER BY close_approach.relative_velocity DESC
            LIMIT 10
        """)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=["Asteroid Name", "Velocity (kmph)"])
        st.subheader(" Top 10 Fastest Asteroids")
        st.dataframe(df, use_container_width=True)
        
    elif option == '4.Find potentially hazardous asteroids that have approached Earth more than 3 times':
        cursor.execute("""
           SELECT a.name, COUNT(c.neo_reference_id) AS approach_count
          FROM asteroids a
          JOIN close_approach c ON a.id = c.neo_reference_id
          WHERE a.is_potentially_hazardous_asteroid = 1
         GROUP BY a.name
        HAVING approach_count > 3 """)
             
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=["Asteroid Name", "Approach Count"])
        st.subheader("Potentially Hazardous Asteroids (More than 3 Approaches)")
        st.dataframe(df, use_container_width=True)

    elif option == '5.Find the month with the most asteroid approaches':    
        cursor.execute("""
            SELECT DATE_FORMAT(close_approach_data, '%Y-%m') AS month,
                COUNT(*) AS approach_count
            FROM close_approach
            GROUP BY month
            ORDER BY month
        """)
        results = cursor.fetchall()
        df = pd.DataFrame(results, columns=["Month", "Approach Count"])
        st.dataframe(df.set_index("Month"), use_container_width=True)

    elif option == '6.Get the asteroid with the fastest ever approach speed':
        cursor.execute("""
                SELECT a.name, c.relative_velocity
                FROM close_approach c
                JOIN asteroids a ON a.id = c.neo_reference_id
                ORDER BY c.relative_velocity DESC
                LIMIT 1
            """)
        result = cursor.fetchone()
        st.subheader("🚀 Fastest Asteroid Approach Speed")
        st.write(f"🌠 Asteroid: {result[0]}")
        st.write(f"💨 Speed: {result[1]:,.2f} km/h")
            
            # Optional: Display nicely in table
        st.dataframe(pd.DataFrame([result], columns=["Asteroid Name", "Relative Velocity (km/h)"]), use_container_width=True)

    elif option == '7.Sort asteroids by maximum estimated diameter (descending)':
        cursor.execute("""
            SELECT asteroids.name, asteroids.estimated_diameter_max_km
            FROM asteroids
            ORDER BY asteroids.estimated_diameter_max_km DESC
        """)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=["Asteroid Name", "Max Diameter (km)"])
        st.subheader(" Asteroids by Maximum Estimated Diameter")
        st.dataframe(df, use_container_width=True)

    elif option == '8.An asteroid whose closest approach is getting nearer over time(Hint: Use ORDER BY close_approach_date and look at miss_distance)':
        cursor.execute("""
        SELECT c.neo_reference_id, a.name, c.close_approach_data, c.miss_distance_kilometers
        FROM close_approach c
        JOIN asteroids a ON a.id = c.neo_reference_id
        WHERE c.neo_reference_id IN (
            SELECT neo_reference_id
            FROM close_approach
            GROUP BY neo_reference_id
            HAVING COUNT(*) >= 2
        )
        ORDER BY c.neo_reference_id, c.close_approach_data
    """)
    
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=["Asteroid ID", "Asteroid Name", "Approach Data", "Miss Distance (km)"])
        st.subheader(" Asteroids with Approaches Getting Closer Over Time")
        st.dataframe(df, use_container_width=True)
            
    elif option == '9.Display the name of each asteroid along with the date and miss distance of its closest approach to Earth':
        cursor.execute("""
        SELECT a.name, c.close_approach_data, c.miss_distance_kilometers
        FROM close_approach c
        JOIN asteroids a ON a.id = c.neo_reference_id
        WHERE (c.neo_reference_id, c.miss_distance_kilometers) IN (
            SELECT neo_reference_id, MIN(miss_distance_kilometers)
            FROM close_approach
            GROUP BY neo_reference_id
        )
        ORDER BY c.miss_distance_kilometers
    """)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=["Asteroid Name", "Approach Date", "Miss Distance (km)"])
        st.subheader("🛰️ Closest Approach of Each Asteroid")
        st.dataframe(df, use_container_width=True)

        

        

  


    elif option == '10.List names of asteroids that approached Earth with velocity > 50,000 km/h':
        cursor.execute("""
            SELECT a.name, c.relative_velocity
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE c.relative_velocity > 50000
        """)
        results = cursor.fetchall()
        df = pd.DataFrame(results, columns=["Asteroid Name", "Relative Velocity (km/h)"])
        st.subheader("🚀 Asteroids with Velocity > 50,000 km/h")
        st.dataframe(df, use_container_width=True)

    elif option == '11.Count how many approaches happened per month':
        cursor.execute("""
            SELECT DATE_FORMAT(close_approach.close_approach_data, '%Y-%m') AS month,
                   COUNT(*) AS approach_count
            FROM close_approach
            GROUP BY month
            ORDER BY month
        """)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=["Month", "Approach Count"])
        st.subheader(" Asteroid Approaches Count Per Month")
        st.dataframe(df, use_container_width=True)

    elif option == '12.Find asteroid with the highest brightness (lowest magnitude value)':
        cursor.execute("""
            SELECT asteroids.name, asteroids.absolute_magnitude_h
            FROM asteroids
            ORDER BY asteroids.absolute_magnitude_h ASC
            LIMIT 1
        """)
        result = cursor.fetchone()
        st.subheader(" Asteroid with Highest Brightness")
        #st.write(f"Asteroid: {result[0]}, Magnitude: {result[1]}")
        st.dataframe(pd.DataFrame([result], columns=["Asteroid Name", "Absolute Magnitude (H)"]), use_container_width=True)
    
    elif option == '13.Get number of hazardous vs non-hazardous asteroids':
        cursor.execute("""
            SELECT is_potentially_hazardous_asteroid, COUNT(*) AS count
            FROM asteroids
            GROUP BY is_potentially_hazardous_asteroid
        """)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=["Hazardous (0=No, 2=Yes)", "Count"])
        st.subheader(" Hazardous vs Non-Hazardous Asteroids")
        st.dataframe(df, use_container_width=True)

    elif option == '14.Find asteroids that passed closer than the Moon (lesser than 1 LD), along with their close approach date and distance.':
        cursor.execute("""
            SELECT asteroids.name, close_approach.close_approach_data, close_approach.miss_distance_km
            FROM close_approach
            JOIN asteroids ON asteroids.id = close_approach.neo_reference_id
            WHERE close_approach.miss_distance_km < 384400  -- 1 LD in km
        """)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=["Asteroid Name", "Approach Data", "Miss Distance (km)"])
        st.subheader(" Asteroids Passing Closer than the Moon")
        st.dataframe(df, use_container_width=True)

    elif option == '15.Find asteroids that came within 0.05 AU(astronomical distance)':
        cursor.execute("""
                        SELECT asteroids.name, close_approach.close_approach_data, close_approach.miss_distance_kilometers
                FROM close_approach
                JOIN asteroids ON asteroids.id = close_approach.neo_reference_id
                WHERE close_approach.miss_distance_kilometers < 0.05 * 149597870.7  -- 0.05 AU in km

        """)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=["Asteroid Name", "Approach Data", "Miss Distance (km)"])
        st.subheader(" Asteroids Coming Within 0.05 AU")
        st.dataframe(df, use_container_width=True)

    elif option == '16.List all asteroids with close approaches after June 1, 2024':    
        cursor.execute("""
            SELECT asteroids.name, close_approach.close_approach_data
            FROM close_approach
            JOIN asteroids ON asteroids.id = close_approach.neo_reference_id
            WHERE close_approach.close_approach_data > '2024-06-01'
        """)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=["Asteroid Name", "Approach Date"])
        st.subheader(" Asteroids Approaching After June 1, 2024")
        st.dataframe(df, use_container_width=True)
    elif option == '17.Group close approaches by orbiting body and count':  
        cursor.execute("""
            SELECT close_approach.orbiting_body, COUNT(*) AS approach_count
            FROM asteroids
            JOIN close_approach ON asteroids.id = close_approach.neo_reference_id
            GROUP BY close_approach.orbiting_body
        """)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=["Orbiting Body", "Approach Count"])
        st.subheader(" Close Approaches Grouped by Orbiting Body")
        st.dataframe(df, use_container_width=True)
    elif option == '18.Find top 5 closest approaches (by km)':
        cursor.execute("""
            SELECT asteroids.name, close_approach.miss_distance_kilometers
            FROM close_approach
            JOIN asteroids ON asteroids.id = close_approach.neo_reference_id
            ORDER BY close_approach.miss_distance_kilometers ASC
            LIMIT 5
        """)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=["Asteroid Name", "Miss Distance (km)"])
        st.subheader(" Top 5 Closest Approaches")
        st.dataframe(df, use_container_width=True)
    elif option == '19.Get average relative velocity of close approaches':
        cursor.execute("""
            SELECT AVG(close_approach.relative_velocity_kmph) AS average_velocity
            FROM close_approach
        """)
        result = cursor.fetchone()
        st.subheader(" Average Relative Velocity of Close Approaches")
        st.write(f"Average Velocity: {result[0]} km/h")
    elif option == '20.Sort asteroids by maximum estimated diameter (descending)':
        cursor.execute("""
            SELECT asteroids.name, asteroids.estimated_diameter_max_km
            FROM asteroids
            ORDER BY asteroids.estimated_diameter_max_km DESC
        """)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=["Asteroid Name", "Max Diameter (km)"])
        st.subheader(" Asteroids by Maximum Estimated Diameter")
        st.dataframe(df, use_container_width=True)





