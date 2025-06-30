
class AbnormalityChecker:

    @staticmethod
    def check_rhr(rhr, age, gender):
        # Durchschnittswerte in Ruhe (bpm)
        if gender == "male":
            low, high = (45, 65) if age < 30 else (50, 70)
        else:
            low, high = (50, 70) if age < 30 else (55, 75)

        if rhr < low:
            return "🟥 Ruheherzfrequenz zu niedrig"
        elif rhr > high:
            return "🟥 Ruheherzfrequenz zu hoch"
        else:
            return "🟩 Ruheherzfrequenz im Normalbereich"

    @staticmethod
    def check_hrv(hrv, age, gender):
        # HRV stark altersabhängig, Frauen oft etwas höher
        if age < 30:
            threshold = 70 if gender == "male" else 75
        elif age < 50:
            threshold = 60 if gender == "male" else 65
        else:
            threshold = 50 if gender == "male" else 55

        if hrv < threshold:
            return "🟥 Niedrige Herzfrequenz-Variabilität"
        else:
            return "🟩 Herzfrequenz-Variabilität im Normalbereich"

    @staticmethod
    def check_skin_temp(temp_celsius):
        # Annahme: 32.0 – 35.0 °C normaler Bereich
        if temp_celsius < 32.0:
            return "🟥 Hauttemperatur zu niedrig"
        elif temp_celsius > 35.0:
            return "🟥 Hauttemperatur zu hoch"
        else:
            return "🟩 Hauttemperatur im Normalbereich"

    @staticmethod
    def check_sleep_score(score):
        # 0–100 %, Ziel: möglichst > 75 %
        if score < 60:
            return "🟥 Sehr schlechter Schlafscore"
        elif score < 75:
            return "🟨 Mittelmäßiger Schlafscore"
        else:
            return "🟩 Guter Schlafscore"
