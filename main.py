import streamlit as st
import pandas as pd
import random
import base64

def main():
    st.title("Prize Generator App")

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
            st.session_state.data = assign_ticket_numbers(st.session_state.data, ticket_col)
            st.write(st.session_state.data)

        if 'Assigned Tickets' in st.session_state.data.columns:
            num_winners = st.number_input("Enter the number of winners:", min_value=1, max_value=len(st.session_state.data))
            if st.button("Select Winners"):
                winners, winning_tickets = select_random_winners(st.session_state.data, num_winners)
                st.write("Winners:")
                st.write(winners)
                st.write("Winning Tickets:")
                st.write(winning_tickets)
                st.markdown(get_table_download_link(winners, "winners.csv", "Download Winners Data"), unsafe_allow_html=True)

        if city_col:
            special_city = st.selectbox("Select a city for special prizes:", list(st.session_state.data[city_col].unique()))
            if special_city and 'Assigned Tickets' in st.session_state.data.columns:
                max_special_winners = len(st.session_state.data[st.session_state.data[city_col] == special_city])
                num_special_winners = st.number_input("Enter the number of special winners:", min_value=1, max_value=max_special_winners)
                if st.button("Select Special Winners"):
                    special_winners, special_winning_tickets = select_special_winners(st.session_state.data, city_col, special_city, num_special_winners)
                    st.write(f"Special Winners from {special_city}:")
                    st.write(special_winners)
                    st.write("Winning Tickets:")
                    st.write(special_winning_tickets)
                    st.markdown(get_table_download_link(special_winners, "special_winners.csv", "Download Special Winners Data"), unsafe_allow_html=True)
            elif 'Assigned Tickets' not in st.session_state.data.columns:
                st.warning("Please assign ticket numbers before selecting special winners.")

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
        winner_info['Winning Ticket'] = ticket
        winners.append(winner_info)

    return pd.DataFrame(winners), winning_tickets

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

    return pd.DataFrame(city_winners), winning_city_tickets

def get_table_download_link(df, filename, link_text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

if __name__ == "__main__":
    main()
