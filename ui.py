import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="AI Teaching Assistant",
    page_icon="📘",
    layout="centered",
)

st.title("AI Teaching Assistant")
st.write("Upload course material, create a teaching plan, learn a topic, and ask questions.")


if "document_id" not in st.session_state:
    st.session_state.document_id = None

if "filename" not in st.session_state:
    st.session_state.filename = None


uploaded_file = st.file_uploader(
    "Upload course material",
    type=["pdf"],
)


if uploaded_file and st.button("Upload PDF"):
    response = requests.post(
        f"{API_URL}/documents",
        files={
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                "application/pdf",
            )
        },
    )

    if response.ok:
        data = response.json()

        st.session_state.document_id = data["document_id"]
        st.session_state.filename = data["filename"]

        st.success(
            f"{data['filename']} uploaded successfully."
        )
    else:
        st.error(response.text)


if st.session_state.document_id:
    st.divider()

    st.subheader(st.session_state.filename)

    if st.button("Create Teaching Plan"):
        response = requests.post(
            f"{API_URL}/plan",
            json={
                "document_id": st.session_state.document_id
            },
        )

        if response.ok:
            st.markdown(response.json()["plan"])
        else:
            st.error(response.text)

    st.divider()

    st.subheader("Teach a Topic")

    topic = st.text_input(
        "Topic",
        placeholder="Example: Model Evaluation and Overfitting",
    )

    if st.button("Teach"):
        if topic:
            response = requests.post(
                f"{API_URL}/teach",
                json={
                    "document_id": st.session_state.document_id,
                    "topic": topic,
                },
            )

            if response.ok:
                data = response.json()

                st.markdown(data["explanation"])

                with st.expander("Sources"):
                    for source in data["sources"]:
                        st.write(
                            f"Page {source['page']} — similarity: {source['score']}"
                        )
            else:
                st.error(response.text)

    st.divider()

    st.subheader("Ask a Question")

    question = st.text_input(
        "Question",
        placeholder="Example: What is machine learning?",
    )

    if st.button("Ask"):
        if question:
            response = requests.post(
                f"{API_URL}/ask",
                json={
                    "document_id": st.session_state.document_id,
                    "question": question,
                },
            )

            if response.ok:
                data = response.json()

                st.markdown(data["answer"])

                with st.expander("Sources"):
                    for source in data["sources"]:
                        st.write(
                            f"Page {source['page']} — similarity: {source['score']}"
                        )
            else:
                st.error(response.text)
