"""StakeGuard Streamlit entry point."""

import streamlit as st

from stakeguard import __version__

st.set_page_config(
    page_title="StakeGuard",
    page_icon=":material/shield:",
    layout="wide",
)

st.title("StakeGuard")
st.caption("Your personal betting risk advisor.")

st.info("The core flow is under construction. Check back soon.")

with st.sidebar:
    st.subheader("StakeGuard")
    st.caption(f"Version {__version__}")
    st.markdown("---")
    st.caption("Think first. Bet smarter.")
