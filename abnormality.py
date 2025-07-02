import pandas as pd
import plotly.graph_objects as go
from datetime import timedelta
import streamlit as st

class AbnormalityChecker:

    # Define normal ranges based on the provided table
    # Structure: {age_group: {gender: {param: (min, max)}}}
    NORMAL_RANGES = {
        (18, 29): {
            "male": {"RHR": (50, 65), "HRV": (45, 100), "Temp": (32.0, 34.0)},
            "female": {"RHR": (55, 70), "HRV": (55, 110), "Temp": (32.5, 34.5)}
        },
        (30, 39): {
            "male": {"RHR": (50, 65), "HRV": (40, 95), "Temp": (32.0, 34.0)},
            "female": {"RHR": (50, 70), "HRV": (50, 100), "Temp": (32.5, 34.5)}
        },
        (40, 49): {
            "male": {"RHR": (50, 70), "HRV": (35, 85), "Temp": (32.0, 34.0)},
            "female": {"RHR": (55, 75), "HRV": (45, 95), "Temp": (32.5, 34.5)}
        },
        (50, 59): {
            "male": {"RHR": (55, 75), "HRV": (30, 80), "Temp": (32.0, 34.0)},
            "female": {"RHR": (60, 80), "HRV": (40, 90), "Temp": (32.5, 34.5)}
        },
        (60, 150): { # Assuming 150 as a practical upper limit for age 60+
            "male": {"RHR": (55, 80), "HRV": (25, 70), "Temp": (32.0, 34.0)},
            "female": {"RHR": (60, 85), "HRV": (35, 80), "Temp": (32.5, 34.5)}
        }
    }
    # Sleep performance is general, not age/gender specific, let's assume a general healthy range
    SLEEP_PERFORMANCE_THRESHOLD_GOOD = 85
    SLEEP_PERFORMANCE_THRESHOLD_MEDIUM = 70


    @staticmethod
    def _get_range_for_person(age, gender, param_type):
        """Helper to get the correct normal range based on age and gender."""
        for age_range, genders_data in AbnormalityChecker.NORMAL_RANGES.items():
            if age_range[0] <= age <= age_range[1]:
                return genders_data.get(gender, {}).get(param_type)
        return None # Should not happen if age ranges cover all possibilities

    @staticmethod
    def check_rhr(rhr_value, age, gender):
        """Checks Resting Heart Rate (RHR) against normal ranges."""
        rhr_range = AbnormalityChecker._get_range_for_person(age, gender, "RHR")
        if rhr_range:
            min_rhr, max_rhr = rhr_range
            if rhr_value < min_rhr:
                return "! Zu niedrig"
            elif rhr_value > max_rhr:
                return "! Zu hoch"
            else:
                return "Normal"
        return "Unbekannt"

    @staticmethod
    def check_hrv(hrv_value, age, gender):
        """Checks Heart Rate Variability (HRV) against normal ranges."""
        hrv_range = AbnormalityChecker._get_range_for_person(age, gender, "HRV")
        if hrv_range:
            min_hrv, max_hrv = hrv_range
            if hrv_value < min_hrv:
                return "! Zu niedrig"
            elif hrv_value > max_hrv:
                return "! Zu hoch"
            else:
                return "Normal"
        return "Unbekannt"

    @staticmethod
    def check_skin_temp(temp_value, age, gender):
        """Checks Skin Temperature against normal ranges."""
        temp_range = AbnormalityChecker._get_range_for_person(age, gender, "Temp")
        if temp_range:
            min_temp, max_temp = temp_range
            if temp_value < min_temp:
                return "! Zu niedrig"
            elif temp_value > max_temp:
                return "! Zu hoch"
            else:
                return "Normal"
        return "Unbekannt"

    @staticmethod
    def check_sleep_score(sleep_value, age, gender): # Age/gender not used here, but kept for consistency
        """Checks Sleep Performance Score."""
        if sleep_value >= AbnormalityChecker.SLEEP_PERFORMANCE_THRESHOLD_GOOD:
            return "Hervorragend"
        elif sleep_value >= AbnormalityChecker.SLEEP_PERFORMANCE_THRESHOLD_MEDIUM:
            return "Mittelmäßig"
        else:
            return "! Schlafqualität gering"

    @staticmethod
    def analyze_and_recommend(df, age, gender):
        recommendations = []
        
        if df.empty or 'datetime' not in df.columns:
            return [("ℹ️", "Keine ausreichenden Daten für eine Analyse verfügbar.")]

        # Ensure df is sorted by datetime for trend analysis
        df = df.sort_values(by='datetime', ascending=False)
        latest_data = df.head(7).copy() # Consider last 7 days for consistency and work on a copy

        if latest_data.empty:
            return [("ℹ️", "Keine ausreichenden Daten für eine Analyse verfügbar.")]

        # Count abnormalities in the latest data
        abnormal_counts = {
            "RHR": 0,
            "HRV": 0,
            "Temp": 0,
            "Sleep": 0
        }
        total_readings = len(latest_data)

        # Apply checks and count abnormalities
        for index, row in latest_data.iterrows():
            if AbnormalityChecker.check_rhr(row["RHR"], age, gender) != "Normal":
                abnormal_counts["RHR"] += 1
            if AbnormalityChecker.check_hrv(row["HRV"], age, gender) != "Normal":
                abnormal_counts["HRV"] += 1
            if AbnormalityChecker.check_skin_temp(row["Temp"], age, gender) != "Normal":
                abnormal_counts["Temp"] += 1
            if AbnormalityChecker.check_sleep_score(row["Sleep"], age, gender) in ["Mittelmäßig", "! Schlafqualität gering"]:
                abnormal_counts["Sleep"] += 1

        # Determine recommendations based on counts and severity
        critical_issues = False
        
        # Get the mode of the status for the latest data, or default to "Normal" if empty
        rhr_status = latest_data['RHR_status'].mode()[0] if not latest_data.empty and 'RHR_status' in latest_data.columns else "Normal"
        hrv_status = latest_data['HRV_status'].mode()[0] if not latest_data.empty and 'HRV_status' in latest_data.columns else "Normal"
        temp_status = latest_data['Temp_status'].mode()[0] if not latest_data.empty and 'Temp_status' in latest_data.columns else "Normal"
        sleep_status = latest_data['Sleep_status'].mode()[0] if not latest_data.empty and 'Sleep_status' in latest_data.columns else "Normal"


        # Aggregated check for overall health
        all_normal = True
        if any(count > 0 for count in abnormal_counts.values()):
            all_normal = False

        if all_normal:
            recommendations.append(("✅", "Alle gemessenen Parameter sind in den letzten 7 Tagen im normalen Bereich. Hervorragend! Behalten Sie Ihre Routinen bei."))
        else:
            # Specific recommendations based on common or persistent issues
            if abnormal_counts["RHR"] >= 3: # If RHR is abnormal for at least 3 out of 7 days
                recommendations.append(("❤️", f"Ihre Ruheherzfrequenz ist an {abnormal_counts['RHR']} der letzten {total_readings} Tage {rhr_status.lower().replace('! ', '')}. Achten Sie auf Stressreduktion und ausreichende Hydration. Bei anhaltender Abweichung, konsultieren Sie Ihren Arzt."))
                critical_issues = True
            elif abnormal_counts["RHR"] > 0:
                    recommendations.append(("❤️", f"Ihre Ruheherzfrequenz zeigt gelegentliche Abweichungen. Regelmäßige leichte Bewegung und Entspannung können helfen."))

            if abnormal_counts["HRV"] >= 3: # If HRV is abnormal for at least 3 out of 7 days
                recommendations.append(("💓", f"Ihre Herzfrequenz-Variabilität ist an {abnormal_counts['HRV']} der letzten {total_readings} Tage {hrv_status.lower().replace('! ', '')}. Dies könnte auf Stress oder mangelnde Erholung hindeuten. Versuchen Sie Achtsamkeitsübungen und mehr Schlaf. Bei anhaltender Abweichung, konsultieren Sie Ihren Arzt."))
                critical_issues = True
            elif abnormal_counts["HRV"] > 0:
                recommendations.append(("💓", f"Ihre Herzfrequenz-Variabilität zeigt gelegentliche Abweichungen. Atemübungen und ausreichend Schlaf sind empfehlenswert."))

            if abnormal_counts["Temp"] >= 3: # If Temp is abnormal for at least 3 out of 7 days
                recommendations.append(("🌡️", f"Ihre Hauttemperatur ist an {abnormal_counts['Temp']} der letzten {total_readings} Tage {temp_status.lower().replace('! ', '')}. Achten Sie auf ausreichende Flüssigkeitszufuhr und vermeiden Sie extreme Temperaturen. Bei anhaltender Abweichung, konsultieren Sie Ihren Arzt."))
                critical_issues = True
            elif abnormal_counts["Temp"] > 0:
                recommendations.append(("🌡️", f"Ihre Hauttemperatur zeigt gelegentliche Abweichungen. Dies kann auf geringfügige Schwankungen im Stoffwechsel hindeuten."))

            if abnormal_counts["Sleep"] >= 3: # If Sleep is not good for at least 3 out of 7 days
                recommendations.append(("😴", f"Ihre Schlafqualität war an {abnormal_counts['Sleep']} der letzten {total_readings} Tage {sleep_status.lower().replace('! ', '')}. Versuchen Sie, regelmäßige Schlafzeiten einzuhalten und eine entspannende Schlafroutine zu entwickeln. Bei anhaltend schlechter Schlafqualität, suchen Sie professionellen Rat."))
                critical_issues = True
            elif abnormal_counts["Sleep"] > 0:
                recommendations.append(("😴", f"Ihre Schlafqualität war gelegentlich mittelmäßig. Achten Sie auf eine gute Schlafhygiene."))

            if critical_issues:
                recommendations.insert(0, ("👩‍⚕️", "Wenn es zu wiederholten oder signifikanten Abweichungen in Ihren Gesundheitsdaten kommt, empfehlen wir eventuell, einen Arzt aufzusuchen, um die Ergebnisse zu besprechen und weitere Schritte zu planen."))
            elif not recommendations: # If no specific recommendations but not all normal
                    recommendations.append(("💡", "Es wurden einige leichte Abweichungen festgestellt. Achten Sie weiterhin auf Ihre Gesundheitsparameter und Ihren Lebensstil."))

        return recommendations


