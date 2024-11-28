import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import base64

# Function to convert an image to base64
def get_base64_of_image(image_file):
    with open(image_file, "rb") as img:
        return base64.b64encode(img.read()).decode()

# Set the path to your local image
image_path = "image.jpg"  # Replace with your local image path
img_base64 = get_base64_of_image(image_path)

# Define the CSS for the background image
background_image = f"""
<style>
.stApp {{
    background-image: url(data:image/jpeg;base64,{img_base64});  /* Use base64 encoded image */
    background-size: cover;
    background-position: center;
}}
</style>
"""

# Inject the CSS into the Streamlit app
st.markdown(background_image, unsafe_allow_html=True)
# List of student names
Group4= ["Rokhaya Diop", "Anna Niane", "Thierno Souleymane Diallo"]

# Display student names
st.sidebar.header("Group4")
for name in Group4:
    st.sidebar.write(name)
# Function to load and display data
def load(dataframe, title):
    st.markdown(f"<h2>{title}</h2>", unsafe_allow_html=True)
    st.subheader('Data Dimension')
    st.write(f'{dataframe.shape[0]} rows, {dataframe.shape[1]} columns')
    st.dataframe(dataframe)

# Function to scrape car data
def scrape_cars(url, last_page_index):
    df = pd.DataFrame()
    for p in range(1, last_page_index + 1):
        page_url = f'{url}?page={p}'
        res = requests.get(page_url)
        soup = bs(res.text, 'html.parser')
        containers = soup.find_all('div', class_='listings-cards__list-item')
        data = []
        for container in containers:
            try:
                gen2 = container.find('div', class_='listing-card__header__tags').text.strip()
                B = re.findall(r'[A-Z][a-z]*|[A-Z]+|\d{4}', gen2)

                A = []
                temp = ''
                for item in B:
                    if item.isalpha() and item.isupper():
                        temp += item
                    else:
                        if temp:
                            A.append(temp)
                            temp = ''
                        A.append(item)
                if temp:
                    A.append(temp)

                if len(A) < 4:
                    continue

                condition = A[0]
                brand = A[1]
                year = A[2]
                address = container.find('div', class_="listing-card__header__location").text.strip()
                price = container.find('span', class_='listing-card__price__value').text.strip().replace("\u202f", "").replace("F Cfa", "")
                image = container.find('div', class_='listing-card__image__inner').img['src']
                dic = {
                    'condition': condition,
                    'brand': brand,
                    'year': year,
                    'address': address,
                    'price': price,
                    'image': image
                }
                data.append(dic)
            except Exception as e:
                print(f"Error processing container: {e}")
                continue
        df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
    return df

# Function to scrape equipment and parts
def scrape_equipment_and_parts(last_page_index):
    df = pd.DataFrame()
    for p in range(1, last_page_index + 1):
        url = f'https://www.expat-dakar.com/equipements-pieces?page={p}'
        res = requests.get(url)
        soup = bs(res.text, 'html.parser')
        containers = soup.find_all('div', class_='listings-cards__list-item')
        data = []
        for container in containers:
            try:
                condition = container.find('div', class_='listing-card__header__tags').text.strip()
                description = container.find('div', class_='listing-card__header__title').text.strip()
                address = container.find('div', class_="listing-card__header__location").text.strip().replace(',\n', ' ')
                price = container.find('span', class_='listing-card__price__value').text.strip().replace("\u202f", "").replace("F Cfa", "")
                image = container.find('div', class_='listing-card__image__inner').img['src']
                dic = {
                    'condition': condition,
                    'description': description,
                    'address': address,
                    'price': price,
                    'image': image
                }
                data.append(dic)
            except Exception as e:
                print(f"Error processing container: {e}")
                continue
        df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
    return df

# Streamlit app setup
st.title("Group4 DATA SCRAPER APP")

# Sidebar inputs
st.sidebar.header("User  Input Features")
pages = st.sidebar.selectbox('Pages indexes', list(range(2, 600)))
choices = st.sidebar.selectbox('Options', ['Scrape data using BeautifulSoup', 'Download scraped data', 'Dashboard of the data', 'Fill the form'])

if choices == 'Scrape data using BeautifulSoup':
    # Scrape data
    voiture_data = scrape_cars("https://www.expat-dakar.com/voitures", pages)
    motocycle_data = scrape_cars("https://www.expat-dakar.com/motos-scooters", pages)
    equipement_data = scrape_equipment_and_parts(pages)

    # Display buttons for each DataFrame
    if st.button('Show Vehicles Data'):
        load(voiture_data, 'Vehicles data')
    if st.button('Show Motorcycle Data'):
        load(motocycle_data, 'Motorcycle data')
    if st.button('Show Equipment Data'):
        load(equipement_data, 'Equipment data')

elif choices == 'Download scraped data':
    # Load existing data
    voiture = pd.read_csv('datas/Voitures.csv')
    motocycle = pd.read_csv('datas/cars.csv')
    equipement = pd.read_csv('datas/equipement.csv')

    # Display buttons for each DataFrame
    if st.button('Show Vehicles Data'):
        load(voiture, 'Vehicles data')
    if st.button('Show Motorcycle Data'):
        load(motocycle, 'Motorcycles data')
    if st.button('Show Equipment Data'):
        load(equipement, 'Equipment data')

elif choices == 'Dashboard of the data':
    # Load data for dashboard
    df1 = pd.read_csv('datas/vehicule.csv')
    df2 = pd.read_csv('datas/moto.csv')
    df3 = pd.read_csv('datas/pièces.csv')

    # Dashboard visualizations
    col1, col2, col3 = st.columns(3)

    with col1:
        plot1 = plt.figure(figsize=(11, 7))
        color = (0.2, 0.4, 0.2, 0.6)
        plt.bar(df1.brand.value_counts()[:5].index, df1.brand.value_counts()[:5].values, color=color)
        plt.title('Top 5 Vehicle Brands Sold')
        plt.xlabel('Brand')
        st.pyplot(plot1)

    with col2:
        plot2 = plt.figure(figsize=(11, 7))
        color = (0.5, 0.7, 0.9, 0.6)
        plt.bar(df2.brand.value_counts()[:5].index, df2.brand.value_counts()[:5].values, color=color)
        plt.title('Top 5 Motorcycle Brands Sold')
        plt.xlabel('Brand')
        st.pyplot(plot2)

    col4, col5, col6 = st.columns(3)

    with col4:
        plot3 = plt.figure(figsize=(11, 7))
        sns.lineplot(data=df1, x="year", y="price")
        plt.title('Price Variation by Vehicle Year')
        st.pyplot(plot3)

    with col5:
        plot4 = plt.figure(figsize=(11, 7))
        sns.lineplot(data=df2, x="year", y="price")
        plt.title('Price Variation by Motorcycle Year')
        st.pyplot(plot4)

    with col6:
        plot5 = plt.figure(figsize=(11, 7))
        sns.lineplot(data=df3, x="condition", y="price")
        plt.title('Price Variation by Equipment Condition')
        st.pyplot(plot5)

else:
    st.markdown("""
    <iframe src="https://ee.kobotoolbox.org/x/VbQKDKG3" width="800" height="1100"></iframe>
    """, unsafe_allow_html=True)