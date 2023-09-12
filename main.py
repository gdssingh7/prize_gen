import streamlit as st
import pandas as pd
import random
import time
import base64

def main():
    st.title("Prize Generator App")
    
    st.markdown("""
        <style>
            body {
                background-color: #E6E6FA;
            }
            .stButton>button {
                background-color: #4CAF50;
                color: white;
            }
        </style>
        """, unsafe_allow_html=True)

    if 'data' not in st.session_state:
        st.session_state.data = None

    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

    if uploaded_file:
        st.session_state.data = pd.read_excel(uploaded_file)
        st.write(st.session_state.data)

    if st.session_state.data is not None:
        ticket_col = st.selectbox("Select the column for number of tickets bought:", list(st.session_state.data.columns))
        city_col = st.selectbox("Select the column for cities:", list(st.session_state.data.columns))

        if ticket_col and 'Assigned Tickets' not in st.session_state.data.columns:
            if st.button("Assign Ticket Numbers"):
                st.session_state.data = assign_ticket_numbers(st.session_state.data, ticket_col)
                st.write(st.session_state.data)

        if 'Assigned Tickets' in st.session_state.data.columns:
            num_winners = st.number_input("Enter the number of winners:", min_value=1, max_value=len(st.session_state.data))
            if st.button("Select Winners"):
                winners = select_random_winners(st.session_state.data, num_winners)
                st.markdown(download_link(winners, "winners.csv", "Download Winners"), unsafe_allow_html=True)

        if city_col:
            special_city = st.selectbox("Select a city for special prizes:", list(st.session_state.data[city_col].unique()))
            if special_city and 'Assigned Tickets' in st.session_state.data.columns:
                max_special_winners = len(st.session_state.data[st.session_state.data[city_col] == special_city])
                num_special_winners = st.number_input("Enter the number of special winners:", min_value=1, max_value=max_special_winners)
                if st.button("Select Special Winners"):
                    special_winners = select_special_winners(st.session_state.data, city_col, special_city, num_special_winners)
                    st.markdown(download_link(special_winners, "special_winners.csv", "Download Special Winners"), unsafe_allow_html=True)

def assign_ticket_numbers(data, ticket_col):
    ticket_counter = 1
    ticket_numbers = []

    for _, row in data.iterrows():
        num_tickets = int(row[ticket_col])
        tickets_for_person = list(range(ticket_counter, ticket_counter + num_tickets))
        ticket_numbers.append(tickets_for_person)
        ticket_counter += num_tickets

    data['Assigned Tickets'] = ticket_numbers
    return data

def select_random_winners(data, p):
    all_tickets = [ticket for sublist in data['Assigned Tickets'] for ticket in sublist]
    winning_tickets = random.sample(all_tickets, p)

    winners = []
    for ticket in winning_tickets:
        winner_info = data[data['Assigned Tickets'].apply(lambda x: ticket in x)].iloc[0]
        winner_info['Winning Ticket'] = ticket
        winners.append(winner_info)
        st.write(f"Winner Ticket: {ticket}")
        st.write(winner_info)
        time.sleep(1)

    return pd.DataFrame(winners)

def select_special_winners(data, city_col, city, k):
    city_data = data[data[city_col] == city]
    all_city_tickets = [ticket for sublist in city_data['Assigned Tickets'] for ticket in sublist]
    
    if k > len(all_city_tickets):
        st.warning("The number of special prizes exceeds the total number of tickets from the selected city. Adjusting to maximum available.")
        k = len(all_city_tickets)
    
    winning_city_tickets = random.sample(all_city_tickets, k)
    
    city_winners = []
    for ticket in winning_city_tickets:
        winner_info = city_data[city_data['Assigned Tickets'].apply(lambda x: ticket in x)].iloc[0]
        winner_info['Winning Ticket'] = ticket
        city_winners.append(winner_info)
        st.write(f"Special Winner Ticket from {city}: {ticket}")
        st.write(winner_info)
        time.sleep(1)

    return pd.DataFrame(city_winners)

def download_link(object_to_download, download_filename, download_link_text):
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    b64 = base64.b64encode(object_to_download.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

if __name__ == "__main__":
    main()
