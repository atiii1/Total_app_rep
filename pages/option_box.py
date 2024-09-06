import streamlit as st

# Define the menu options
menu_options = [
    "Option 1: Show statement 1",
    "Option 2: Show statement 2",
    "Option 3: Show statement 3",
    "Option 4: Show statement 4",
    "Option 5: Show statement 5",
    "Option 6: Show statement 6"
]

# Create a selectbox for the menu
selected_option = st.selectbox("Choose an option from the menu:", menu_options)

# Display a statement based on the selected option
if selected_option == "Option 1: Show statement 1":
    st.write("You selected Option 1: Here is statement 1.")
elif selected_option == "Option 2: Show statement 2":
    st.write("You selected Option 2: Here is statement 2.")
elif selected_option == "Option 3: Show statement 3":
    st.write("You selected Option 3: Here is statement 3.")
elif selected_option == "Option 4: Show statement 4":
    st.write("You selected Option 4: Here is statement 4.")
elif selected_option == "Option 5: Show statement 5":
    st.write("You selected Option 5: Here is statement 5.")
elif selected_option == "Option 6: Show statement 6":
    st.write("You selected Option 6: Here is statement 6.")
else:
    st.write("Please select an option from the menu.")