def plot_abnormalities_over_time(df, age, gender):
    """
    Plots the health parameters over time, highlighting abnormal points and normal ranges.
    Assumes 'datetime' column exists and status columns (e.g., RHR_status) are present.
    """
    if df.empty or 'datetime' not in df.columns:
        st.warning("Keine Daten oder 'datetime'-Spalte für die Zeitverlaufsanalyse verfügbar.")
        return

    parameters = {
        "RHR": "Ruheherzfrequenz (bpm)",
        "HRV": "Herzfrequenz-Variabilität (ms)",
        "Temp": "Hauttemperatur (°C)",
        "Sleep": "Schlafscore (%)"
    }

    for param, title in parameters.items():
        if param not in df.columns or f"{param}_status" not in df.columns:
            continue # Skip if parameter or its status is missing

        st.subheader(f"Verlauf von {title}")

        fig = go.Figure()

        # Main line trace for the parameter value
        fig.add_trace(go.Scatter(
            x=df['datetime'],
            y=df[param],
            mode='lines+markers',
            name=f'{param} Verlauf',
            line=dict(color='blue'),
            marker=dict(size=6)
        ))

        # Add horizontal lines for normal ranges (only for RHR, HRV, Temp as Sleep has different thresholds)
        if param in ["RHR", "HRV", "Temp"]:
            param_range = AbnormalityChecker._get_range_for_person(age, gender, param)
            if param_range:
                min_val, max_val = param_range
                fig.add_hline(y=min_val, line_dash="dash", line_color="green", annotation_text="Untergrenze Normalbereich", annotation_position="bottom right", annotation_font_size=10)
                fig.add_hline(y=max_val, line_dash="dash", line_color="green", annotation_text="Obergrenze Normalbereich", annotation_position="top right", annotation_font_size=10)
            else:
                st.warning(f"Normalbereiche für {param} (Alter: {age}, Geschlecht: {gender}) konnten nicht gefunden werden.")


        # Checkbox to control visibility of abnormal points plot
        # Use a unique key for each checkbox to avoid errors
        show_abnormalities = st.checkbox(f"Zeige Status-Werte für {param}", value=True, key=f"checkbox_{param}_plot_status")

        if show_abnormalities:
            # Filter for abnormal points
            abnormal_points_df = df[~df[f"{param}_status"].isin(["Normal", "Hervorragend"])]

            if not abnormal_points_df.empty:
                fig.add_trace(go.Scatter(
                    x=abnormal_points_df['datetime'],
                    y=abnormal_points_df[param],
                    mode='markers',
                    name=f'{param} Status',
                    marker=dict(
                        color='red',
                        size=10,
                        symbol='circle',
                        line=dict(width=1, color='DarkSlateGrey')
                    ),
                    hoverinfo='text',
                    hovertext=[
                        f"Datum: {d.strftime('%Y-%m-%d %H:%M')}<br>Wert: {v}<br>Status: {s}"
                        for d, v, s in zip(abnormal_points_df['datetime'], abnormal_points_df[param], abnormal_points_df[f"{param}_status"])
                    ]
                ))

        fig.update_layout(
            xaxis_title="Datum",
            yaxis_title=param,
            hovermode="x unified",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)