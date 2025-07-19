import streamlit as st
from PyPDF2 import PdfReader
import docx2txt
import os
from PIL import Image
from fpdf import FPDF
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from dotenv import load_dotenv

# ✅ STEP 1: Load API Keys from .env
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")
 
# ✅ STEP 2: Streamlit Page Settings and CSS
st.set_page_config(page_title="BoTfOliO🤖")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Piazzolla&display=swap');

    html, body, [class*="css"] {
        font-family: 'Piazzolla', serif !important;
    }

    .stApp {
        background: rgba(0, 8, 17, 1);
    }

    .centered-title {
        text-align: left;
        font-size: 48px;
        font-weight: 600;
    }

    .subtext {
        text-align: center;
        font-size: 22px;
        color: #5C4F4F;
    }

    div.stButton > button {
        background: rgba(112, 88, 63, 1);
        color: rgba(226, 226, 226, 1);
        border-radius: 10px;
        font-size: 18px;
        font-family: 'Piazzolla', serif;
    }

    .stFileUploader {
        background-color: rgba(112, 88, 63, 0.2);
        padding: 12px;
        border-radius: 12px;
        font-family: 'Piazzolla', serif;
    }

    .stFileUploader label {
        background-color: rgba(112, 88, 63, 1);
        color: white;
        border-radius: 8px;
        padding: 6px 12px;
        font-family: 'Piazzolla', serif;
    }

    h1, h2, h3, h4, h5, h6, p, span, label, div {
        font-family: 'Piazzolla', serif !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='centered-title'>BoTfOliO🤖</div>", unsafe_allow_html=True)

# ✅ STEP 3: File Uploaders
resume_file = st.file_uploader("📄 Upload your Resume", type=["pdf", "docx", "txt"])

# ✅ STEP 4: Read File Function
def read_file(file):
    if file.name.endswith(".pdf"):
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif file.name.endswith(".docx"):
        return docx2txt.process(file)
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    return ""

# ✅ STEP 5: Save as PDF Function
def save_as_pdf(content, filename="BoTfOliO_Report.pdf"):
    import re

    def clean_text(text):
        text = text.replace("—", "-")
        text = text.replace("“", '"').replace("”", '"').replace("’", "'")
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        return text

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    clean_content = clean_text(content)
    for line in clean_content.split('\n'):
        pdf.multi_cell(0, 10, txt=line)

    pdf.output(filename)

# ✅ STEP 6: Analyze Button
if st.button("🔍 Analyze"):
    try:
            st.warning("Please upload your resume.")
            with st.spinner("Analyzing with AI🤖..."):
                resume_text = read_file(resume_file)[:5000]

                if resume_text.strip() == "" == "":
                    st.error("❌ One or both files contain no readable text.")
                else:
                    llm = ChatOpenAI(
                        openai_api_key=OPENROUTER_API_KEY,
                        base_url="https://openrouter.ai/api/v1",
                        model="deepseek/deepseek-chat:free",
                        temperature=0.3,
                        max_tokens=900,
                    )

                    prompt_template = """
                    You are an AI resume evaluator. Evaluate the resume and provide:

                    1. Summary of alignment
                    2. Strengths in the resume
                    3. Missing skills or qualifications
                    4. Suggestions for improvement
                    5. corrected version of uploaded resume
                    6. Write a cover letter for this resume and job description
                    
                    RESUME:
                    {context}

                    """

                    prompt = PromptTemplate(
                        input_variables=["context", "question"],
                        template=prompt_template,
                    )

                    chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)

                    result = chain.run(
                        input_documents=[Document(page_content=resume_text)],
                       
                    )

                    st.success("✅ HERE WE GOT IT!")
                    st.write(result)

                    # Save and offer PDF download
                    save_as_pdf(result)
                    with open("BoTfOliO_Report.pdf", "rb") as f:
                        st.download_button(
                            label="📥 Download PDF Report",
                            data=f,
                            file_name="BoTfOliO_Report.pdf",
                            mime="application/pdf"
                        )

    except Exception as e:
        st.error(f"❌ Something went wrong: {e}")

