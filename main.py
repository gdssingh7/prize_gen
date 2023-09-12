import streamlit as st
import pandas as pd
import random
def main():
    st.title("Prize Generator App")

    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx", key="file_uploader")

    if uploaded_file is not None:
        data = pd.read_excel(uploaded_file)
        st.write(data.head())

        # Selecting the required columns
        ticket_col = st.selectbox("Select the column for number of tickets bought:", [""] + list(data.columns), key="ticket_column")
        city_col = st.selectbox("Select the column for cities:", [""] + list(data.columns), key="city_column")
        
        if ticket_col and city_col:
            # Convert ticket_col to integer
            data[ticket_col] = data[ticket_col].astype(int)
            
            if 'Assigned Tickets' not in data.columns:
                if st.button("Assign Ticket Numbers"):
                    data = assign_ticket_numbers(data, ticket_col)
                    st.write(data.head())
                    st.session_state.data = data  # Store in session state
            else:
                st.write(data.head())
            
            # Selecting number of random winners
            num_winners = st.number_input("Enter the number of winners:", min_value=1, max_value=len(data), value=5, key="num_winners")
            
            if st.button("Select Winners"):
                winners = select_random_winners(data, num_winners)
                st.write("Winners:")
                st.write(winners)
                
            # Selecting special winners from a city
            special_city = st.selectbox("Select a city for special prizes:", [""] + list(data[city_col].unique()), key="special_city")
            
            if special_city:
                max_special_winners = len(data[data[city_col] == special_city])
                default_value = min(2, max_special_winners)
                num_special_winners = st.number_input("Enter the number of special winners:", min_value=1, max_value=max_special_winners, value=default_value, key="num_special_winners")

                if st.button("Select Special Winners"):
                    special_winners = select_special_winners(data, city_col, special_city, num_special_winners)
                    st.write(f"Special Winners from {special_city}:")
                    st.write(special_winners)

def assign_ticket_numbers(data, ticket_col):
    ticket_counter = 1
    ticket_numbers = []

    for _, row in data.iterrows():
        num_tickets = int(row[ticket_col])  # Ensure it's an integer
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
        winners.append(winner_info)

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
        city_winners.append(winner_info)

    return pd.DataFrame(city_winners)

if __name__ == "__main__":
    main()
