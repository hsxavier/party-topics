#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 14:26:32 2022

@author: skems

General functions to ease usage of Facebook's Graph API.
"""

import requests
import json
import os

def load_token_from_env(variable='TOKEN'):
    """
    Read a token (long sequence of characters
    that looks like a cryptographic key) from
    the environment `variable`. 
    
    Returns a str.
    """
    
    token = os.environ[variable]

    return token


def load_token_from_file(path):
    """
    Read a token (long sequence of characters
    that looks like a cryptographic key) from
    a file in `path` (str or Path). 
    
    Returns a str.
    """
    
    with open(path, 'r') as f:
        token = f.read().replace('\n', '')
    
    return token


def query_graph(query, token, api_url='https://graph.facebook.com/v14.0/', verbose=True):
    """
    Make a request for the Graph API (Facebook).
    
    Parameters
    ----------
    query : str
        Resource (endpoint) to use, along with parameters.
        E.g.: '103924785736259/feed?fields=id,created_time'
    token : str
        User access token (from https://developers.facebook.com/tools/explorer)
        of Page access token (obtained with an API request).
    api_url : str
        URL of the API host, plus the version.
    verbose : bool
        Whether to print the HTTP response status code.
        
    Returns
    -------
    result : dict
        A JSON-like structure with the content of the 
        API's response.
    """
    
    # Junta os pedaços para formar a URL:
    and_token = '?' if query.find('?') == -1 else '&'
    url = api_url + query + and_token + 'access_token=' + token

    # Requisita dados da API:
    response = requests.get(url)
    if verbose is True:
        print('Status: {}'.format(response.status_code))
    result = json.loads(response.text)
    
    return result