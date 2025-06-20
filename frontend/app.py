import streamlit as st
import requests
import json
import time
import os # Import os for potential future use or to be consistent with backend

# --- Configuration ---
FASTAPI_URL = "http://127.0.0.1:8000" # Ensure your FastAPI backend is running on this host and port.

# --- Page Configuration ---
st.set_page_config(
    page_title="RAG-Toolkit",
    page_icon="📚",
    layout="wide"
)

# --- Session State Initialization ---
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"
if 'rag_history' not in st.session_state:
    st.session_state.rag_history = []
if 'rag_file_uploaded' not in st.session_state:
    st.session_state.rag_file_uploaded = False
if 'summary_text' not in st.session_state:
    st.session_state.summary_text = ""
if 'eval_history' not in st.session_state:
    st.session_state.eval_history = []
if 'eval_files_processed' not in st.session_state:
    st.session_state.eval_files_processed = False
if 'eval_context_file_data' not in st.session_state:
    st.session_state.eval_context_file_data = None
if 'eval_metrics_file_data' not in st.session_state:
    st.session_state.eval_metrics_file_data = None
if 'persistent_index_status' not in st.session_state:
    st.session_state.persistent_index_status = {}

# --- Sidebar ---
st.sidebar.title("RAG-Toolkit")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ("Dashboard", "RAG Chatbot", "Document Summarizer", "Evaluation Assistant", "Knowledge Base Manager"),
    index=["Dashboard", "RAG Chatbot", "Document Summarizer", "Evaluation Assistant", "Knowledge Base Manager"].index(st.session_state.page),
)
st.session_state.page = page

st.sidebar.markdown("---")

max_tokens = st.sidebar.slider(
    "Max Tokens",
    min_value=100,
    max_value=4096,
    value=st.session_state.get("max_tokens_sidebar", 512),
    step=100,
    help="Set the maximum number of tokens for generated responses."
)
st.session_state.max_tokens_sidebar = max_tokens
st.sidebar.write(f"Current Max Tokens: **{max_tokens}**")

st.sidebar.markdown("---")

if st.sidebar.button("Reset Current Page"):
    if st.session_state.page == "RAG Chatbot":
        st.session_state.rag_history = []
        st.session_state.rag_file_uploaded = False
    elif st.session_state.page == "Document Summarizer":
        st.session_state.summary_text = ""
    elif st.session_state.page == "Evaluation Assistant":
        st.session_state.eval_history = []
        st.session_state.eval_files_processed = False
        st.session_state.eval_context_file_data = None
        st.session_state.eval_metrics_file_data = None
    elif st.session_state.page == "Knowledge Base Manager":
        st.session_state.persistent_index_status = {}
    st.rerun()
    st.sidebar.info("Page reset initiated. Any inputs on this page might have been cleared.")

# --- Functions to interact with Persistent RAG Backend ---
@st.cache_data(ttl=5)
def get_persistent_index_status_cached():
    try:
        response = requests.get(f"{FASTAPI_URL}/persistent_rag/status/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching persistent index status: {e}")
        return {"error": str(e)}

def update_persistent_index_status():
    status = get_persistent_index_status_cached()
    st.session_state.persistent_index_status = status

if st.session_state.page == "Knowledge Base Manager":
    update_persistent_index_status()


# --- Main Content Area ---

