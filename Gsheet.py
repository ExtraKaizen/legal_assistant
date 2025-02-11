from langchain.text_splitter import CharacterTextSplitter
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from langchain_groq import ChatGroq


API_KEY= "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"
MODEL_NAME = "llama-3.2-11b-vision-preview"
llm = ChatGroq(groq_api_key=API_KEY, model_name=MODEL_NAME)


def detect_risks_and_recommendations(text_chunks):
        results = []
        for chunk in text_chunks:
            prompt = (
                f"Analyze the following text and provide a structured response:\n\n"
                f"Text: {chunk}\n\n"
                f"Provide the following details:\n"
                f"- Risks: Summarize potential risks, issues, or hidden dependencies clearly.\n"
                f"- Recommendations: Suggest practical, clear, and actionable recommendations to mitigate the risks.\n\n"
                f"Output format:\n"
                f"Risks: <List the risks in simple points>\n"
                f"Recommendations: <List the recommendations in simple points>"
            )
            response = llm.invoke(prompt)
            response_text = response.content.strip()
            risks, recommendations = "No risks identified.", "No recommendations provided."

            if "Risks:" in response_text and "Recommendations:" in response_text:
                try:
                    risks_start = response_text.index("Risks:") + len("Risks:")
                    recommendations_start = response_text.index("Recommendations:")
                    risks = response_text[risks_start:recommendations_start].strip()
                    recommendations = response_text[recommendations_start + len("Recommendations:"):].strip()
                except ValueError:
                    pass

            results.append({
                "context": chunk,
                "risks": risks,
                "recommendations": recommendations
            })
        return results

   
def gsheet(file):
    SERVICE_ACCOUNT_FILE = "infosys-449015-83ef8f804adb.json"
    SPREADSHEET_ID = "1rvEwtYh7mpqcBZgv7D14giGZ_mhBM-aiNZ_dxjJJQf0"  # Replace with your Google Sheet ID

    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=20)
    texts = text_splitter.split_text(file)
    results = detect_risks_and_recommendations(texts)
    df = pd.DataFrame(results)
    credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()

    values = [["Context", "Risks", "Recommendations"]]
    for result in results:
            values.append([result["context"], result["risks"], result["recommendations"]])

    body = {"values": values}
    sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range="Sheet1!A1",
            valueInputOption="RAW",
            body=body,
        ).execute()
# st.success("Data saved to Google Sheets.")
