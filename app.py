import streamlit as st
from dotenv import load_dotenv
import os
from pathlib import Path
from google import genai
from prompt_engine import engineer_prompt, get_available_styles, detect_prompt_issues, get_corrected_prompt_suggestion

load_dotenv(dotenv_path=Path(__file__).parent / ".env")
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="AI Prompt Engine", page_icon="✨")
st.title("✨ AI Prompt Engineering App")

if not api_key:
    st.error("GEMINI_API_KEY missing. Create project/.env file")
    st.stop()

client = genai.Client(api_key=api_key)

style = st.selectbox("Choose Prompt Style:", get_available_styles())
user_input = st.text_area("Your Idea / Question:", height=120, placeholder="e.g. writ a story abuot robo")

# --- NEW FEATURE: Check for errors ---
corrected_prompt = ""
if user_input.strip():
    issues = detect_prompt_issues(user_input)
    suggestion = get_corrected_prompt_suggestion(user_input)

    if issues and suggestion.lower()!= user_input.lower().strip():
        st.warning(f"⚠️ I found issues: {', '.join(issues)}")
        st.info(f"💡 Did you mean: **{suggestion}**?")
        if st.button(f"✅ Use corrected: '{suggestion}'"):
            user_input = suggestion
            corrected_prompt = suggestion
            st.success("Using corrected prompt!")

    # AI-powered better correction
    if st.checkbox("Use AI to auto-correct my prompt"):
        if st.button("AI Correct my prompt"):
            with st.spinner("AI is correcting..."):
                try:
                    res = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=f"Correct the grammar, spelling and make this prompt clear and professional. Only return the corrected prompt, nothing else: '{user_input}'"
                    )
                    st.code(res.text, language="text")
                    if st.button(f"Use this AI correction"):
                        st.session_state['ai_corrected'] = res.text
                except Exception as e:
                    st.error(str(e))

final_input = st.session_state.get('ai_corrected', corrected_prompt or user_input)

if st.button("Generate 🚀"):
    if not final_input.strip():
        st.warning("Type something first!")
    else:
        final_prompt = engineer_prompt(final_input, style)
        with st.spinner(f"Generating with {style} style..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=final_prompt
                )
                st.success("Result:")
                st.write(response.text)
                with st.expander("See Engineered Prompt"):
                    st.code(final_prompt)
            except Exception as e:
                st.error(f"Error: {e}")

if st.session_state.get('ai_corrected'):
    if st.button("Clear AI correction"):
        del st.session_state['ai_corrected']
        st.rerun()
