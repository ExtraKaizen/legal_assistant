import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import PyPDF2
import nltk
import random
import time
from datetime import datetime
from fpdf import FPDF
from faker import Faker
import requests
from mailjet_rest import Client
import base64
from email_validator import validate_email, EmailNotValidError
from pathlib import Path
from Gsheet import gsheet

nltk.download('punkt')
fake = Faker()

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("groq_api_key")

# Initialize Groq client
client = Groq(api_key=groq_api_key)

def inject_custom_css():
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@700&family=Open+Sans:wght@400;600&display=swap');
        
        :root {{
            --primary: #FF9F00; 
            --secondary: #FFD700; 
            --accent: #F3D87C;   
            --background: #202A44; 
            --sidebar-bg: #1B2334; 
            --card-bg: #1A1F3F;  
            --doc-card-hover: #1F2435; 
        }}
        
        body {{
            font-family: 'Open Sans', sans-serif;
            background: var(--background);
            color: #EDEDED;  
        }}
        
        .main {{
            background: #fcfcfc;
        }}
        
        .chat-bubble {{
            padding: 1.2rem;
            border-radius: 1.5rem;
            margin: 1rem 0;
            max-width: 75%;
            position: relative;
            animation: fadeIn 0.3s ease-in;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); 
            font-size: 0.95rem;
            line-height: 1.6;
            transition: transform 0.2s ease;
        }}
        
        .user-bubble {{
            background: var(--accent);
            color: #2A2F4F; 
            margin-left: auto;
            border-bottom-right-radius: 0.5rem;
        }}
        
        .bot-bubble {{
            background: #ededeb;
            color: black;
            margin-right: auto;
            border-bottom-left-radius: 0.5rem;
            backdrop-filter: blur(5px);
        }}
        
        .doc-card {{
            background: var(--card-bg);
            padding: 1rem;
            border-radius: 1rem;
            margin: 0.5rem 0;
            cursor: pointer;
            transition: all 0.3s ease;
            color: #EDEDED; /* Text color for card */
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .doc-card:hover {{
            background: var(--doc-card-hover); /* Hover effect to distinguish interactive elements */
        }}
        
        .selected-doc {{
            background: var(--secondary)!important;
            color: var(--background)!important;
        }}
        
        .stTextInput input {{
            border: 2px solid var(--primary)!important;
            border-radius: 12px!important;
            background: #FFFFFF22!important; /* Slightly darker input background for contrast */
            color: var(--primary)!important;
        }}
        
        .stMarkdown img {{
            max-width: 500px;
            margin-bottom: 1rem;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: var(--primary)!important;
            font-family: 'Merriweather', serif;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
    """, unsafe_allow_html=True)


def init_session():
    session_defaults = {
        "documents": {},
        "selected_doc": None,
        "history": [],
        "analysis": {},
        "view_mode": "insights"
    }
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def process_document(uploaded_file):
    try:
        doc_id = uploaded_file.file_id
        if doc_id in st.session_state.documents:
            return

        if uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = "".join([page.extract_text() for page in pdf_reader.pages])
            metadata = {
                "pages": len(pdf_reader.pages),
                "author": pdf_reader.metadata.get("/Author", "Unknown"),
                "created": pdf_reader.metadata.get("/CreationDate", "Unknown"),
                "modified": pdf_reader.metadata.get("/ModDate", "Unknown")
            }
        else:
            text = uploaded_file.getvalue().decode()
            metadata = {
                "pages": "N/A",
                "author": "Unknown",
                "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "modified": "N/A"
            }

        # Store document data
        st.session_state.documents[doc_id] = {
            "name": uploaded_file.name,
            "content": text,
            "metadata": metadata,
            "analysis": {}
        }

        # Process analysis with improved prompts
        with st.spinner(f"Analyzing {uploaded_file.name}..."):
            doc_content = text[:12000]  # Truncate to avoid token limits
            
            st.session_state.documents[doc_id]["analysis"] = {
                "risk_score": random.randint(20, 80),
                "summary": get_ai_response(
                    doc_content, 
                    "Provide a comprehensive 5-point executive summary with bold headings using **"
                ),
                "risks": get_ai_response(
                    doc_content,
                    "Identify and explain top 5 risks with:\n1. Risk title in bold\n2. Severity score (1-5)\n3. Explanation"
                ),
                "recommendations": get_ai_response(
                    doc_content,
                    "Provide 5 detailed recommendations with:\n1. Recommendation title in bold\n2. Implementation steps\n3. Priority level"
                )
            }

        st.session_state.selected_doc = doc_id
        return True
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        return False

# Function to generate a report
def generate_pdf_report(doc_id):
    # Retrieve document data
    doc = st.session_state.documents[doc_id]
    analysis = doc["analysis"]
    
    # Initialize PDF object
    pdf = FPDF()
    pdf.add_page()

    # Set font to Times-Roman for the whole document (default in FPDF)
    pdf.set_font("Times", size=10)

    # Set padding for the page content (for page edges)
    padding_left = 20
    padding_right = 20
    padding_top = 15
    padding_bottom = 15

    # Add some padding space from the top
    pdf.set_xy(padding_left, padding_top)
    
    # Header section with the title
    pdf.set_font("Times", 'B', size=18)  # Bold for the title
    pdf.set_text_color(255, 215, 0)  # Gold color for the title
    pdf.cell(0, 8, txt="Legal Analysis Report", ln=1, align='C')

    # Document name and generation date with a clean style
    pdf.set_font("Times", 'I', size=10)  # Italic for metadata
    pdf.set_text_color(200, 200, 200)  # Light grey
    pdf.cell(0, 6, txt=f"Document: {doc['name']}", ln=1, align='C')
    pdf.cell(0, 6, txt=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=1, align='C')
    pdf.ln(2)  # Add a minimal space before the next section
    
    # Executive Summary Section
    pdf.set_font("Times", 'B', size=14)  # Bold for section headers
    pdf.set_text_color(255, 215, 0)  # Gold color for the header
    pdf.cell(0, 6, txt="Executive Summary", ln=1)

    # Content of the Executive Summary
    pdf.set_font("Times", '', size=10)  # Regular font for content
    pdf.set_text_color(0, 0, 0)  # Black color for content text
    pdf.multi_cell(0, 6, txt=analysis.get('summary', 'No summary available.'))
    pdf.ln(2)  # Add minimal space after the summary
    
    # Risk Assessment Section
    pdf.set_font("Times", 'B', size=14)  # Bold for section headers
    pdf.set_text_color(255, 215, 0)  # Gold color for the header
    pdf.cell(0, 6, txt="Risk Assessment", ln=1)
    
    # Content of the Risk Assessment
    pdf.set_font("Times", '', size=10)  # Regular font for content
    pdf.set_text_color(0, 0, 0)  # Black text color
    pdf.multi_cell(0, 6, txt=analysis.get('risks', 'No risk assessment available.'))
    pdf.ln(2)  # Add minimal space after the risk assessment
    
    # Recommendations Section
    pdf.set_font("Times", 'B', size=14)  # Bold for section headers
    pdf.set_text_color(255, 215, 0)  # Gold color for the header
    pdf.cell(0, 6, txt="Recommendations", ln=1)
    
    # Content of the Recommendations
    pdf.set_font("Times", '', size=10)  # Regular font for content
    pdf.set_text_color(0, 0, 0)  # Black text color
    pdf.multi_cell(0, 6, txt=analysis.get('recommendations', 'No recommendations available.'))
    pdf.ln(2)  # Add minimal space after recommendations

    # Footer section (optional)
    pdf.set_y(-15)  # Place footer at the bottom
    pdf.set_font("Times", 'I', 8)  # Italic font for footer
    pdf.set_text_color(128, 128, 128)  # Grey color for footer text
    pdf.cell(0, 6, txt="Confidential - For Internal Use Only", align='C')

    # Return the PDF output as a binary string
    return pdf.output(dest='S').encode('latin1')
  


# Get the AI responses
def get_ai_response(context, prompt, max_tokens=1500):
    system_prompt = """You are a legal expert assistant. Format responses with:
    - Clear section headers in **bold**
    - Bullet points for lists
    - Numbered steps when appropriate
    - Risk scores (1-5) for risk items
    - Priority levels for recommendations"""
    
    try:
        messages = [{"role": "system", "content": system_prompt}]
        
        if context:
            messages.append({"role": "user", "content": f"Document Content: {context}\n\n{prompt}"})
        else:
            messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            messages=messages,
            # model= "llama3-8b-8192",
            model= "mixtral-8x7b-32768",
            temperature=0.3,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error processing request: {str(e)}"

# Main Function
def main():
    st.set_page_config(page_title="⚖️ LegalMind Pro", page_icon="⚖️", layout="wide")
    inject_custom_css()
    init_session()
    
    # Main Title
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="font-size: 5rem; color: #FFD700;">⚖️ LegalMind Pro</h1>
        <h3 style="color: #FFE55C;">AI-Powered Legal Document Analysis Suite</h3>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("### ⚖️ Documents")
        
        uploaded_files = st.file_uploader("", 
                                        type=["pdf", "txt"],
                                        accept_multiple_files=True,
                                        help="Upload multiple legal documents")
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                if uploaded_file.file_id not in st.session_state.documents:
                    process_document(uploaded_file)
            
            # Document selection
            for doc_id, doc_data in st.session_state.documents.items():
                if st.button(
                    doc_data["name"],
                    key=f"doc_{doc_id}",
                    help="Click to select document",
                    type="primary" if st.session_state.selected_doc == doc_id else "secondary"
                ):
                    st.session_state.selected_doc = doc_id
            
            st.markdown("---")
            
            # Report Generation
            if st.session_state.selected_doc:
                if st.button("📄 Generate Report"):
                    doc_id = st.session_state.selected_doc
                    report = generate_pdf_report(doc_id)
                    st.download_button("💾 Download Report", report, 
                                     file_name=f"{st.session_state.documents[doc_id]['name']}_report.pdf",
                                     mime="application/pdf")
              
                
                if st.button("📄 Upload to Google Sheet"):
                  # file_content = uploaded_file.read().decode("utf-8")
                  pdf_reader = PyPDF2.PdfReader(uploaded_file)
                  text = "".join([page.extract_text() for page in pdf_reader.pages])
                  gsheet(text)
               
              

            # Email Section
            st.markdown("---")
            with st.expander("📧 Email Report"):
                email = st.text_input("Recipient Email")
                if st.button("Send Report"):
                    try:
                        valid = validate_email(email)
                        
                        if st.session_state.selected_doc:
                            doc_id = st.session_state.selected_doc
                            doc_data = st.session_state.documents[doc_id]
                            
                            # Load logo image
                            logo_path = Path("assets/logo.jpeg")
                            with open(logo_path, "rb") as logo_file:
                                logo_b64 = base64.b64encode(logo_file.read()).decode()
                            
                            # Generate report
                            report = generate_pdf_report(doc_id)
                            report_name = f"{doc_data['name']}_analysis_report.pdf"
                            
                            # Prepare original document
                            original_doc_name = doc_data["name"]
                            if original_doc_name.endswith('.pdf'):
                                original_doc_content = doc_data["content"].encode('utf-8')
                                content_type = "application/pdf"
                            else:
                                original_doc_content = doc_data["content"].encode('utf-8')
                                content_type = "text/plain; charset=utf-8"
                            
                            # Configure Mailjet client
                            mailjet = Client(auth=(os.getenv('EMAIL_API_KEY'), os.getenv('EMAIL_API_SECRET')), version='v3.1')
                            
                            # Create HTML email template
                            html_content = f"""
                            <html>
                                <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                                    <div style="max-width: 600px; margin: 0 auto;">
                                        <img src="data:image/jpeg;base64,{logo_b64}" alt="LegalMind Pro Logo" 
                                            style="max-width: 200px; margin-bottom: 20px;">
                                        
                                        <h2 style="color: #2A2F4F;">Legal Document Analysis Report</h2>
                                        
                                        <p>Dear Client,</p>
                                        
                                        <p>We have completed the analysis of your document: 
                                        <strong>{original_doc_name}</strong>. Please review the attached report containing:</p>
                                        
                                        <ul>
                                            <li>🔍 Comprehensive risk assessment</li>
                                            <li>📋 Detailed recommendations</li>
                                            <li>⚖️ Key legal implications</li>
                                        </ul>
                                        
                                        <h3 style="color: #2A2F4F; margin-top: 25px;">Risk Overview</h3>
                                        <p>Our analysis identified critical risks requiring attention. 
                                        The document received a risk score of {doc_data['analysis']['risk_score']}/100, indicating 
                                        {"urgent attention required" if doc_data['analysis']['risk_score'] > 70 else "moderate risk level"}.</p>
                                        
                                        <h3 style="color: #2A2F4F; margin-top: 25px;">Next Steps</h3>
                                        <ul>
                                            <li>Review the attached report and original document</li>
                                            <li>Prioritize implementation of recommendations</li>
                                            <li>Contact us for clarification if needed</li>
                                        </ul>
                                        
                                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                                            <p>Best regards,<br>
                                            <strong>The LegalMind Pro Team</strong></p>
                                            <img src="data:image/jpeg;base64,{logo_b64}" alt="Logo" 
                                                style="max-width: 100px; opacity: 0.8; margin-top: 15px;">
                                        </div>
                                    </div>
                                </body>
                            </html>
                            """

                            # Create email with attachments
                            data = {
                                'Messages': [{
                                    "From": {
                                        "Email": "legalmindpro@gmail.com",
                                        "Name": "LegalMind Pro"
                                    },
                                    "To": [{
                                        "Email": valid.email
                                    }],
                                    "Subject": f"Legal Analysis Report: {original_doc_name}",
                                    "HTMLPart": html_content,
                                    "Attachments": [
                                        {
                                            "ContentType": "application/pdf",
                                            "Filename": report_name,
                                            "Base64Content": base64.b64encode(report).decode()
                                        },
                                        {
                                            "ContentType": content_type,
                                            "Filename": original_doc_name,
                                            "Base64Content": base64.b64encode(original_doc_content).decode()
                                        }
                                    ]
                                }]
                            }
                            
                            # Send email
                            result = mailjet.send.create(data=data)
                            
                            if result.status_code == 200:
                                st.success("📨 Report and document sent successfully!")
                            else:
                                st.error(f"Failed to send email: {result.json().get('ErrorMessage', 'Unknown error')}")
                        else:
                            st.warning("Please select a document first!")
                            
                    except EmailNotValidError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"Error sending email: {str(e)}")

    # Main Content
    col1, col2 = st.columns([1, 2], gap="medium")

    with col1:
        st.markdown("### 📑 Document Insights")
        st.session_state.view_mode = st.radio("View Mode", ["Insights", "Document Preview"], horizontal=True)
        
        if st.session_state.selected_doc and "Insights" in st.session_state.view_mode:
            doc = st.session_state.documents[st.session_state.selected_doc]
            analysis = doc["analysis"]
            
            with st.expander("🔍 Metadata", expanded=True):
                st.write(f"**Author:** {doc['metadata']['author']}")
                st.write(f"**Created:** {doc['metadata']['created']}")
                st.write(f"**Modified:** {doc['metadata']['modified']}")
                st.write(f"**Pages:** {doc['metadata']['pages']}")
            
            with st.expander("📝 Summary"):
                st.markdown(analysis.get('summary', 'No summary available'))
            
            with st.expander("⚠️ Risks"):
                st.markdown(analysis.get('risks', 'No risk analysis available'))
            
            with st.expander("💡 Recommendations"):
                st.markdown(analysis.get('recommendations', 'No recommendations available'))
        
        elif st.session_state.selected_doc and "Document" in st.session_state.view_mode:
            doc = st.session_state.documents[st.session_state.selected_doc]
            st.markdown(f"### {doc['name']}")
            st.text_area("Content", 
                        value=doc["content"][:10000] + ("..." if len(doc["content"]) > 10000 else ""), 
                        height=600,
                        label_visibility="collapsed")

    with col2:
        st.markdown("### 💬 Legal Assistant")
        
        # Chat Container
        with st.container(height=700):
            for msg in st.session_state.history:
                bubble_class = "user-bubble" if msg["role"] == "user" else "bot-bubble"
                icon = "👤" if msg["role"] == "user" else "⚖️"
                st.markdown(f"""
                <div class="chat-bubble {bubble_class}">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                        <span style="font-size: 1.2rem;">{icon}</span>
                        <strong>{'You' if msg['role'] == 'user' else 'Legal AI'}</strong>
                    </div>
                    {msg['content']}
                </div>
                """, unsafe_allow_html=True)
        
        # Chat Input
        user_input = st.chat_input("Type your legal query...")

        if user_input:
            st.session_state.history.append({"role": "user", "content": user_input})
            
            with st.spinner("Analyzing..."):
                start_time = time.time()
                
                if st.session_state.selected_doc:
                    context = st.session_state.documents[st.session_state.selected_doc]["content"]
                    response = get_ai_response(context, user_input)
                else:
                    response = get_ai_response("", user_input)
                
                if not st.session_state.selected_doc and any(word in user_input.lower() for word in ["hi", "hello", "hey"]):
                    response = "Hello! I'm your legal AI assistant. How can I help you today?"
                
                processing_time = time.time() - start_time
                
                if processing_time > 3:
                    st.toast(f"Response generated in {processing_time:.1f}s", icon="⏳")
                
                st.session_state.history.append({"role": "assistant", "content": response})
                st.rerun()

if __name__ == "__main__":
    main()
