
import streamlit as st
import base64
import requests

st.set_page_config(page_title="Schlüssel-AI", layout="centered")

st.title("Schlüssel-AI: Verlorenen Schlüssel eimfach nachbestellen")
st.write("Lade ein Bild deines Schlosses hoch – wir sagen dir, welcher Schlüssel passt.")

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

            predictions = upload_result.get("predictions", [])
            if predictions:
                top_prediction = predictions[0]
                pred_class = top_prediction["class"]
                confidence = round(top_prediction["confidence"] * 100, 2)

                st.success(f"Erkannt: **{pred_class}** mit {confidence}% Sicherheit")

                if confidence < 60:
                    st.info("Hinweis: Die Erkennung war unsicher. Bildqualität oder Perspektive prüfen.")

                # Link zu zimmerschluessel.de
                link = f"https://www.zimmerschluessel.de/catalogsearch/result/?q={pred_class}"
                st.markdown(
                    f'<a href="{link}" target="_blank"><button style="background-color:#4CAF50;color:white;padding:10px;border:none;border-radius:5px;cursor:pointer;margin-top:10px;">Jetzt passenden Schlüssel ansehen</button></a>',
                    unsafe_allow_html=True
                )
            else:
                st.warning("Keine Vorhersage erhalten. Bitte versuche ein anderes Bild.")

        except Exception as e:
            st.error("Fehler bei der Verarbeitung.")
            st.exception(e)