if st.session_state.page == "Dashboard":
    st.markdown("<h1 style='text-align: center; color: #8a2be2;'>Welcome to the RAG-Toolkit!</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; font-size: 1.2em; margin-top: 30px;'>
            Your powerful suite for advanced document understanding, summarization, and intelligent chatbot interactions,
            all built with cutting-edge AI.
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💬 **Start Chatting**", help="Go to RAG Chatbot", use_container_width=True):
            st.session_state.page = "RAG Chatbot"
            st.rerun()
    with col2:
        if st.button("📄 **Summarize Documents**", help="Go to Document Summarizer", use_container_width=True):
            st.session_state.page = "Document Summarizer"
            st.rerun()

elif st.session_state.page == "RAG Chatbot":
    st.header("💬 RAG Chatbot")
    st.markdown("---")

    persistent_status = get_persistent_index_status_cached()
    if persistent_status.get("is_loaded_in_memory") == "True" and int(persistent_status.get("chunk_count", 0)) > 0:
        st.info(f"Using **Global Knowledge Base** with {persistent_status.get('chunk_count')} chunks for augmented RAG.")
        global_kb_active = True
    else:
        st.warning("Global Knowledge Base is not loaded or is empty. RAG will only use session-specific documents if uploaded.")
        global_kb_active = False

    st.write("Upload a document (PDF, TXT, JSON) to ground your chat for this session, or rely on the Global Knowledge Base if active.")

    uploaded_file = st.file_uploader("Upload Session Document (Optional)", type=["pdf", "txt", "json"], key="rag_uploader")

    if uploaded_file is not None and not st.session_state.rag_file_uploaded:
        with st.spinner(f"Uploading and processing '{uploaded_file.name}'..."):
            try:
                files = {'files': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                response = requests.post(f"{FASTAPI_URL}/rag/upload_files/", files=files)
                response.raise_for_status()

                st.success(f"File **'{uploaded_file.name}'** processed successfully for RAG! You can now chat with its content.")
                st.session_state.rag_file_uploaded = True
                st.session_state.rag_history = []
                st.rerun()
            except requests.exceptions.RequestException as e:
                st.error(f"Error processing file: {e}")
                st.session_state.rag_file_uploaded = False
                st.session_state.rag_history = []
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                st.session_state.rag_file_uploaded = False
                st.session_state.rag_history = []
    elif uploaded_file is None and st.session_state.rag_file_uploaded:
        st.success("Session document previously processed for RAG. You can now chat.")

    st.markdown("---")
    st.subheader("Chat History")

    chat_enabled = st.session_state.rag_file_uploaded or global_kb_active

    if not st.session_state.rag_history:
        if not chat_enabled:
            st.info("Upload a session document OR build/load the Global Knowledge Base to enable chat.")
        else:
            st.info("No messages yet. Type in the box below to start a conversation!")
    else:
        for role, content in st.session_state.rag_history:
            with st.chat_message(role):
                if role == "user":
                    st.markdown(content)
                elif role == "assistant":
                    # Assistant's content is now a dict with 'answer' and 'image_urls'
                    st.markdown(content['answer'])
                    if content['image_urls']:
                        st.markdown("**Relevant Images:**")
                        # Use columns for a grid-like layout of thumbnails
                        cols = st.columns(3) # Display up to 3 images per row
                        for i, image_url in enumerate(content['image_urls']):
                            with cols[i % 3]:
                                try:
                                    # Extract image name for display
                                    image_name_from_url = os.path.basename(image_url)
                                    # Create an expander for each image
                                    with st.expander(f"View {image_name_from_url}", expanded=False):
                                        # Display full-size image inside the expander
                                        st.image(image_url, caption=f"Full Size: {image_name_from_url}", use_container_width=True)
                                        # Optionally, fetch and display more metadata here if the backend provided it
                                        # (e.g., if image_urls also included dicts with 'image_name', 'labels' etc.)
                                except Exception as img_e:
                                    st.warning(f"Could not display image from {image_url}: {img_e}")

    chat_input = st.chat_input("Ask a question about the document...", disabled=not chat_enabled)
    if chat_input:
        st.chat_message("user").write(chat_input)
        st.session_state.rag_history.append(("user", chat_input)) # Store user message as string

        with st.spinner("AI is thinking..."):
            try:
                formatted_history_for_backend = []
                # Iterate through history to format for backend.
                # Note: `content` for assistant is now a dict, so we need to extract 'answer'.
                # The history for the backend should be (question_str, answer_str) tuples.
                for i in range(0, len(st.session_state.rag_history) -1, 2):
                    if (i + 1) < len(st.session_state.rag_history):
                        user_msg_text = st.session_state.rag_history[i][1]
                        # For assistant's previous responses, extract the 'answer' text
                        ai_msg_content = st.session_state.rag_history[i+1][1]
                        ai_msg_text = ai_msg_content.get('answer', '') if isinstance(ai_msg_content, dict) else ai_msg_content
                        formatted_history_for_backend.append((user_msg_text, ai_msg_text))

                payload = {
                    "question": chat_input,
                    "history": formatted_history_for_backend,
                    "max_tokens": max_tokens
                }
                
                # IMPORTANT: Specify response_model for the frontend request as well
                # FastAPI will automatically parse it, but requests library returns raw JSON
                response = requests.post(f"{FASTAPI_URL}/rag/chat/", json=payload)
                response.raise_for_status()

                # Get the full response dictionary
                backend_response_data = response.json()
                
                # Check if 'answer' key exists, provide default if not
                ai_response_text = backend_response_data.get("answer", "Error: No answer from AI.")
                # Get image URLs, provide empty list if not present
                returned_image_urls = backend_response_data.get("image_urls", [])

                # Store the full dictionary content for the assistant's message in history
                st.session_state.rag_history.append(("assistant", {"answer": ai_response_text, "image_urls": returned_image_urls}))
                
                # Re-run to display the new messages (and images)
                st.rerun()

            except requests.exceptions.RequestException as e:
                st.error(f"Error communicating with RAG backend: {e}")
                st.chat_message("assistant").write("Sorry, I'm having trouble connecting to the RAG system right now. Please ensure the backend is running and a permanent index is loaded, or a session document is uploaded.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                st.chat_message("assistant").write("An unexpected error occurred while processing your request.")


elif st.session_state.page == "Document Summarizer":
    st.header("📄 Document Summarizer")
    st.markdown("---")
    st.write("Upload a document (PDF, TXT, JSON) to get a concise summary.")

    uploaded_summary_file = st.file_uploader("Drag & drop your document here, or click to upload", type=["pdf", "txt", "json"], key="summarizer_uploader")

    if uploaded_summary_file is not None:
        if st.button("Generate Summary", key="generate_summary_btn"):
            st.session_state.summary_text = ""
            with st.spinner(f"Generating summary for '{uploaded_summary_file.name}'... This may take a moment."):
                try:
                    files = {'file': (uploaded_summary_file.name, uploaded_summary_file.getvalue(), uploaded_summary_file.type)}
                    
                    data = {
                        "num_clusters": 10,
                        "max_tokens": max_tokens
                    }

                    response = requests.post(f"{FASTAPI_URL}/summarizer/summarize_document/", files=files, data=data)
                    response.raise_for_status()

                    st.session_state.summary_text = response.json().get("summary", "Error: No summary from AI.")
                    st.success("Summary generated!")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error generating summary: {e}. Please check the backend server logs.")
                    st.session_state.summary_text = "Error: Could not retrieve summary. " + str(e)
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
                    st.session_state.summary_text = "Error: An unexpected error occurred. " + str(e)
    
    st.markdown("---")
    st.subheader("Summary Preview")
    
    if st.session_state.summary_text:
        st.text_area(
            "Summary",
            st.session_state.summary_text,
            height=300,
            disabled=False
        )
        st.download_button(
            label="Download Summary",
            data=st.session_state.summary_text,
            file_name="summary.txt",
            mime="text/plain",
            help="Download the generated summary as a text file."
        )
    else:
        st.info("Upload a document and click 'Generate Summary' to see its summary.")


elif st.session_state.page == "Evaluation Assistant":
    st.header("✅ Evaluation Assistant")
    st.markdown("---")

    st.write("Upload your **context file** (PDF/JSON) and **metrics JSON file** together to begin evaluation.")

    col1, col2 = st.columns(2)
    with col1:
        context_file_uploader = st.file_uploader("Upload Context File (PDF, JSON)", type=["pdf", "json"], key="eval_context_uploader")
        if context_file_uploader is not None:
            st.session_state.eval_context_file_data = (context_file_uploader.name, context_file_uploader.getvalue(), context_file_uploader.type)
        else:
            st.session_state.eval_context_file_data = None 

    with col2:
        metrics_file_uploader = st.file_uploader("Upload Metrics JSON File", type=["json"], key="eval_metrics_uploader")
        if metrics_file_uploader is not None:
            st.session_state.eval_metrics_file_data = (metrics_file_uploader.name, metrics_file_uploader.getvalue(), metrics_file_uploader.type)
        else:
            st.session_state.eval_metrics_file_data = None

    if st.button("Process Evaluation Files", key="process_eval_files_btn"):
        if st.session_state.eval_context_file_data is None or st.session_state.eval_metrics_file_data is None:
            st.warning("Please upload both a context file and a metrics JSON file.")
        else:
            st.session_state.eval_files_processed = False
            st.session_state.eval_history = []
            with st.spinner(f"Processing files... This may take a moment."):
                try:
                    files = {
                        'context_file': st.session_state.eval_context_file_data,
                        'metrics_file': st.session_state.eval_metrics_file_data
                    }
                    
                    response = requests.post(f"{FASTAPI_URL}/evaluator/upload_eval_files/", files=files)
                    response.raise_for_status()

                    st.success(f"Context and Metrics files processed successfully! You can now ask questions.")
                    st.session_state.eval_files_processed = True
                except requests.exceptions.RequestException as e:
                    st.error(f"Error processing evaluation files: {e}. Please check backend logs.")
                    st.session_state.eval_files_processed = False
                    st.session_state.eval_history = []
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
                    st.session_state.eval_files_processed = False
                    st.session_state.eval_history = []
    
    if st.session_state.eval_context_file_data:
        st.info(f"Context file ready: {st.session_state.eval_context_file_data[0]}")
    else:
        st.info("No Context file uploaded yet.")

    if st.session_state.eval_metrics_file_data:
        st.info(f"Metrics file ready: {st.session_state.eval_metrics_file_data[0]}")
    else:
        st.info("No Metrics file uploaded yet.")

    st.markdown("---")
    st.subheader("Evaluation Feedback Chat")

    if not st.session_state.eval_files_processed:
        st.info("Upload and process your context and metrics files above to enable the evaluation chat.")
    else:
        if not st.session_state.eval_history:
            st.info("Files processed. Type your question below to get feedback!")
        else:
            for role, message in st.session_state.eval_history:
                with st.chat_message(role):
                    st.markdown(message)

        eval_chat_input = st.chat_input("Ask a question about the evaluation...")
        if eval_chat_input:
            st.chat_message("user").write(eval_chat_input)
            st.session_state.eval_history.append(("user", eval_chat_input))

            with st.spinner("AI is analyzing evaluation data..."):
                try:
                    formatted_history_for_backend = []
                    for i in range(0, len(st.session_state.eval_history) -1, 2):
                        if (i + 1) < len(st.session_state.eval_history):
                            user_msg = st.session_state.eval_history[i][1]
                            ai_msg = st.session_state.eval_history[i+1][1]
                            formatted_history_for_backend.append((user_msg, ai_msg))

                    history_payload = json.dumps(formatted_history_for_backend)

                    payload_data = {
                        "question": eval_chat_input,
                        "history": history_payload,
                        "max_tokens": max_tokens
                    }

                    response = requests.post(f"{FASTAPI_URL}/evaluator/ask_evaluation/", json=payload_data)
                    response.raise_for_status()

                    ai_feedback = response.json().get("feedback", "Error: No feedback from AI.")
                    st.chat_message("assistant").write(ai_feedback)
                    st.session_state.eval_history.append(("assistant", ai_feedback))

                except requests.exceptions.RequestException as e:
                    st.error(f"Error communicating with Evaluation backend: {e}")
                    st.chat_message("assistant").write("Sorry, I'm having trouble connecting to the evaluation system right now.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
                    st.chat_message("assistant").write("An unexpected error occurred while processing your request.")

elif st.session_state.page == "Knowledge Base Manager":
    st.header("🗄️ Knowledge Base Manager")
    st.markdown("---")

    st.write("""
        Upload documents (PDF, TXT, JSON) to build or update your **permanent Global Knowledge Base**.
        This index will persist across application restarts and will be automatically
        used to augment responses in the RAG Chatbot.
    """)

    uploaded_kb_files = st.file_uploader(
        "Upload files for Global Knowledge Base (PDF, TXT, JSON)",
        type=["pdf", "txt", "json"],
        accept_multiple_files=True,
        key="kb_uploader"
    )

    if st.button("Build/Update Permanent Index", key="build_kb_btn"):
        if not uploaded_kb_files:
            st.warning("Please upload at least one file to build/update the permanent index.")
        else:
            with st.spinner("Building permanent index... This may take a while depending on file size."):
                files_to_send = []
                for file in uploaded_kb_files:
                    files_to_send.append(('files', (file.name, file.getvalue(), file.type)))
                
                try:
                    response = requests.post(f"{FASTAPI_URL}/persistent_rag/upload_and_index/", files=files_to_send)
                    response.raise_for_status()
                    st.success(response.json().get("message", "Permanent index updated!"))
                    st.session_state.persistent_index_status = {}
                    update_persistent_index_status()
                except requests.exceptions.RequestException as e:
                    st.error(f"Error building permanent index: {e}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")

    st.markdown("---")
    st.subheader("Manage Existing Index")

    col_del, col_refresh = st.columns(2)
    with col_del:
        if st.button("Delete Permanent Index", key="delete_kb_btn"):
            if st.session_state.persistent_index_status.get("files_exist_on_disk") == "True":
                if st.button("Confirm Delete (This is permanent!)", key="confirm_delete_kb_btn"):
                    with st.spinner("Deleting permanent index..."):
                        try:
                            response = requests.post(f"{FASTAPI_URL}/persistent_rag/delete_index/")
                            response.raise_for_status()
                            st.success(response.json().get("message", "Permanent index deleted."))
                            st.session_state.persistent_index_status = {}
                            update_persistent_index_status()
                        except requests.exceptions.RequestException as e:
                            st.error(f"Error deleting permanent index: {e}")
                        except Exception as e:
                            st.error(f"An unexpected error occurred: {e}")
                else:
                    st.info("Click 'Confirm Delete' again to proceed with permanent deletion.")
            else:
                st.info("No permanent index found on disk to delete.")
    with col_refresh:
        if st.button("Refresh Index Status", key="refresh_kb_status_btn"):
            st.session_state.persistent_index_status = {}
            update_persistent_index_status()
            st.success("Status refreshed!")

    st.markdown("---")
    st.subheader("Current Permanent Index Status")
    
    if st.session_state.persistent_index_status:
        status = st.session_state.persistent_index_status
        st.write(f"**Loaded in Memory:** {status.get('is_loaded_in_memory')}")
        st.write(f"**Files Exist on Disk:** {status.get('files_exist_on_disk')}")
        st.write(f"**Number of Chunks:** {status.get('chunk_count')}")
        st.write(f"**Storage Path:** `{status.get('persistent_dir')}`")
    else:
        st.info("Fetching permanent index status...")
        update_persistent_index_status()
        st.empty()

