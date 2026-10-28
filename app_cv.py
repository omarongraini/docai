import streamlit as st

from chatpdf.features.cv.service import evaluate_cv
from chatpdf.rag.ingest import _extract_clean_pages

st.set_page_config(page_title="CV Evaluator", page_icon="📄", layout="wide")

st.title("📄 CV / Job Description Evaluator")
st.markdown("Upload a CV, paste the job description, and let the AI find the gaps.")

# Sidebar for inputs
with st.sidebar:
    st.header("Inputs")
    cv_file = st.file_uploader("Upload CV (PDF)", type=["pdf"])
    lang_choice = st.selectbox("Output Language", ["en", "ar"])

    st.divider()
    st.subheader("Job Description")
    jd_text = st.text_area("Paste the JD here", height=300)

# Main area for actions and results
if st.button("Evaluate Match", type="primary", use_container_width=True):
    if not cv_file:
        st.error("⚠️ Please upload a CV first.")
    elif not jd_text.strip():
        st.error("⚠️ Please paste a Job Description.")
    else:
        with st.spinner("Extracting text and evaluating with AI..."):
            try:
                # 1. Extract text from PDF using our existing PyMuPDF logic
                pages = _extract_clean_pages(cv_file.getvalue())
                cv_text = "\n".join(pages)

                # 2. Call the service
                result = evaluate_cv(cv_text, jd_text, language=lang_choice)

                # 3. Render Results
                st.divider()

                # Score & Summary
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.metric(label="Match Score", value=f"{result.score} / 100")
                with col2:
                    st.info(result.summary)

                # Skills Breakdown
                col_left, col_right = st.columns(2)

                with col_left:
                    st.subheader("✅ Matched Skills")
                    if not result.matched_skills:
                        st.write("No matching skills found.")
                    for m in result.matched_skills:
                        if m.found_in_cv:
                            st.success(f'**{m.skill}**\n\n*"{m.evidence}"*')

                with col_right:
                    st.subheader("❌ Missing Skills")
                    if not result.missing_skills:
                        st.write("No missing skills found. Perfect match!")
                    for skill in result.missing_skills:
                        st.error(skill)

                # Experience Gap
                st.subheader("📉 Experience Gap")
                st.warning(result.experience_gap)

            except Exception as e:  # noqa: BLE001 (UI boundary: catch all to prevent app crash) # noqa: BLE001 (UI boundary: catch all to prevent app crash)
                st.error(f"Evaluation failed: {e}")
