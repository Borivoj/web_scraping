import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
import re

def get_brokers_postal_code(postal_code):
    
    URL_S = 'https://www.makelaarinverzekeringen.be/views/ajax'

    params = {
        'dealer-name': '',
        'geo_center[coordinates][lat]': '',
        'geo_center[coordinates][lng]': '',
        'geo_center[geocoder][geolocation_geocoder_address]': postal_code,# Hre is the postal code param
        'geo': '15',
        '_wrapper_format': 'drupal_ajax',
        'view_name': 'locator',
        'view_display_id': 'block_1',
        'view_args': '',
        'view_path': '/node/1903217',
        'view_base_path': '',
        'view_dom_id': '864b5379be4926591f390138fa665d2aacd99ef521c3e6374149bbf194e0f396',
        'pager_element': '0',
        '_drupal_ajax': '1',
        'ajax_page_state[theme]': 'brocom',
        'ajax_page_state[theme_token]': '',
        'ajax_page_state[libraries]': 'ajax_loader/ajax_loader.throbber,brocom/global-styling,brocom/locator_search_block,brocom/locator_search_form,brocom/typekit,classy/base,classy/messages,classy/node,core/drupal.autocomplete,core/normalize,dms_core/gin,eu_cookie_compliance/eu_cookie_compliance_default,facebook_pixel/facebook_pixel,geolocation/location_input.geocoder,geolocation/map_center.fitlocations,geolocation_google_maps/commonmap.google,geolocation_google_maps/google,geolocation_google_maps/mapfeature.control_locate,geolocation_google_maps/mapfeature.control_maptype,geolocation_google_maps/mapfeature.control_zoom,geolocation_google_maps/mapfeature.marker_infowindow,geolocation_google_places_api/geolocation_google_places_api.geocoder.googleplacesapi,system/base,views/views.ajax,views/views.module,views_autocomplete_filters/drupal.views-autocomplete-filters',
    }

    # Send the GET request with parameters
    response = requests.get(URL_S, params=params)
    resp_complete = response.json()
    table_of_brokers_html = resp_complete[2]['data']
    soup = BeautifulSoup(table_of_brokers_html, 'html.parser')

    dealers = soup.find_all('div', class_='dealer')
    dtBRK = pd.DataFrame(columns=["website", "name"])
    for dealer in dealers:
        a_tag = dealer.find('a', class_='action website')
        # class = column title
        if a_tag and 'href' in a_tag.attrs:
            url = a_tag['href']
        else:
            url = ""
        
        name_of_broker = dealer.find('div', class_='column title')
        
        dtBRK_new = pd.DataFrame(data = [[url,name_of_broker.get_text(strip=True)]], columns=["website", "name"])
        dtBRK = pd.concat([dtBRK, dtBRK_new], ignore_index=True)

    return(dtBRK.drop_duplicates())

def get_websites_postal_code(postal_code):
    
    URL_S = 'https://www.makelaarinverzekeringen.be/views/ajax'

    params = {
        'dealer-name': '',
        'geo_center[coordinates][lat]': '',
        'geo_center[coordinates][lng]': '',
        'geo_center[geocoder][geolocation_geocoder_address]': postal_code,# Hre is the postal code param
        'geo': '15',
        '_wrapper_format': 'drupal_ajax',
        'view_name': 'locator',
        'view_display_id': 'block_1',
        'view_args': '',
        'view_path': '/node/1903217',
        'view_base_path': '',
        'view_dom_id': '864b5379be4926591f390138fa665d2aacd99ef521c3e6374149bbf194e0f396',
        'pager_element': '0',
        '_drupal_ajax': '1',
        'ajax_page_state[theme]': 'brocom',
        'ajax_page_state[theme_token]': '',
        'ajax_page_state[libraries]': 'ajax_loader/ajax_loader.throbber,brocom/global-styling,brocom/locator_search_block,brocom/locator_search_form,brocom/typekit,classy/base,classy/messages,classy/node,core/drupal.autocomplete,core/normalize,dms_core/gin,eu_cookie_compliance/eu_cookie_compliance_default,facebook_pixel/facebook_pixel,geolocation/location_input.geocoder,geolocation/map_center.fitlocations,geolocation_google_maps/commonmap.google,geolocation_google_maps/google,geolocation_google_maps/mapfeature.control_locate,geolocation_google_maps/mapfeature.control_maptype,geolocation_google_maps/mapfeature.control_zoom,geolocation_google_maps/mapfeature.marker_infowindow,geolocation_google_places_api/geolocation_google_places_api.geocoder.googleplacesapi,system/base,views/views.ajax,views/views.module,views_autocomplete_filters/drupal.views-autocomplete-filters',
    }

    # Send the GET request with parameters
    response = requests.get(URL_S, params=params)
    resp_complete = response.json()
    table_of_brokers_html = resp_complete[2]['data']
    soup = BeautifulSoup(table_of_brokers_html, 'html.parser')

    website_divs = soup.find_all('div', class_='website')
    div_name_br = soup.find_all('div', class_='column title')
    
    dtBRK = pd.DataFrame(columns=['website'])
    dtBRKn = pd.DataFrame(columns=['name'])
    for div in website_divs:
        a_tag = div.find('a')
        # class = column title
        if a_tag and 'href' in a_tag.attrs:
            url = a_tag['href']
            dtBRK_new = pd.DataFrame(data = [url], columns=["website"])
            dtBRK = pd.concat([dtBRK, dtBRK_new], ignore_index=True)

    for div in div_name_br:
        dtBRKn_new = pd.DataFrame(data = [div.get_text(strip=True)], columns=["name"])
        dtBRKn = pd.concat([dtBRKn, dtBRKn_new], ignore_index=True)
    dtBRK = pd.concat([dtBRK, dtBRKn], axis = 1)
    return(dtBRK.drop_duplicates())

def find_rows_in_string(df, column_name, input_string):
    """
    Finds rows in the specified column of the DataFrame that are substrings of the input string.

    Parameters:
    df (pd.DataFrame): The DataFrame to search.
    column_name (str): The name of the column to search.
    input_string (str): The string to search within.

    Returns:
    list: A list of row indices where the column value is a substring of the input string.
    """
    # Ensure the column exists in the DataFrame
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")

    # Find rows where the column value is a substring of the input string
    matching_rows = df[df[column_name].apply(lambda x: x in input_string)].index.tolist()
    
    return matching_rows

def match_belgian_id_num(input_string):
    matches = re.findall('[0-9]{4}\.[0-9]{3}\.[0-9]{3}', input_string)
    return(matches)