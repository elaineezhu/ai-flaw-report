import streamlit as st
import os
from form.app import create_app

if "STORAGE_PROVIDER" not in os.environ:
    os.environ["STORAGE_PROVIDER"] = "huggingface"

if __name__ == "__main__":
    create_app()