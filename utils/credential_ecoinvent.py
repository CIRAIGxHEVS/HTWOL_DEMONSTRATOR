import requests
import streamlit as st
import ecoinvent_interface as ei

def test_ecoinvent_connection(username, password):
    try:
        # Crée une instance de Settings avec les identifiants fournis
        settings = ei.Settings(username=username, password=password)
        # Crée une instance de EcoinventRelease pour tester la connexion
        release = ei.EcoinventRelease(settings)
        # Teste la connexion en listant les versions disponibles
        versions = release.list_versions()
        # Si tout se passe bien, les identifiants sont valides
        st.error(":white_check_mark: Credentials are valid!")
        return True
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            st.error(":x: Invalid username and/or password, please try again.")
        else:
            st.error(f":x: HTTP Error: {str(e)}")
    except requests.exceptions.ConnectionError:
        st.error(":x: Cannot connect to the internet, please try again later.")
    except Exception as e:
        st.error(f":x: An unexpected error occurred: {str(e)}")
    return False
