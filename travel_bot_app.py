import streamlit as st
import requests

from user_profile import create_user_profile, show_user_profile
from geopy.distance import geodesic

api_key = "573364392b1fdf8437832127e64599f5"

def get_weather(location):
    #api_key = "573364392b1fdf8437832127e64599f5"
    base_url = f"http://api.weatherstack.com/current?access_key={api_key}&query={location}"
    response = requests.get(base_url)
    
    if response.status_code == 200:
        data = response.json()
        weather = data['current']['weather_descriptions']
        temp = round(data['current']['temperature'], 2)  # Convert Kelvin to Celsius
        return f"The weather in {location} is currently {weather} with a temperature of {temp}°C."
    else:
        return "Sorry, I couldn't fetch the weather for that location."

def get_coordinates_weatherstack(location):
    #api_key = "573364392b1fdf8437832127e64599f5"  # Replace with your API key
    base_url = f"http://api.weatherstack.com/current?access_key={api_key}&query={location}"
    response = requests.get(base_url)
    
    if response.status_code == 200:
        data = response.json()
        if "location" in data:
            lat = data["location"]["lat"]
            lon = data["location"]["lon"]
            return lat, lon
        else:
            return "No coordinates found for this location."
    else:
        return "Error fetching coordinates."

def recommend_destination_with_budget(preference, budget):
    recommendations = {
        "beaches": [
            {"name": "Bali", "cost": 1500},
            {"name": "Maldives", "cost": 4000},
            {"name": "Goa", "cost": 800},
        ],
        "mountains": [
            {"name": "Himalayas", "cost": 1200},
            {"name": "Swiss Alps", "cost": 5000},
            {"name": "Rocky Mountains", "cost": 2500},
        ],
    }
    
    # Filter destinations by budget
    return [place["name"] for place in recommendations.get(preference, []) if place["cost"] <= budget]


#Calculate distance from current location to recommended locations
def get_nearby_destinations(user_location, destinations):
    # Example destinations with coordinates
    destination_coords  = {}

    for city in destinations:
        destination_coords[city]=get_coordinates_weatherstack(city)
    
    nearby = []
    for name, coords in destination_coords.items():
        distance = geodesic(user_location, coords).km  # Calculate distance in kilometers
        if distance <= 300000:  # Customize the radius as needed
            nearby.append((name, round(distance, 2)))
    
    return nearby



# Create or view user profile
create_user_profile()
if st.button("Show Profile"):
    show_user_profile()

user_location = st.text_input("Enter your current location:")

st.title("Travel Bot")
preference = st.text_input("What kind of destination are you looking for? (e.g., beaches, mountains)")

filtered_recommendations=[]

#Based on user's profile
if 'user_profile' in st.session_state:
    user_budget = st.session_state['user_profile']['budget']
    filtered_recommendations = recommend_destination_with_budget(preference.lower(), user_budget)
    print(filtered_recommendations)
    st.write(f"Here are {preference} destinations within your budget: {', '.join(filtered_recommendations)}")
else:
    st.warning("Please create your profile to get budget-specific recommendations!")

if user_location:
    user_coords = get_coordinates_weatherstack(user_location)
    nearby_destinations = get_nearby_destinations(user_coords, filtered_recommendations)
    if nearby_destinations:
        st.write("Here are some nearby destinations:")
        for dest, dist in nearby_destinations:
            st.write(f"- {dest}: {dist} km away")
    else:
        st.write("No destinations found within the specified distance!")

#Recommendation based on a location

st.title("Travel Bot - Recommendation")

destination = st.text_input("Enter a destination you like:")

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder


# Example dataset
data = {
    "Destination": ["Bali", "Maldives", "Swiss Alps", "Kyoto", "Goa"],
    "Type": ["Beach", "Beach", "Mountains", "Culture", "Beach"],
    "Climate": ["Tropical", "Tropical", "Cold", "Moderate", "Tropical"],
    "Cost": [1500, 4000, 5000, 2000, 800],
    "Popularity Score": [90, 95, 85, 80, 88],
}
df = pd.DataFrame(data)

# Preprocess data
features = df[["Cost", "Popularity Score"]]
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)


