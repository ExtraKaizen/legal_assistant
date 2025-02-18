# LegalMind Pro - AI-Powered Legal Document Analysis Suite

## Overview

**LegalMind Pro** is an **Advanced AI-Driven App** designed to assist legal professionals, businesses, and individuals in analyzing legal documents. The application leverages state-of-the-art AI models to provide comprehensive insights, risk assessments, and recommendations based on the content of uploaded legal documents. With features like document analysis, risk scoring, executive summaries, and a built-in legal assistant, LegalMind Pro streamlines the process of legal document review and decision-making.

## Features

- **Document Analysis**: Upload PDF or text documents for detailed analysis.
- **Risk Assessment**: Identify and evaluate potential risks within legal documents.
- **Executive Summaries**: Generate concise, actionable summaries of document content.
- **Recommendations**: Receive tailored recommendations for addressing identified risks.
- **Legal Assistant**: Interact with an AI-powered legal assistant for real-time queries and support.
- **Report Generation**: Download comprehensive PDF reports summarizing document analysis.
- **Email Integration**: Send analysis reports and original documents via email directly from the app.
- **Customizable UI**: A sleek, professional interface with dark mode and custom styling.

## Installation

To run LegalMind Pro locally, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repository/legalmind-pro.git
   cd legalmind-pro
   ```

2. **Set Up Environment Variables**:
   - Create a `.env` file in the root directory.
   - Add the following environment variables:
     ```plaintext
     groq_api_key=your_groq_api_key
     EMAIL_API_KEY=your_mailjet_api_key
     EMAIL_API_SECRET=your_mailjet_api_secret
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

5. **Access the Application**:
   - Open your web browser and navigate to `http://localhost:8501`.

## Usage

### Uploading Documents

1. **Upload Documents**:
   - Use the sidebar to upload PDF or text documents.
   - Multiple documents can be uploaded simultaneously.

2. **Document Selection**:
   - Select a document from the sidebar to view its analysis.

### Viewing Insights

1. **Metadata**:
   - View document metadata such as author, creation date, and page count.

2. **Executive Summary**:
   - Access a concise summary of the document's content.

3. **Risk Assessment**:
   - Review identified risks with severity scores and explanations.

4. **Recommendations**:
   - Get detailed recommendations for addressing identified risks.

### Interacting with the Legal Assistant

1. **Chat Interface**:
   - Use the chat interface to ask legal questions or seek clarification on document content.

2. **Contextual Responses**:
   - The assistant provides responses based on the content of the selected document.

### Generating Reports

1. **Generate PDF Report**:
   - Click the "Generate Report" button in the sidebar to create a PDF report.

2. **Download Report**:
   - Download the generated report for offline use.

3. **Email Report**:
   - Enter the recipient's email address and send the report directly from the app.

## Technologies Used

- **Streamlit**: For building the web application interface.
- **Groq API**: For leveraging AI models to analyze documents and provide responses.
- **PyPDF2**: For extracting text from PDF documents.
- **NLTK**: For natural language processing tasks.
- **FPDF**: For generating PDF reports.
- **Mailjet**: For sending emails with attached reports.
- **Faker**: For generating fake data (used in development).

## Customization

### UI Customization

The application's UI can be customized by modifying the CSS styles in the `inject_custom_css` function. The current theme features a dark background with golden accents, but you can adjust colors, fonts, and other styles to match your preferences.

### AI Model Configuration

The AI model used for document analysis and chat responses can be configured in the `get_ai_response` function. Currently, the application uses the `mixtral-8x7b-32768` model, but you can switch to other models supported by the Groq API.

## Contributing

We welcome contributions to LegalMind Pro! If you'd like to contribute, please follow these steps:

1. **Fork the Repository**.
2. **Create a New Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make Your Changes**.
4. **Commit Your Changes**:
   ```bash
   git commit -m "Add your commit message here"
   ```
5. **Push to the Branch**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Open a Pull Request**.

## License

LegalMind Pro is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Support

For any issues or questions, please open an issue on the GitHub repository or contact the maintainers directly.

---

**LegalMind Pro** is designed to make legal document analysis more efficient and accessible. Whether you're a legal professional or someone dealing with legal documents, this tool aims to provide valuable insights and recommendations to help you make informed decisions.
