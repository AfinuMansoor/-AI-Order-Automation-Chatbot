import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

# Product catalog
PRODUCTS = {
    "Smartphone": "128GB, Dual SIM, AMOLED display",
    "Laptop": "16GB RAM, 512GB SSD, Intel i7",
    "Headphones": "Wireless, Noise Cancelling",
    "Smartwatch": "Fitness tracker, Heart-rate monitor",
    "Camera": "DSLR, 24MP, 4K Video",
}

CUSTOMER_CARE_NUMBER = "+1-800-555-1234"

# Streamlit page configuration
st.set_page_config(page_title="🛍 Order Bot", layout="centered")
st.markdown("<h1 style='text-align:center;'>🛍 AI Order Automation Chatbot</h1>", unsafe_allow_html=True)

# Custom CSS for modern clean layout
st.markdown("""
    <style>
    .user-msg, .bot-msg {
        padding: 12px 16px;
        border-left: 4px solid;
        background: #f9f9f9;
        color: #333;
        margin: 10px 0;
        font-size: 1rem;
        border-radius: 8px;
    }
    .user-msg {
        border-color: #4CAF50;
    }
    .bot-msg {
        border-color: #2196F3;
    }
    .timestamp {
        display: block;
        margin-top: 4px;
        font-size: 0.75em;
        color: #666;
    }
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding-right: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "chat_history" not in st.session_state:
    greeting = "Good morning!" if datetime.now().hour < 12 else "Good afternoon!" if datetime.now().hour < 18 else "Good evening!"
    st.session_state.chat_history = [
        {"role": "user", "parts": ["Hello"], "time": datetime.now()},
        {"role": "model", "parts": [f"Hi! I’m your order assistant bot. {greeting} What would you like to order today?"], "time": datetime.now()},
    ]

if "product_selected" not in st.session_state:
    st.session_state.product_selected = None

if "talk_customer_care" not in st.session_state:
    st.session_state.talk_customer_care = False

# Sidebar for product selection and other controls
with st.sidebar:
    st.header("🛒 Product Selection")
    product = st.selectbox("Choose a product:", ["-- Select --"] + list(PRODUCTS.keys()))
    if product != "-- Select --":
        st.session_state.product_selected = product
        st.success(f"Product Selected: {product}")
        st.markdown(f"*Details*: {PRODUCTS[product]}")

    st.markdown("---")

    # Toggle talk to customer care mode
    talk_care = st.checkbox("💬 Talk to Customer Care", value=st.session_state.talk_customer_care)
    st.session_state.talk_customer_care = talk_care

    st.markdown("---")

    # Clear chat history button (resets session state)
    if st.button("🧹 Clear Chat History"):
        st.session_state.chat_history = [
            {"role": "user", "parts": ["Hello"], "time": datetime.now()},
            {"role": "model", "parts": [f"Hi again! Let’s start a fresh order. What would you like to order today?"], "time": datetime.now()},
        ]
        st.session_state.product_selected = None
        st.session_state.talk_customer_care = False
        st.warning("Chat history cleared! Please refresh the page to reset completely.")

    # Display chat log text for reference
    st.markdown("#### 💬 Chat Log (Text View)")
    for msg in st.session_state.chat_history[2:]:
        st.markdown(f"- {msg['time'].strftime('%H:%M')} *{msg['role'].capitalize()}*: {msg['parts'][0]}")

# Display chat history in scrollable container
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for msg in st.session_state.chat_history[2:]:  # Skip initial greeting
    role_class = "user-msg" if msg["role"] == "user" else "bot-msg"
    st.markdown(
        f"<div class='{role_class}'><b>{'You' if msg['role'] == 'user' else '🤖 Bot'}:</b><br>{msg['parts'][0]}<span class='timestamp'>{msg['time'].strftime('%H:%M')}</span></div>",
        unsafe_allow_html=True
    )
st.markdown("</div>", unsafe_allow_html=True)

# User input
user_input = st.chat_input("Type your message...")

if user_input:
    selected_product = st.session_state.product_selected
    input_lower = user_input.lower()
    product_context = ""

    if st.session_state.talk_customer_care:
        # If talking to customer care, respond with a fixed message including the number
        bot_reply = f"Please call our Customer Care at {CUSTOMER_CARE_NUMBER} for assistance."
        # Append user message
        st.session_state.chat_history.append({"role": "user", "parts": [user_input], "time": datetime.now()})
        st.markdown(
            f"<div class='user-msg'><b>You:</b><br>{user_input}<span class='timestamp'>{datetime.now().strftime('%H:%M')}</span></div>",
            unsafe_allow_html=True
        )
        # Append bot message
        st.session_state.chat_history.append({"role": "model", "parts": [bot_reply], "time": datetime.now()})
        st.markdown(
            f"<div class='bot-msg'><b>🤖 Bot:</b><br>{bot_reply}<span class='timestamp'>{datetime.now().strftime('%H:%M')}</span></div>",
            unsafe_allow_html=True
        )
    else:
        # Normal order flow - add product context if selected and not mentioned
        if selected_product and selected_product.lower() not in input_lower:
            product_context = f"I would like to order a {selected_product} ({PRODUCTS[selected_product]}). "
        final_message = product_context + user_input

        # Append user message
        st.session_state.chat_history.append({"role": "user", "parts": [final_message], "time": datetime.now()})
        st.markdown(
            f"<div class='user-msg'><b>You:</b><br>{user_input}<span class='timestamp'>{datetime.now().strftime('%H:%M')}</span></div>",
            unsafe_allow_html=True
        )

        # Gemini response
        response = model.generate_content(
            [{"role": m["role"], "parts": m["parts"]} for m in st.session_state.chat_history]
        )
        bot_reply = response.text

        # Append and show bot message
        st.session_state.chat_history.append({"role": "model", "parts": [bot_reply], "time": datetime.now()})
        st.markdown(
            f"<div class='bot-msg'><b>🤖 Bot:</b><br>{bot_reply}<span class='timestamp'>{datetime.now().strftime('%H:%M')}</span></div>",
            unsafe_allow_html=True
        )