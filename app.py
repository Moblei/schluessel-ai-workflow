
import streamlit as st
import base64
import requests

st.set_page_config(page_title="Schlüssel-AI", layout="centered")

st.title("Schlüssel-AI: Erkenne deinen Schlüsseltyp")
st.write("Lade ein Bild deines Schlosses hoch – wir sagen dir, welcher Schlüsseltyp passt.")

uploaded_file = st.file_uploader("Bild auswählen", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image_bytes = uploaded_file.read()
    st.image(image_bytes, caption="Hochgeladenes Bild", use_container_width=True)

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    with st.spinner("Analyse läuft..."):
        try:
            api_url = "https://infer.roboflow.com/moritz-b/custom-workflow-6"
            api_key = st.secrets["API_KEY"]

            response = requests.post(
                url=f"{api_url}?api_key={api_key}",
                json={"image": image_base64}
            )

            # Fehlerbehandlung: wenn Response leer oder kein JSON
            try:
                result = response.json()
            except Exception:
                st.error("Roboflow hat keine gültige Antwort zurückgegeben.")
                st.text(f"Status: {response.status_code}")
                st.text(response.text)
                st.stop()

            # Debug (optional)
            st.subheader("Rohdaten (Debug)")
            st.json(result)

            predictions = []
            if isinstance(result, list):
                if len(result) > 0 and "predictions" in result[0]:
                    predictions = result[0]["predictions"]
            elif "predictions" in result:
                predictions = result["predictions"]

            if predictions and len(predictions) > 0:
                top_prediction = predictions[0]
                confidence = round(top_prediction['confidence'] * 100, 2)
                st.success(f"Erkannt: **{top_prediction['class']}** mit {confidence}% Sicherheit")
                if confidence < 60:
                    st.info("Hinweis: Die Erkennung war unsicher. Bildqualität oder Perspektive prüfen.")
            else:
                st.warning("Keine Vorhersage erhalten. Bitte versuche ein anderes Bild.")

        except Exception as e:
            st.error("Fehler bei der Anfrage an Roboflow.")
            st.exception(e)
