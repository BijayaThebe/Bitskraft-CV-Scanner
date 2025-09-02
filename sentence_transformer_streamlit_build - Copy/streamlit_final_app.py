import streamlit as st
import pandas as pd
import os
import pythoncom
from pathlib import Path
from outlook_work import config

# Import modules
try:
    from outlook_work.downloader import OutlookCVFetcher, send_bulk_emails, DEFAULT_EMAIL_TEMPLATE
    from outlook_work.resume_Parse import ResumeParser
    from outlook_work.config import get_save_directory
except ImportError as e:
    st.error(f"❌ Failed to import Outlook modules: {e}")
    st.stop()

try:
    from model_handling import UniversalResumeAnalyzer
except ImportError as e:
    st.error(f"❌ Failed to import AI model: {e}")
    st.stop()

# -------------------------------
# App Configuration
# -------------------------------
st.set_page_config(
    page_title="💼 Bitskraft CV Scanner & AI Evaluator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# Sidebar Navigation
# -------------------------------
st.sidebar.title("🧭 Navigation")
app_mode = st.sidebar.radio(
    "Choose Mode",
    ["📧 Outlook CV Fetcher", "🧠 AI Resume Evaluator", "🏆 Final Ranked Results"],
    help="Switch between app sections"
)

# -------------------------------
# Session State Initialization
# -------------------------------
if 'results_df' not in st.session_state:
    st.session_state['results_df'] = pd.DataFrame()
if 'parsed_df' not in st.session_state:
    st.session_state['parsed_df'] = pd.DataFrame()
if 'analysis_done' not in st.session_state:
    st.session_state['analysis_done'] = False
if 'parse_done' not in st.session_state:
    st.session_state['parse_done'] = False
if 'email_account' not in st.session_state:
    st.session_state['email_account'] = 'your-email@bitskraft.com'

# -------------------------------
# Helper: Save/Load Path
# -------------------------------
def get_save_path():
    try:
        with open("cv_save_path.txt", "r", encoding="utf-8") as f:
            path = f.read().strip()
        save_path = Path(path)
        return save_path if save_path.exists() else None
    except Exception:
        return None

def save_path_to_config(path):
    try:
        save_path = Path(path).resolve()
        save_path.mkdir(parents=True, exist_ok=True)
        with open("cv_save_path.txt", "w", encoding="utf-8") as f:
            f.write(str(save_path))
        return True
    except Exception as e:
        st.error(f"❌ Failed to save path: {e}")
        return False

# -------------------------------
# MODE 1: Outlook CV Fetcher
# -------------------------------
if app_mode == "📧 Outlook CV Fetcher":
    st.title("📧 Outlook CV Fetcher & Parser")

    st.markdown("""
    **Automatically download CVs from Outlook and parse them into structured data.**
    """)

    # Folder Selection
    st.header("📁 Select Save Location")
    current_path = get_save_path()

    if current_path:
        st.success(f"✅ Current Save Folder:\n\n`{current_path}`")
    else:
        st.info("No folder selected yet. Please set one below.")

    folder_input = st.text_input(
        "📁 Enter folder path to save CVs:",
        value=str(current_path) if current_path else "",
        placeholder="e.g., C:\\Users\\YourName\\Documents\\Resumes"
    )

    if st.button("✅ Set Folder"):
        if folder_input.strip():
            try:
                save_path = Path(folder_input.strip()).resolve()
                save_path.mkdir(parents=True, exist_ok=True)
                if save_path_to_config(save_path):
                    st.success(f"📁 Save path updated to:\n\n`{save_path}`")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Cannot use this path: {e}")
        else:
            st.warning("Please enter a valid path.")

    # Determine save directory
    SAVE_DIR = get_save_path() or Path(__file__).parent / "uploads" / "resumes"
    SAVE_DIR = Path(SAVE_DIR).resolve()
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_CSV = SAVE_DIR / "candidates.csv"

    # Outlook Integration
    st.header("📥 Outlook Integration")
    email_account = st.text_input("📧 Enter Your Outlook Email", value=st.session_state['email_account'])

    # Store email in session state when changed
    if email_account and email_account != st.session_state['email_account']:
        st.session_state['email_account'] = email_account
        st.success("✅ Email address saved!")

    if st.checkbox("✅ Enable Outlook Integration", key="enable_outlook"):
        if st.button("📥 Fetch CVs from Outlook"):
            with st.spinner("🔗 Connecting to Outlook..."):
                try:
                    pythoncom.CoInitialize()
                    fetcher = OutlookCVFetcher(email_account=email_account, save_dir=str(SAVE_DIR))
                    downloaded_count = fetcher.process_jobbox()
                    if downloaded_count and downloaded_count > 0:
                        st.success(f"✅ {downloaded_count} CVs downloaded successfully!")
                    else:
                        st.info("📭 No new CVs found in JobBox.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Outlook error: {e}")
                finally:
                    pythoncom.CoUninitialize()

    # Parse Resumes
    if st.button("🔄 Parse All Resumes", key="parse"):
        with st.spinner("🔍 Parsing PDFs..."):
            try:
                parser = ResumeParser(save_dir=str(SAVE_DIR), output_file=str(OUTPUT_CSV))
                parser.parse_pdfs()
                parser.save_to_excel()
                if OUTPUT_CSV.exists():
                    df = pd.read_csv(OUTPUT_CSV)
                    if df is not None and not df.empty:
                        st.session_state['parsed_df'] = df
                        st.session_state['parse_done'] = True
                        st.success(f"✅ Parsing complete! Found {len(df)} candidates.")
                    else:
                        st.warning("⚠️ CSV file is empty or contains no valid data.")
                else:
                    st.warning("⚠️ No CSV file created. Check if any PDFs were parsed.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Parsing failed: {e}")

    # View Parsed Data
    st.markdown("---")
    if st.button("🔍 View Parsed Data"):
        if st.session_state['parse_done'] and not st.session_state['parsed_df'].empty:
            st.subheader("📋 Parsed Candidate Data")
            st.dataframe(st.session_state['parsed_df'], use_container_width=True)
            st.success(f"✅ Found {len(st.session_state['parsed_df'])} candidate(s)")
        else:
            st.warning("⚠️ No parsed data found. Run the parser first.")

# -------------------------------
# MODE 2: AI Resume Evaluator
# -------------------------------
elif app_mode == "🧠 AI Resume Evaluator":
    st.title("🧠 Bitskraft AI Resume Evaluator")

    st.markdown("""
    **Upload resumes and evaluate them against a job description using AI.**
    """)

    # Cache model
    @st.cache_resource
    def get_analyzer():
        st.info("📥 Loading AI model... (first run may take ~30 sec)")
        return UniversalResumeAnalyzer()

    analyzer = get_analyzer()

    # Job Description
    st.markdown("### 📝 Job Requirements")
    job_description = st.text_area(
        "Describe the ideal candidate:",
        height=200,
        placeholder="E.g., 3+ years in Python, experience with NLP, TensorFlow, AWS..."
    )

    if not job_description.strip():
        st.info("💡 Please enter job requirements to begin.")
    else:
        st.markdown("### 📎 Upload Resumes (PDF/DOCX)")
        uploaded_files = st.file_uploader(
            "Upload up to 1,000 resumes",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            help="Max 1,000 files supported"
        )

        if not uploaded_files:
            st.warning("📤 Please upload at least one resume.")
        else:
            total_files = len(uploaded_files)
            total_size = sum(f.size for f in uploaded_files)

            if total_files > 1000:
                st.error("❌ Maximum 1,000 resumes allowed.")
            elif total_size > 100 * 1024 * 1024:  # 100 MB
                st.error("❌ Total file size exceeds 100 MB limit.")
            else:
                if st.button("🚀 Start AI Evaluation", type="primary"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    results = []
                    for i, file in enumerate(uploaded_files):
                        filename = file.name
                        status_text.text(f"Processing {i+1}/{total_files}: {filename}")

                        try:
                            file.seek(0)
                            content = file.read()

                            # Determine format
                            if filename.lower().endswith(".pdf"):
                                file_format = "pdf"
                            elif filename.lower().endswith(".docx"):
                                file_format = "docx"
                            else:
                                result = {
                                    "Resume Name": filename,
                                    "Error": "Unsupported file type",
                                    "Overall Match Score": 0.0,
                                    "Keywords Matched": "",
                                    "Semantic Relevance": 0.0,
                                    "Summary": "Unsupported format"
                                }
                                results.append(result)
                                continue

                            # Extract text
                            text = analyzer.extract_text(content, file_format)
                            if not text or not text.strip():
                                result = {
                                    "Resume Name": filename,
                                    "Error": "No text extracted",
                                    "Overall Match Score": 0.0,
                                    "Keywords Matched": "",
                                    "Semantic Relevance": 0.0,
                                    "Summary": "Empty or unreadable content"
                                }
                                results.append(result)
                                st.warning(f"⚠️ No text extracted from {filename}")
                                continue

                            # Analyze resume
                            analysis = analyzer.analyze_resume(text, job_description)
                            
                            # Safe extraction with None checks
                            overall_score = analysis.get("overall_match_score", 0.0)
                            keywords = analysis.get("keywords_matched", [])
                            semantic_score = analysis.get("semantic_relevance", 0.0)
                            summary = analysis.get("summary", "No summary available")
                            
                            # Convert None values to safe defaults
                            result = {
                                "Resume Name": filename,
                                "Overall Match Score": float(overall_score) if overall_score is not None else 0.0,
                                "Keywords Matched": ", ".join(keywords) if keywords else "",
                                "Semantic Relevance": float(semantic_score) if semantic_score is not None else 0.0,
                                "Summary": summary if summary else "No summary available"
                            }
                            results.append(result)

                        except Exception as e:
                            st.error(f"❌ Failed to process {filename}: {e}")
                            result = {
                                "Resume Name": filename,
                                "Error": str(e),
                                "Overall Match Score": 0.0,
                                "Keywords Matched": "",
                                "Semantic Relevance": 0.0,
                                "Summary": "Processing failed"
                            }
                            results.append(result)

                        progress_bar.progress((i + 1) / total_files)

                    # Convert to DataFrame
                    df = pd.DataFrame(results)

                    # Safe filtering - handle NaN and None values
                    if 'Error' in df.columns:
                        df = df[~df['Error'].notna()]
                        df = df.drop(columns=['Error'], errors='ignore')

                    if df.empty:
                        st.warning("⚠️ No valid resumes were processed.")
                    else:
                        # Safe sorting with fillna to handle None values
                        df['Overall Match Score'] = pd.to_numeric(df['Overall Match Score'], errors='coerce').fillna(0.0)
                        df = df.sort_values("Overall Match Score", ascending=False).reset_index(drop=True)
                        df["Rank"] = df.index.map(lambda x: f"{x+1}{'st' if x==0 else 'nd' if x==1 else 'rd' if x==2 else 'th'}")
                        st.session_state['results_df'] = df
                        st.session_state['analysis_done'] = True

                    status_text.text("✅ AI Analysis Complete!")
                    progress_bar.empty()

        # Display results
        if st.session_state.get('analysis_done', False):
            df = st.session_state['results_df']
            if not df.empty:
                st.markdown("### 📊 AI Evaluation Results")

                top_options = [5, 10, 20, 50, 100, "All"]
                choice = st.selectbox("🔽 Show top candidates:", top_options, index=1, key="top_n_ai")

                display_df = df if choice == "All" else df.head(choice)
                st.dataframe(display_df, use_container_width=True)

                # Safe access to scores with None checks
                best_score = 0.0
                if len(df) > 0 and "Overall Match Score" in df.columns:
                    score_val = df["Overall Match Score"].iloc[0]
                    best_score = float(score_val) if score_val is not None else 0.0
                    
                st.caption(f"✅ Total processed: {len(df)} | Best match: {best_score:.3f}")

                csv = df.to_csv(index=False)
                st.download_button(
                    "⬇️ Download Full Report (CSV)",
                    data=csv,
                    file_name="ai_evaluation.csv",
                    mime="text/csv"
                )

                with st.expander("🔍 View Raw JSON"):
                    st.json(df.to_dict("records"))

# -------------------------------
# MODE 3: Final Ranked Results
# -------------------------------
elif app_mode == "🏆 Final Ranked Results":
    st.title("🏆 Final Ranked Candidate List")

    st.markdown("""
    **Unified view of all candidates with AI score, contact info, and ranking.**
    """)

    # Get email account from session state
    email_account = st.session_state.get('email_account', 'your-email@bitskraft.com')
    
    parsed_df = st.session_state['parsed_df']
    ai_df = st.session_state['results_df']

    if (st.session_state.get('parse_done', False) and 
        st.session_state.get('analysis_done', False) and 
        not parsed_df.empty and not ai_df.empty):
        
        # Rename and ensure columns exist
        if 'FileName' in parsed_df.columns:
            parsed_df_renamed = parsed_df.rename(columns={"FileName": "Resume Name"})
        else:
            st.error("❌ Parsed data missing 'FileName' column.")
            st.stop()

        required_cols = ["Name", "Phone", "Email", "LinkedIn", "GitHub"]
        for col in required_cols:
            if col not in parsed_df_renamed.columns:
                parsed_df_renamed[col] = "Not available"

        # Merge
        merged_df = pd.merge(ai_df, parsed_df_renamed, on="Resume Name", how="left")

        # Select and rename early
        columns_to_keep = [
            "Rank", "Name", "Phone", "Email", "LinkedIn", "GitHub",
            "Overall Match Score", "Keywords Matched", "Semantic Relevance", "Resume Name"
        ]
        final_df = merged_df[[col for col in columns_to_keep if col in merged_df.columns]].copy()

        # Ensure numeric score
        if 'Overall Match Score' in final_df.columns:
            final_df['Overall Match Score'] = pd.to_numeric(final_df['Overall Match Score'], errors='coerce').fillna(0.0)
            final_df = final_df.sort_values("Overall Match Score", ascending=False).reset_index(drop=True)
            final_df["Rank"] = [f"{i+1}{'st' if i==0 else 'nd' if i==1 else 'rd' if i==2 else 'th'}" for i in range(len(final_df))]

        st.session_state['final_ranked'] = final_df

        # Filter
        st.markdown("### 🔽 Select How Many Top Candidates to Show")
        top_options = [5, 10, 20, 50, 100, "All"]
        choice = st.selectbox("Show top:", top_options, index=0, key="top_n_final")

        display_df = final_df if choice == "All" else final_df.head(choice)

        # Stylish display
        st.markdown("### 🏆 Ranked Candidates")
        if not final_df.empty:
            # Safe formatting
            format_dict = {}
            if 'Overall Match Score' in final_df.columns:
                format_dict['Overall Match Score'] = "{:.3f}"
            if 'Semantic Relevance' in final_df.columns:
                format_dict['Semantic Relevance'] = "{:.3f}"
                
            styled_df = display_df.style.format(format_dict)
            st.dataframe(styled_df, use_container_width=True)

            # Safe access to top score
            top_score = "N/A"
            if len(final_df) > 0 and 'Overall Match Score' in final_df.columns:
                score_val = final_df['Overall Match Score'].iloc[0]
                if score_val is not None:
                    top_score = f"{float(score_val):.3f}"
                    
            st.markdown(f"**📊 Summary**: Showing {len(display_df)} of {len(final_df)} candidates. Top score: `{top_score}`")

            # Export
            csv = final_df.to_csv(index=False)
            st.download_button(
                "📦 Download Full Ranked List (CSV)",
                data=csv,
                file_name="final_ranked_candidates.csv",
                mime="text/csv"
            )

            with st.expander("🔍 View Full Details"):
                st.dataframe(final_df, use_container_width=True)
                
            # Add email sending functionality
            st.markdown("---")
            st.subheader("📧 Contact Top Candidates")
            
            # Email template customization
            st.markdown("### ✉️ Email Template")
            email_subject = st.text_input(
                "Email Subject",
                value=DEFAULT_EMAIL_TEMPLATE['subject'],
                help="Use {position} as a placeholder for the job position"
            )
            
            email_body = st.text_area(
                "Email Body",
                value=DEFAULT_EMAIL_TEMPLATE['body'],
                height=300,
                help="Use {candidate_name}, {position}, and {company_name} as placeholders"
            )
            
            email_template = {
                'subject': email_subject,
                'body': email_body
            }
            
            # Select number of top candidates to contact
            max_candidates = min(10, len(final_df))
            if max_candidates > 0:
                num_candidates = st.slider(
                    "Number of top candidates to contact",
                    min_value=1,
                    max_value=max_candidates,
                    value=min(5, max_candidates)
                )
                
                # Get top candidates
                top_candidates = final_df.head(num_candidates).copy()
                
                # Sort by score descending
                top_candidates_sorted = top_candidates.sort_values(by='Overall Match Score', ascending=False).reset_index(drop=True)

                # Make Name and Email editable
                display_cols = ['Name', 'Email']
                if 'Overall Match Score' in top_candidates_sorted.columns:
                    display_cols.append('Overall Match Score')

                edited_candidates = st.data_editor(
                    top_candidates_sorted[display_cols],
                    column_config={
                        "Name": st.column_config.TextColumn(
                            "Name",
                            help="Edit candidate's name",
                            default="",
                            max_chars=100,
                            required=True,
                        ),
                        "Email": st.column_config.TextColumn(
                            "Email",
                            help="Edit candidate's email address",
                            default="",
                            max_chars=100,
                            validate=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                            required=True,
                        ),
                        "Overall Match Score": st.column_config.NumberColumn(
                            "Score",
                            help="Match score (read-only)",
                            format="%.3f",
                            disabled=True,
                        ),
                    },
                    disabled=("Overall Match Score",) if "Overall Match Score" in display_cols else False,
                    key="editable_candidate_table"
                )

                # Save edited data
                st.session_state['edited_candidates'] = edited_candidates

                # Show final list after edits
                st.markdown("### ✅ Final Contact List (After Edits)")
                for idx, row in edited_candidates.iterrows():
                    rank = idx + 1
                    name = row['Name'].strip()
                    email = row['Email'].strip()
                    score = f"{row['Overall Match Score']:.3f}" if not pd.isna(row['Overall Match Score']) else "N/A"
                    st.write(f"**Rank {rank}**: {name} — `{email}` (Score: {score})")

                # Send Emails Button
                if st.button("🚀 Send Emails to Selected Candidates", type="primary"):
                    if not email_account or email_account == 'your-email@bitskraft.com':
                        st.error("Please set your Outlook email address in the Outlook CV Fetcher section first.")
                    else:
                        with st.spinner(f"Sending emails to {len(edited_candidates)} candidates..."):
                            successful_emails = send_bulk_emails(
                                edited_candidates,  # ✅ Use edited DataFrame
                                email_template,
                                email_account
                            )
                            
                            if successful_emails:
                                st.success(f"✅ Successfully sent emails to {len(successful_emails)} candidates!")
                                for email in successful_emails:
                                    st.write(f"- {email}")
                            else:
                                st.error("❌ Failed to send any emails. Please check your Outlook configuration.")
            else:
                st.warning("⚠️ No candidates available for emailing.")
        else:
            st.warning("⚠️ No candidates to display. Check parsing and AI evaluation steps.")

    else:
        st.warning("⚠️ Please complete both **Outlook Parsing** and **AI Evaluation** to see final results.")
        st.info("""
        - Go to **📧 Outlook CV Fetcher** to parse resumes.
        - Go to **🧠 AI Resume Evaluator** to analyze them.
        - Then return here to see the unified ranked list.
        """)

# -------------------------------
# Footer
# -------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ Info")
st.sidebar.markdown("""
- **App**: Bitskraft CV Scanner v1.0
- **Model**: UniversalResumeAnalyzer
- **Support**: hr-tech@bitskraft.com
""")