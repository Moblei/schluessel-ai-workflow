
import streamlit as st
import base64
import requests
import urllib.parse

st.set_page_config(page_title="Schlüssel-AI", layout="centered")

st.title("Schlüssel-AI: Erkenne deinen Schlüsseltyp")
st.write("Lade ein Bild deines Schlosses hoch – wir sagen dir, welcher Schlüsseltyp passt.")

uploaded_file = st.file_uploader("Bild auswählen", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image_bytes = uploaded_file.read()
    st.image(image_bytes, caption="Hochgeladenes Bild", use_container_width=True)

    # Bild in Base64 umwandeln und URL-encoden
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    image_base64_encoded = urllib.parse.quote_plus(image_base64)

    with st.spinner("Analyse läuft..."):
        try:
            api_url = "https://infer.roboflow.com/moritz-b/custom-workflow-6"
            api_key = st.secrets["API_KEY"]

            response = requests.get(
                url=f"{api_url}?api_key={api_key}&image={image_base64_encoded}"
            )

            result = response.json()

            # Debug anzeigen (optional)
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
            st.error("Fehler bei der Anfrage an Roboflow.")
            st.exception(e)
