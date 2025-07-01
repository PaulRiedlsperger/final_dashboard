# Ausgabe
    # RHR
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**💖 RHR:** {rhr_warning}")
    with col2:
        st.plotly_chart(show_mini_chart(current=latest_rhr, lower=lower_rhr, upper=upper_rhr, unit="bpm"), use_container_width=True)

    # HRV
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**💕 HRV:** {hrv_warning}")
    with col2:
        st.plotly_chart(show_mini_chart(current=latest_hrv, lower=lower_hrv, upper=upper_hrv, unit="ms"), use_container_width=True)

    # Temperatur
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**🌡️ Hauttemperatur:** {temp_warning}")
    with col2:
        st.plotly_chart(show_mini_chart(current=latest_temp, lower=lower_temp, upper=upper_temp, unit="°C"), use_container_width=True)

    # Schlafscore
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**😴 Schlafscore:** {sleep_warning}")
    with col2:
        st.plotly_chart(show_mini_chart(current=latest_sleep, lower=lower_sleep, upper=upper_sleep, unit="%"), use_container_width=True)
            
    result_link = person.healthdata_path
    df = read_my_csv(result_link)
   
