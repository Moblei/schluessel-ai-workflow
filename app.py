
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

    with st.spinner("Bild wird vorbereitet..."):
        try:
            # Upload zur Roboflow Dataset API
            upload_url = "https://detect.roboflow.com/schluessel_ai_classification_2/1"
            api_key = st.secrets["API_KEY"]

            response_upload = requests.post(
                url=f"{upload_url}?api_key={api_key}",
                files={"file": image_bytes},
            )

            if response_upload.status_code != 200:
                st.error("Fehler beim Hochladen des Bildes zu Roboflow.")
                st.text(response_upload.text)
                st.stop()

            upload_result = response_upload.json()

            # Debug anzeigen (optional)
            # st.subheader("Rohdaten (Debug)")
            # st.json(upload_result)

            predictions = upload_result.get("predictions", [])
            if predictions:
                top_prediction = predictions[0]
                confidence = round(top_prediction['confidence'] * 100, 2)
                st.success(f"Erkannt: **{top_prediction['class']}** mit {confidence}% Sicherheit")
                if confidence < 60:
                    st.info("Hinweis: Die Erkennung war unsicher. Bildqualität oder Perspektive prüfen.")
            else:
                st.warning("Keine Vorhersage erhalten. Bitte versuche ein anderes Bild.")

        except Exception as e:
            st.error("Fehler bei der Verarbeitung.")
            st.exception(e)
