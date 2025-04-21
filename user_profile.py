import streamlit as st

# User profile
def create_user_profile():
    st.subheader("Create Your Travel Profile")
    name = st.text_input("Enter your name:")
    favorite_type = st.selectbox("What's your favorite type of destination?", ["Beaches", "Mountains", "Culture", "Adventure"])
    budget = st.slider("What’s your travel budget? (in USD)", 500, 10000, 2000)  # Default: 2000 USD
    
    if st.button("Save Profile"):
        st.session_state['user_profile'] = {
            "name": name,
            "favorite_type": favorite_type,
            "budget": budget,
        }
        st.success("Profile saved!")

# Display profile
def show_user_profile():
    if 'user_profile' in st.session_state:
        profile = st.session_state['user_profile']
        st.write(f"Name: {profile['name']}")
        st.write(f"Favorite Type: {profile['favorite_type']}")
        st.write(f"Budget: ${profile['budget']}")
    else:
        st.warning("No profile found! Please create your profile.")
