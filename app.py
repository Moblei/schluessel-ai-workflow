
import streamlit as st

try:
    import cv2
    st.success("cv2 wurde erfolgreich geladen.")
    
except ImportError as e:
    st.error("OpenCV konnte nicht geladen werden.")
    st.exception(e)
st.set_page_config(page_title="Schlüssel-AI", layout="centered")

st.title("Schlüssel-AI: Erkenne deinen Schlüsseltyp")
st.write("Lade ein Bild deines Schlosses hoch – wir sagen dir, welcher Schlüsseltyp passt.")

uploaded_file = st.file_uploader("Bild auswählen", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image_bytes = uploaded_file.read()
    st.image(image_bytes, caption="Hochgeladenes Bild", use_column_width=True)

    with st.spinner("Analyse läuft..."):
        try:
            client = InferenceHTTPClient(
                api_url="https://infer.roboflow.com",
                api_key=st.secrets["API_KEY"]
            )

            result = client.run_workflow(
                workspace_name="moritz-b",
                workflow_id="custom-workflow-6",
                images={"image": image_bytes},
                use_cache=True
            )

            predictions = result.get("predictions", [])
            if predictions:
                top_prediction = predictions[0]
                st.success(f"Erkannt: **{top_prediction['class']}** mit {round(top_prediction['confidence'] * 100, 2)}% Sicherheit")
            else:
                st.warning("Keine zuverlässige Vorhersage möglich. Bitte versuche ein anderes Bild.")

        except Exception as e:
            st.error("Fehler bei der Anfrage an Roboflow.")
            st.exception(e)
