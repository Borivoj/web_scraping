import requests
import json
from bs4 import BeautifulSoup
import pandas as pd


def get_brokers_postal_code_2(postal_code):
    
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

# Test the function
get_brokers_postal_code_2('9000')

4 number DOT 3 numbers DOT 3 numbers