
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
            # Korrekte Upload-URL für dein Dataset
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
            image_url = upload_result.get("image", {}).get("url")

            if not image_url:
                st.error("Fehler beim Abrufen der Bild-URL.")
                st.json(upload_result)
                st.stop()

            # Schritt 2: Bild-URL an Workflow senden (GET)
            workflow_url = "https://infer.roboflow.com/moritz-b/custom-workflow-6"
            response = requests.get(
                url=f"{workflow_url}?api_key={api_key}&image={image_url}"
            )

            result = response.json()

            # Debug (optional)
            # st.subheader("Rohdaten (Debug)")
            # st.json(result)

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
            st.error("Fehler bei der Verarbeitung.")
            st.exception(e)
