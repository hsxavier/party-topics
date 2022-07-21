#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 14:28:33 2022

@author: skems

Functions used by this app, specifically.
"""

import graph_api as fb
import pandas as pd
import matplotlib.pyplot as pl
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer
from matplotlib import cm


def list_pages_in_category(token, category=None, fields=['id', 'access_token', 'about']):
    """
    Return the IDs and access tokens (if 
    requested) for my pages in the specified
    category (if any).
    
    Parameters
    ----------
    token : str
        User access token for the user owner
        of the desired pages.
    category : str or None
        The page category (e.g. 'Político')
        or None for no filtering (return 
        all my pages).
    fields : list of str
        Fields of information in each 
        page to gather from.
    
    Returns
    -------
    ids : list of str
        IDs of the selected pages.
    tokens : list of str
        Page access tokens of the 
        selection, if `return_token` is True.
    """
    
    # Make sure category is in fields:
    fields = fields + ['category'] if 'category' not in fields else fields
    # Join fields for the request:
    fields_str = ','.join(fields)
    
    # Lista páginas associadas ao meu usuário: 
    result = fb.query_graph('me/accounts?fields={:}'.format(fields_str), token)
    
    # Select pages in category:
    if category is not None:
        result = list(filter(lambda d: d['category'] == category, result['data']))

    # Split data from different fields into different lists:
    togo = tuple([d[f] for d in result] for f in fields if f != 'category')
    
    # Return data:
    if len(togo) == 1:
        return togo[0]
    else:
        return togo
        

def get_feed_data(page_id, page_token, fields=['message']):
    """
    Extract the requested information from 
    a page's feed.
    
    Parameters
    ----------
    page_id : str
        The ID of a page, e.g.:
        '102358565898903'.
    page_token : str
        The specified page's access token.
    fields : list of str
        Fields of information in each 
        post of the page's feed to gather 
        from.
    
    Returns
    -------
    togo : list or tuple of lists
        If only one field is specified in
        `fields`, return a list of the 
        information in that field, one per 
        post. If more that one field is 
        specified, return one list per field.
    """
    
    # Join fields for the request:
    fields_str = ','.join(fields)
    # Get data from page:
    result = fb.query_graph('{:}/feed?fields={:}'.format(page_id, fields_str), page_token)
    
    # Split data from different fields into different lists:
    togo = tuple([d[f] for d in result['data']] for f in fields)
    
    if len(togo) == 1:
        return togo[0]
    else:
        return togo


def request_pages_posts(token):
    """
    Get pages associated to user and build
    a DataFrame with all the posts from 
    these pages.
    """
    
    # Build database of pages:
    page_ids, page_tokens, page_abouts = list_pages_in_category(token, 'Político')
    pages_df = pd.DataFrame({'id': page_ids, 'token': page_tokens, 'about': page_abouts})
    pages_df['party'] = pages_df['about'].str.extract('(Party [A-Z])')[0]
    
    # Request the posts from all pages:
    page_posts = [get_feed_data(i, t) for i, t in zip(page_ids, page_tokens)]
    all_posts  = pd.concat([pd.Series(p, index=[i] * len(p), name='posts') for i, p in zip(page_ids, page_posts)])
    
    # Join page's info to posts:
    posts_df = pages_df.join(all_posts, on='id').reset_index(drop=True)
    
    return posts_df


def count_words_in_posts(posts_df, nuisance_words):
    """
    Add columns to posts DataFrame that records
    the number of times each word in mentioned 
    in each post.
    """
    
    # Hard-coded:
    stop_words = ['de', 'a', 'o', 'que', 'e', 'é', 'do', 'da', 'em', 'um', 'para', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'ao', 
              'ele', 'das', 'à', 'seu', 'sua', 'ou', 'quando', 'muito', 'nos', 'já', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'depois', 'sem', 
              'mesmo', 'aos', 'seus', 'quem', 'nas', 'me', 'esse', 'eles', 'você', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha', 'numa', 'pelos', 'elas', 'qual', 'nós', 
              'lhe', 'deles', 'essas', 'esses', 'pelas', 'este', 'dele', 'tu', 'te', 'vocês', 'vos', 'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 
              'nossos', 'nossas', 'dela', 'delas', 'esta', 'estes', 'estas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'aquilo', 'estou', 'está', 'estamos', 'estão', 
              'estive', 'esteve', 'estivemos', 'estiveram', 'estava', 'estávamos', 'estavam', 'estivera', 'estivéramos', 'esteja', 'estejamos', 'estejam', 'estivesse', 
              'estivéssemos', 'estivessem', 'estiver', 'estivermos', 'estiverem', 'hei', 'há', 'havemos', 'hão', 'houve', 'houvemos', 'houveram', 'houvera', 'houvéramos', 
              'haja', 'hajamos', 'hajam', 'houvesse', 'houvéssemos', 'houvessem', 'houver', 'houvermos', 'houverem', 'houverei', 'houverá', 'houveremos', 'houverão', 'houveria', 
              'houveríamos', 'houveriam', 'sou', 'somos', 'são', 'era', 'éramos', 'eram', 'fui', 'foi', 'fomos', 'foram', 'fora', 'fôramos', 'seja', 'sejamos', 'sejam', 'fosse', 
              'fôssemos', 'fossem', 'for', 'formos', 'forem', 'serei', 'será', 'seremos', 'serão', 'seria', 'seríamos', 'seriam', 'tenho', 'tem', 'temos', 'tém', 'tinha', 
              'tínhamos', 'tinham', 'tive', 'teve', 'tivemos', 'tiveram', 'tivera', 'tivéramos', 'tenha', 'tenhamos', 'tenham', 'tivesse', 'tivéssemos', 'tivessem', 'tiver', 
              'tivermos', 'tiverem', 'terei', 'terá', 'teremos', 'terão', 'teria', 'teríamos', 'teriam']
    
    # Count word occurences:
    vectorizer = CountVectorizer(stop_words=stop_words + nuisance_words, min_df=2, ngram_range=(1,2))
    vectorizer.fit(posts_df['posts'])
    word_tokens = vectorizer.get_feature_names()
    counts_df = pd.DataFrame(vectorizer.transform(posts_df['posts']).toarray(), columns=word_tokens, index=posts_df.index)
    
    # Aggregate per party:
    posts_counts_df = posts_df.join(counts_df)
    
    return posts_counts_df, word_tokens
 

def aggregate_by_party(posts_counts_df, word_cols):
    """
    Aggregate word counts by party and compute 
    the fraction of each word count in the 
    total party count.
    
    Parameters
    ----------
    posts_counts_df : DataFrame
        Table with the counts for each word 
        (column) and for each post (row),
        with another column specifying the 
        party responsible for the post.
    word_cols : list of str
        The names of columns refering to 
        word counts (i.e. the words that 
        are being counted).
    
    Returns
    -------
    party_freq_df : DataFrame
        The fraction of each word count
        in the party's total word count.
    """
    
    party_counts_df = posts_counts_df.groupby('party')[word_cols].sum().transpose()
    party_freq_df   = party_counts_df / party_counts_df.sum()
    
    return party_freq_df


def plot_party_emphasis(party_freq_df):
    
    #sorting_col  = party_freq_df.sum(axis=1)
    sorting_col  = party_freq_df['Party A'] - party_freq_df['Party B']
    sorted_words = sorting_col.sort_values().index
    
    fig = pl.figure()
    
    cmap = cm.get_cmap('tab10')
    for i, p in enumerate(party_freq_df.columns):
        party_freq_df.loc[sorted_words, p].plot(kind='barh', alpha=0.7, color=cmap(i), label=p)
    
    ax = pl.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_color('dimgray')
    pl.grid(axis='x', color='gray', alpha=0.5)
    pl.legend()
    pl.xlabel('Emphasis on the word')
    pl.tick_params(bottom=False, left=False)
    
    return fig