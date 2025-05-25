import streamlit as st
import pandas as pd
import qrcode
from PIL import Image
from io import BytesIO
import json
import os
import datetime
import time
import string
import random
from nanoid import generate

# Configure the page
st.set_page_config(
    page_title="LinkSnip | URL Shortener",
    page_icon="✂️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS
def local_css():
    st.markdown("""
    <style>
        /* Main theme colors */
        :root {
            --primary-color: #0066FF;
            --secondary-color: #14B8A6;
            --accent-color: #FF5722;
            --text-color: #333333;
            --bg-color: #F8F9FA;
            --card-color: #FFFFFF;
        }
        
        /* Global styles */
        .stApp {
            background-color: var(--bg-color);
            color: var(--text-color);
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-color);
            font-weight: 600;
        }
        
        /* Header styling */
        .header {
            display: flex;
            align-items: center;
            margin-bottom: 2rem;
            animation: fadeIn 0.5s ease-in-out;
        }
        
        .header-logo {
            font-size: 2.5rem;
            margin-right: 0.5rem;
            color: var(--primary-color);
        }
        
        .header-title {
            font-size: 2rem;
            font-weight: 700;
            margin: 0;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Card styling */
        .card {
            background-color: var(--card-color);
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin-bottom: 1rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            border-left: 4px solid var(--primary-color);
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08);
        }
        
        /* Button styling */
        .stButton > button {
            background-color: var(--primary-color) !important;
            color: white !important;
            border: none !important;
            border-radius: 4px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton > button:hover {
            background-color: #0055CC !important;
            transform: translateY(-1px) !important;
        }
        
        /* Input styling */
        .stTextInput > div > div > input {
            border-radius: 4px !important;
            border: 1px solid #DDDDDD !important;
            padding: 0.75rem !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--primary-color) !important;
            box-shadow: 0 0 0 2px rgba(0, 102, 255, 0.2) !important;
        }
        
        /* Copy button */
        .copy-btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background-color: var(--secondary-color);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 0.25rem 0.75rem;
            font-size: 0.875rem;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }
        
        .copy-btn:hover {
            background-color: #0F9A8E;
        }
        
        /* URL card */
        .url-card {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            background-color: var(--card-color);
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            margin-bottom: 0.75rem;
        }
        
        .url-details {
            flex-grow: 1;
        }
        
        .url-title {
            font-weight: 600;
            color: var(--primary-color);
            margin-bottom: 0.25rem;
        }
        
        .url-original {
            font-size: 0.875rem;
            color: #666666;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 400px;
        }
        
        .url-stats {
            font-size: 0.75rem;
            color: #888888;
            margin-top: 0.25rem;
        }
        
        .url-actions {
            display: flex;
            gap: 0.5rem;
        }
        
        /* QR code container */
        .qr-container {
            display: flex;
            justify-content: center;
            margin: 1rem 0;
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .fadeIn {
            animation: fadeIn 0.5s ease-in-out;
        }
        
        /* Sidebar styling */
        .stSidebar {
            background-color: var(--card-color);
        }
        
        /* Footer */
        .footer {
            text-align: center;
            margin-top: 2rem;
            padding: 1rem 0;
            border-top: 1px solid #EEEEEE;
            font-size: 0.875rem;
            color: #888888;
        }
        
        /* Link styling */
        a {
            color: var(--primary-color);
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .header-title {
                font-size: 1.75rem;
            }
            
            .url-original {
                max-width: 200px;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'urls' not in st.session_state:
    # Try to load from file
    if os.path.exists('urls.json'):
        try:
            with open('urls.json', 'r') as f:
                st.session_state.urls = json.load(f)
        except:
            st.session_state.urls = {}
    else:
        st.session_state.urls = {}

if 'domain' not in st.session_state:
    st.session_state.domain = "http://linksnip.io/"

# Functions for URL shortening
def is_valid_url(url):
    """Basic URL validation"""
    if not url:
        return False
    if not url.startswith(('http://', 'https://')):
        return False
    return True

def generate_short_code(length=6):
    """Generate a random short code"""
    return generate(size=length)

def create_custom_short_url(custom_code):
    """Validate and create a custom short URL"""
    if not custom_code:
        return False, "Custom code cannot be empty"
    
    if custom_code in st.session_state.urls:
        return False, "This custom code is already in use"
    
    if not all(c in string.ascii_letters + string.digits + '-_' for c in custom_code):
        return False, "Custom code can only contain letters, numbers, hyphens, and underscores"
        
    return True, custom_code

def save_urls():
    """Save URLs to a JSON file"""
    with open('urls.json', 'w') as f:
        json.dump(st.session_state.urls, f)

def generate_qr_code(url):
    """Generate a QR code for the given URL"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#0066FF", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

def update_click_count(short_code):
    """Update the click count for a URL"""
    if short_code in st.session_state.urls:
        st.session_state.urls[short_code]["clicks"] += 1
        st.session_state.urls[short_code]["last_clicked"] = datetime.datetime.now().isoformat()
        save_urls()

def time_ago(timestamp_str):
    """Convert timestamp to 'time ago' format"""
    if not timestamp_str:
        return "Never"
        
    timestamp = datetime.datetime.fromisoformat(timestamp_str)
    now = datetime.datetime.now()
    delta = now - timestamp
    
    if delta.days > 365:
        years = delta.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif delta.days > 30:
        months = delta.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif delta.days > 0:
        return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
    elif delta.seconds > 3600:
        hours = delta.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif delta.seconds > 60:
        minutes = delta.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

# Apply custom CSS
local_css()

# Header
st.markdown('<div class="header"><div class="header-logo">✂️</div><h1 class="header-title">LinkSnip</h1></div>', unsafe_allow_html=True)
st.markdown("<p>Transform long URLs into concise, shareable links.</p>", unsafe_allow_html=True)

# Main content area
with st.container():
    st.markdown('<div class="card fadeIn">', unsafe_allow_html=True)
    
    # URL Input form
    long_url = st.text_input("Enter your long URL", placeholder="https://example.com/very/long/url/that/needs/shortening")
    
    # Advanced options expander
    with st.expander("Advanced Options"):
        col1, col2 = st.columns(2)
        with col1:
            custom_code = st.text_input("Custom short code (optional)", placeholder="my-link")
        with col2:
            expiration_days = st.number_input("Expiration (days, 0 = never)", min_value=0, value=0)
    
    # Submit button
    if st.button("Shorten URL"):
        if not is_valid_url(long_url):
            st.error("Please enter a valid URL starting with http:// or https://")
        else:
            # Generate or validate custom short code
            if custom_code:
                valid, result = create_custom_short_url(custom_code)
                if not valid:
                    st.error(result)
                    short_code = None
                else:
                    short_code = result
            else:
                short_code = generate_short_code()
            
            # If we have a valid short code, create the URL
            if short_code:
                expiration_date = None
                if expiration_days > 0:
                    expiration_date = (datetime.datetime.now() + datetime.timedelta(days=expiration_days)).isoformat()
                
                st.session_state.urls[short_code] = {
                    "original_url": long_url,
                    "created_at": datetime.datetime.now().isoformat(),
                    "expiration_date": expiration_date,
                    "clicks": 0,
                    "last_clicked": None
                }
                save_urls()
                
                short_url = f"{st.session_state.domain}{short_code}"
                
                # Display success message and shortened URL
                st.success(f"URL shortened successfully!")
                
                # URL display and copy functionality
                st.markdown(f"""
                <div style="margin: 1rem 0; padding: 1rem; background-color: #F1F9FF; border-radius: 4px; border-left: 4px solid var(--primary-color);">
                    <div style="font-weight: 600; margin-bottom: 0.5rem;">Your shortened URL:</div>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <input type="text" value="{short_url}" id="shortUrl" 
                            style="flex-grow: 1; padding: 0.5rem; border: 1px solid #DDDDDD; border-radius: 4px; font-size: 1rem;"
                            readonly onclick="this.select();">
                        <button onclick="navigator.clipboard.writeText('{short_url}'); this.innerText='Copied!'; setTimeout(() => this.innerText='Copy', 2000);" 
                            class="copy-btn">Copy</button>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Generate and display QR code
                qr_code_image = generate_qr_code(short_url)
                st.markdown('<div class="qr-container">', unsafe_allow_html=True)
                st.image(qr_code_image, caption="Scan this QR code", width=200)
                st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# URL History
if st.session_state.urls:
    st.markdown("## Your URLs")
    
    # Sort URLs by creation date (newest first)
    sorted_urls = sorted(
        st.session_state.urls.items(),
        key=lambda x: x[1]["created_at"],
        reverse=True
    )
    
    # Create a dataframe for display
    urls_data = []
    for code, data in sorted_urls:
        # Check if URL is expired
        expired = False
        if data["expiration_date"]:
            expiration_date = datetime.datetime.fromisoformat(data["expiration_date"])
            if datetime.datetime.now() > expiration_date:
                expired = True
        
        urls_data.append({
            "short_code": code,
            "original_url": data["original_url"],
            "short_url": f"{st.session_state.domain}{code}",
            "created_at": datetime.datetime.fromisoformat(data["created_at"]),
            "clicks": data["clicks"],
            "last_clicked": time_ago(data["last_clicked"]),
            "expired": expired
        })
    
    df = pd.DataFrame(urls_data)
    
    # Display each URL as a card
    for _, row in df.iterrows():
        status_color = "#DC2626" if row["expired"] else "#10B981"
        status_text = "Expired" if row["expired"] else "Active"
        
        st.markdown(f"""
        <div class="url-card">
            <div class="url-details">
                <div class="url-title">{row["short_url"]}</div>
                <div class="url-original">{row["original_url"]}</div>
                <div class="url-stats">
                    <span style="color: {status_color}; font-weight: 600;">●</span> {status_text} | 
                    Created: {row["created_at"].strftime("%Y-%m-%d")} | 
                    Clicks: {row["clicks"]} | 
                    Last clicked: {row["last_clicked"]}
                </div>
            </div>
            <div class="url-actions">
                <button onclick="navigator.clipboard.writeText('{row["short_url"]}'); this.innerText='Copied!'; setTimeout(() => this.innerText='Copy', 2000);" 
                    class="copy-btn">Copy</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Sidebar with settings
with st.sidebar:
    st.markdown("## Settings")
    
    # Domain setting
    new_domain = st.text_input("Custom domain", value=st.session_state.domain)
    if new_domain != st.session_state.domain:
        if not new_domain.endswith('/'):
            new_domain += '/'
        st.session_state.domain = new_domain
    
    # Export/Import functionality
    st.markdown("### Export/Import")
    
    # Export
    if st.button("Export URLs"):
        # Convert to CSV
        if st.session_state.urls:
            export_data = []
            for code, data in st.session_state.urls.items():
                export_data.append({
                    "short_code": code,
                    "original_url": data["original_url"],
                    "created_at": data["created_at"],
                    "expiration_date": data["expiration_date"] or "Never",
                    "clicks": data["clicks"]
                })
            
            df_export = pd.DataFrame(export_data)
            csv = df_export.to_csv(index=False)
            
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="linksnip_urls.csv",
                mime="text/csv"
            )
        else:
            st.warning("No URLs to export")
    
    # Clear all URLs
    if st.button("Clear All URLs"):
        st.session_state.urls = {}
        save_urls()
        st.success("All URLs have been cleared")
    
    # About section
    st.markdown("### About LinkSnip")
    st.markdown("""
    LinkSnip is a URL shortening tool that helps you create concise, 
    shareable links from long URLs. Features include:
    
    - Custom short codes
    - URL expiration settings
    - QR code generation
    - Click tracking
    
    Created with ❤️ using Streamlit
    """)

# Footer
st.markdown("""
<div class="footer">
    © 2025 LinkSnip | A Simple URL Shortener 
</div>
""", unsafe_allow_html=True)
