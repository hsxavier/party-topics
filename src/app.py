#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Thu Jul 21 14:19:05 2022

@author: skems
"""

import streamlit as st
from datetime import datetime

import graph_api as fb
import backend as bk
import htmlhacks as hh

# Carrega CSS:
hh.localCSS("style.css")


#st.image('http://henriquexavier.net/images/fantasmas_pic.jpg')

#st.markdown('# Party topics')
#st.markdown('#### What are the candidates for the Brazilian House of Representatives talking about on the 2022 elections?')

#hh.html('<hr/>')

# Load token:
#user_token = fb.load_token_from_file('/home/skems/ceweb/config/keys/facebook_graph_api_user_access_token_upto_2022-09-18.txt')
user_token = fb.load_token_from_env()

# Get facebook data and aggregate word counts by party:
ignore_words = ['vamos', 'precisamos', 'enquanto', 'hoje', 'amigos']
counts_df, vocab = bk.count_words_in_posts(bk.request_pages_posts(user_token), ignore_words)
last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
party_freq_df = bk.aggregate_by_party(counts_df, vocab)

# Plot:
update_html = '<p style="color:#717171; text-align:right">Last update: ' + last_update + ' (UTC)</p>'
hh.html(update_html)
#st.markdown('Words most used by candidates of each party')
emphasis_plot = bk.plot_party_emphasis(party_freq_df)
st.pyplot(emphasis_plot)

#hh.html('<hr/>')

# Info:
info = """#### How is this measured?

1. We monitor all the candidates' public pages on [Facebook](https://www.facebook.com) and gather their posts;
2. We count how many times each word was used, ignoring both rare words and commonly used words that are not related to topics of interest (e.g. stopwords);
3. These counts are aggregated by party, and we finally compute the frequency of each word in each party's speech. 

**Notes**

* This is a way to compare the policies and topics of interest of various Brazilian political parties.
* Only **aggregated** and **anonymized** data is presented.
"""
#st.markdown(info)

# Disclaimer:
disclaimer = """#### Disclaimer for Facebook reviewers

* This app will only achieve its goals if the [Page Public Content Access](https://developers.facebook.com/docs/features-reference/page-public-content-access) feature is authorized, because we need access to the candidates' public pages;
* Current app permissions only allow access to Public Pages owned by the app's developer. Thus, we used the four mock pages below as candidates' pages:
    * [Candidate 1](https://www.facebook.com/Candidate-1-111426894976704), from Party A;
    * [Candidate 2](https://www.facebook.com/Candidate-2-100281926113114), from Party A;
    * [Candidate 3](https://www.facebook.com/Candidate-3-102358565898903), from Party B; 
    * [Candidate 4](https://www.facebook.com/Candidate-4-109748375146739), from Party B.
* This app will only be used on this website. There are no other uses to it.

"""
#st.markdown(disclaimer)

#hh.html('<hr/>')

footnote = '<p style="color:#717171; text-align:right">App developed by <a href="https://henriquexavier.net">Henrique Xavier</a>.</p>'
#hh.html(footnote)
