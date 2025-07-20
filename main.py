# Granite ComplianceCop - Streamlit + Audio Upload + IBM Granite Simulation

import streamlit as st
import tempfile
import os
import speech_recognition as sr
from fpdf import FPDF
from pydub import AudioSegment


def simulate_granite_analysis(transcript):
    violation_patterns = [
        {"keyword": "confidential", "category": "Confidentiality Breach", "risk_level": "High", "suggestion": "Remind employees of NDA terms."},
        {"keyword": "delay reporting", "category": "Financial Compliance", "risk_level": "High", "suggestion": "Ensure finance reporting follows standards."},
        {"keyword": "delete records", "category": "Data Tampering", "risk_level": "High", "suggestion": "Ensure records are handled under audit procedures."},
        {"keyword": "bypass ethics", "category": "Ethical Violation", "risk_level": "High", "suggestion": "Follow protocol and ethical review."},
        {"keyword": "do not disclose", "category": "HR Compliance", "risk_level": "High", "suggestion": "Disclosures must follow grievance redressal."},
        {"keyword": "personal whatsapp", "category": "Data Security", "risk_level": "Medium", "suggestion": "Discourage use of unauthorized channels."},
        {"keyword": "don’t log", "category": "Wage Misreporting", "risk_level": "Medium", "suggestion": "All work hours must be reported."},
        {"keyword": "credentials on slack", "category": "Access Control Violation", "risk_level": "High", "suggestion": "Avoid credential sharing on public platforms."},
        {"keyword": "foreign payment", "category": "Audit Risk", "risk_level": "High", "suggestion": "Report foreign payments transparently."},
        {"keyword": "gmail", "category": "Privacy Risk", "risk_level": "Medium", "suggestion": "Send sensitive info only via secured channels."},
        {"keyword": "inflate results", "category": "Integrity Risk", "risk_level": "High", "suggestion": "Report truthful and accurate data."},
        {"keyword": "verbal only", "category": "Lack of Audit Trail", "risk_level": "Low", "suggestion": "Maintain written documentation where possible."},
    ]

    for i in range(1, 101):
        violation_patterns.append({
            "keyword": f"violation{i}",
            "category": f"AutoGen Category {i}",
            "risk_level": "Medium" if i % 2 == 0 else "Low",
            "suggestion": f"Auto-generated suggestion for violation {i}."
        })

    violations = []
    for line in transcript.splitlines():
        speaker = "Unknown"
        statement = line
        if ":" in line:
            parts = line.split(":", 1)
            if len(parts) == 2:
                speaker = parts[0].strip()
                statement = parts[1].strip().lower()

        for pattern in violation_patterns:
            if pattern["keyword"] in statement:
                report_to = "HR Department" if pattern["risk_level"] == "High" else "Compliance Officer"
                violations.append({
                    "speaker": speaker,
                    "line": line,
                    "category": pattern["category"],
                    "risk_level": pattern["risk_level"],
                    "suggestion": pattern["suggestion"],
                    "report_to": report_to
                })
    return violations


def clean_text(text):
    return (
        text.replace('\u2019', "'")
            .replace('\u2018', "'")
            .replace('\u201c', '"')
            .replace('\u201d', '"')
            .replace('\u2014', '-')
            .replace('\u2013', '-')
    )

def generate_pdf(transcript, violations):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Compliance Report", ln=True, align='C')
    pdf.ln(10)
    pdf.multi_cell(0, 10, clean_text(f"Transcript:\n{transcript}"))
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Detected Violations:", ln=True)
    pdf.set_font("Arial", size=12)
    for v in violations:
        pdf.multi_cell(0, 10, clean_text(
            f"- Speaker: {v['speaker']}\n  Line: {v['line']}\n  Category: {v['category']}\n  Risk Level: {v['risk_level']}\n  Suggestion: {v['suggestion']}\n  Report To: {v['report_to']}\n"
        ))
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name
def transcribe_audio(audio_file_path):
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_file(audio_file_path)
    wav_path = audio_file_path.replace(".mp3", ".wav")
    audio.export(wav_path, format="wav")
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return "Could not understand the audio."
        except sr.RequestError as e:
            return f"Could not request results; {e}"

st.title("Granite ComplianceCop - AI Compliance Assistant")
st.write("Upload a meeting transcript or audio and detect potential compliance violations.")

option = st.radio("Choose input method:", ("Text Transcript", "Audio Upload (.mp3)"))
transcript_input = ""

if option == "Text Transcript":
    transcript_input = st.text_area("Paste Transcript or Meeting Notes:")
else:
    uploaded_audio = st.file_uploader("Upload MP3 Audio File", type="mp3")
    if uploaded_audio is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
            tmp_audio.write(uploaded_audio.read())
            audio_path = tmp_audio.name
        st.info("Transcribing audio...")
        transcript_input = transcribe_audio(audio_path)
        st.text_area("Transcript from Audio:", transcript_input, height=200)

if st.button("Analyze for Violations"):
    if transcript_input.strip() == "":
        st.error("Please provide transcript text or upload audio.")
    else:
        with st.spinner("Analyzing using Granite AI..."):
            violations = simulate_granite_analysis(transcript_input)
        st.success(f"Analysis complete. {len(violations)} violation(s) found.")

        for i, v in enumerate(violations):
            st.markdown(f"### Violation {i+1}")
            st.markdown(f"**Speaker:** {v['speaker']}")
            st.markdown(f"**Line:** {v['line']}")
            st.markdown(f"**Category:** {v['category']}")
            st.markdown(f"**Risk Level:** {v['risk_level']}")
            st.markdown(f"**Suggestion:** {v['suggestion']}")
            st.markdown(f"**Report To:** {v['report_to']}")

        pdf_path = generate_pdf(transcript_input, violations)
        with open(pdf_path, "rb") as f:
            st.download_button("Download Compliance Report (PDF)", f, file_name="compliance_report.pdf")

        os.remove(pdf_path)