similarity_matrix = cosine_similarity(scaled_features)

#Added more features-Categorical data
categories = df[["Type", "Climate"]]
encoder = OneHotEncoder()
encoded_categories = encoder.fit_transform(categories).toarray()

# Combine numerical and categorical features
final_features = np.concatenate((scaled_features, encoded_categories), axis=1)

# Calculate similarity
weights = [0.5, 0.3, 0.1, 0.05, 0.05, 0.05, 0.05, 0.1]  # Example weights
weighted_features = final_features * weights
similarity_matrix = cosine_similarity(weighted_features)


# Recommend similar destinations
def recommend(destination):
    idx = df[df["Destination"] == destination].index[0]
    similar_indices = similarity_matrix[idx].argsort()[::-1][1:4]  # Top 3 recommendations
    return df.iloc[similar_indices]["Destination"].values


if destination:
    recommendations = recommend(destination)
    st.write(f"If you like {destination}, you might also enjoy: {', '.join(recommendations)}")




# #Calculate distance from current location to recommended locations
# def get_nearby_destinations(user_location, destinations):
#     # Example destinations with coordinates
#     destination_coords = {
#         "Bali": (-8.3405, 115.0920),
#         "Maldives": (3.2028, 73.2207),
#         "Goa": (15.2993, 74.1240),
#         "Phuket": (7.8804, 98.3923),
#     }
    
#     nearby = []
#     for name, coords in destination_coords.items():
#         distance = geodesic(user_location, coords).km  # Calculate distance in kilometers
#         if distance <= 3000:  # Customize the radius as needed
#             nearby.append((name, round(distance, 2)))
    
#     return nearby


# Function to recommend destinations
# def recommend_destination(preference, subcategory=None):
#     recommendations = {
#         "beaches": {
#             "tropical": ["Bali", "Maldives", "Phuket"],
#             "peaceful": ["Fiji", "Seychelles", "Mauritius"],
#             "lively": ["Goa", "Miami Beach", "Ibiza"]
#         },
#         "mountains": {
#             "hiking": ["Himalayas", "Swiss Alps", "Rocky Mountains"],
#             "scenic": ["Andes", "Blue Ridge Mountains", "Kilimanjaro"],
#         },
#     }    
#     if subcategory:
#         return recommendations.get(preference, {}).get(subcategory, ["I’m not sure what to suggest for that specific type."])
#     else:
#         return list(recommendations.get(preference, {}).keys())  # Return subcategories if no specific one is chosen

#Based on user's preference
# if preference:
#     subcategories = recommend_destination(preference)
#     subcategory = st.selectbox(f"Choose a type of {preference} destination:", subcategories)
    
#     if subcategory:
#         refined_recommendations = recommend_destination(preference, subcategory)
#         st.write(f"Here are some {subcategory} {preference} destinations you might like: {', '.join(refined_recommendations)}")


# #Based on user's profile
# if 'user_profile' in st.session_state:
#     user_budget = st.session_state['user_profile']['budget']
#     filtered_recommendations = recommend_destination_with_budget(preference.lower(), user_budget)
#     st.write(f"Here are {preference} destinations within your budget: {', '.join(filtered_recommendations)}")
# else:
#     st.warning("Please create your profile to get budget-specific recommendations!")

# if user_location:
#     user_coords = get_coordinates_weatherstack(user_location)
#     nearby_destinations = get_nearby_destinations(user_coords, destination_coords)
#     if nearby_destinations:
#         st.write("Here are some nearby destinations:")
#         for dest, dist in nearby_destinations:
#             st.write(f"- {dest}: {dist} km away")
#     else:
#         st.write("No destinations found within the specified distance!")



# if "weather in" in user_input:
#     location = user_input.split("weather in")[-1].strip()
#     st.write(get_weather(location))
# elif "best time to visit" in user_input:
#     st.write("The best time to visit depends on the destination! For example, Paris is beautiful in spring (April to June).")
# elif "recommend a destination" in user_input:
#     st.write("How about Bali for its stunning beaches or Kyoto for its cherry blossoms?")
# elif user_input:
#     st.write("I'm still learning, but I can answer questions about destinations and travel times!")


