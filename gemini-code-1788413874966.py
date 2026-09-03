# MODULE 6: PHASE 5 SPATIAL MAPPING, GEOCODING & STATISTICAL ANALYTICS
elif menu == "📈 Phase 5: Spatial & Statistical Analytics":
    st.subheader("Phase 5: Spatial Mapping, Geocoding, & Advanced Statistical Analytics")
    
    t_geo, t_gis, t_stat, t_ref = st.tabs([
        "📍 6.1 Geocoding Protocol",
        "🗺️ 6.2 Multi-Layer GIS Engine",
        "📊 6.3 Advanced Statistical Modeling",
        "📋 Analytics Framework Table"
    ])

    # 6.1 Geocoding Protocol
    with t_geo:
        st.markdown("**6.1 Spot Mapping & Mobile Address Geocoding Workflow**")
        
        st.markdown("""
        * **Step 1: Participatory BHW Spot Mapping:** Mobilize BHWs to draw baseline community spot maps capturing every residential structure, water source, and health facility.
        * **Step 2: GPS Mobile Geocoding:** Utilizing handheld GPS devices or mobile survey software (KoboToolbox), capture exact latitude and longitude coordinates $(x, y)$ for every surveyed household.
        * **Step 3: GIS Layering:** Upload geocoded survey points into QGIS or ArcGIS to convert static addresses into spatial shapefiles.
        """)

        st.markdown("---")
        st.markdown("**⚡ Mobile Geocoding Coordinate Validator (KoboToolbox Field Test)**")
        c1, c2, c3 = st.columns(3)
        input_lat = c1.number_input("Test Latitude (Y)", value=11.1562, format="%.6f")
        input_lon = c2.number_input("Test Longitude (X)", value=124.9912, format="%.6f")
        input_acc = c3.number_input("GPS Accuracy Radius (Meters)", value=3.2, step=0.1)

        if input_acc <= 5.0:
            st.success(f"✅ **GPS Lock Validated:** High accuracy ({input_acc}m) suitable for household shapefile export.")
        else:
            st.warning(f"⚠️ **Weak GPS Lock:** Accuracy is {input_acc}m. Re-calibrate device before saving geocode.")
