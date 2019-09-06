from flask import Flask, request, send_from_directory, jsonify, url_for, render_template
import os
import json
import csv
import pandas as pd
import geopandas as gpd
import numpy as np
from trails_site import app

# homepage
@app.route('/')
def get_page():
    return render_template('index.html')

project_data = {
    "polygon_uri": "/home/woodsp/mbs-trails/gis/allsites.shp",
    "geojson_lines_uri": "/home/woodsp/mbs-trails/gis/allsites_lines.geojson",
    "project_codes": ['MBS_PIL', 'MBS_SARL', 'MBS_PIL, MBS_SARL'],
    "monthly_estimates": "/home/woodsp/mbs-trails/3_analyze/viz_model_mmm.csv",
    "monthly_onsite": "/home/woodsp/mbs-trails/3_analyze/viz_model_mmmir.csv",
    "weekly_estimates": "/home/woodsp/mbs-trails/3_analyze/viz_model_www.csv",
    "weekly_onsite": "/home/woodsp/mbs-trails/3_analyze/viz_model_wwwir.csv"}

## get project site metadata (names and siteids)
allsites = gpd.read_file(project_data['polygon_uri'])
PROJECT_SITES = allsites.loc[allsites['Prjct_code'].isin(project_data['project_codes']),
                             ['Trail_name', 'siteid']]

def create_monthlies():
    #load monthly
    month_estimate = pd.read_csv(project_data['monthly_estimates'])
    month_onsite = pd.read_csv(project_data['monthly_onsite'])

    idvars = ["trail", "d2p"]
    ## are these social media data estimates or the original predictors?
    estimates = ["jjmm", "flickr", "twitter", "instag", "wta"]
    response = ["resp.ss"]
    out_fieldnames = ["siteid", "date", "estimate", "onsite", "flickr", "twitter", "instag", "wta"]

    ## join estimates and response to a single table
    month_estimate = month_estimate[idvars + estimates]
    month_onsite = month_onsite[idvars + response]
    monthly = pd.merge(month_estimate, month_onsite, on=idvars, how='left')

    ## reformat date
    monthly[['year','month', 'day']] = monthly['d2p'].str.split('-',expand=True)
    monthly['date'] = monthly['year'] + '-' + monthly['month']
    monthly.drop(labels='d2p', axis=1, inplace=True)

    ## select only project sites
    monthly = monthly.loc[monthly['trail'].isin(PROJECT_SITES['siteid'])]
    monthly = pd.merge(monthly, PROJECT_SITES, left_on='trail', right_on='siteid', how='left')

    ## rename and drop some columns:
    monthly.drop(labels='trail', axis=1, inplace=True)
    monthly.rename(columns={'jjmm':'estimate', 'resp.ss':'onsite'}, inplace=True)

    ### DIVIDE by 2 - since we never did that for IR counts
    ## also limit precision in predicted vals
    monthly['estimate'] = (monthly['estimate']/2).round(2)
    monthly['onsite'] = (monthly['onsite']/2).round(2)

    # temp selecting and renaming of cols to test against existing app
    # monthly = monthly[['siteid', 'date', 'estimate', 'onsite', 'Trail_name', 'year', 'month']]
    # monthly.rename(columns={'siteid':'AllTRLs_ID', 'estimate':'predicted', 'onsite':'actual'}, inplace=True)
    # monthly.to_csv('static/data/hikers_monthly.csv', index=False, na_rep='NA')

    monthly = monthly[['siteid', 'date', 'estimate', 'onsite', 'Trail_name', 'year', 'month', 'flickr', 'twitter', 'instag', 'wta']]
    jsonstring = monthly.to_json(orient='records') # to_json converts NaNs and Nones to null
    jsonstring = jsonstring.replace('null', '"NaN"') # but bad idea to pass null to js, since null converted to numeric == 0
    return jsonstring

monthlies = create_monthlies()

# geojson API endpoint
@app.route('/api/geojson')
def get_geojson():
    # with open(os.getcwd() + '/static/data/trails.geojson') as f:
    #     d = json.load(f)
    # return jsonify(d)

    ####################################################################
    ### get geojson lines - join some data for symbolizing lines on map

    alllines = gpd.read_file(project_data['geojson_lines_uri'])
    alllines['siteid'] = pd.to_numeric(alllines['siteid'])
    alllines.drop(axis=1, labels='Notes', inplace=True)


    # select only project sites
    project_lines = alllines.loc[alllines['siteid'].isin(PROJECT_SITES['siteid'])]
    project_lines = pd.merge(project_lines, PROJECT_SITES, on='siteid', how='left')

    # get 2017 annual totals, so we have some data to join
    # note we're using the monthly data returned by create_monthlies()
    month = pd.read_json(monthlies)
    months2018 = month.loc[month['year'] == 2018]
    annual = months2018[['siteid', 'estimate']].groupby('siteid').sum()

    annual['annual'] = np.log(annual['estimate']+1)
    annual.drop(axis=1, labels='estimate', inplace=True)
    annual.reset_index(inplace=True)

    project_lines = pd.merge(project_lines, annual, how='left', on='siteid')

    return project_lines.to_json() # not sure if this gets you exactly the proper format you need


# monthly hiker data API endpoint
@app.route('/api/hikers_monthly')
def get_hikersmonthly():
    return monthlies

# annual average data API endpoint (requires an int representing the siteid)
@app.route('/api/annuals/<int:int>')
def get_annuals(int):

    month = pd.read_json(monthlies)
    site = month.loc[month['siteid'] == int]
    annual_totals = site.groupby('year')['estimate'].sum().round(0)
    annual_flickr = site.groupby('year')['flickr'].sum().round(0)
    annual_twitter = site.groupby('year')['twitter'].sum().round(0)
    annual_instag = site.groupby('year')['instag'].sum().round(0)
    annual_wta = site.groupby('year')['wta'].sum().round(0)
    total_years = site['year'].unique()
    annual_table = []
    for i in range(len(total_years)):
        dictionary = {
            'year': total_years[i],
            'avg_pred': annual_totals[total_years[i]],
            'flickr': annual_flickr[total_years[i]],
            'twitter': annual_twitter[total_years[i]],
            'instag': annual_instag[total_years[i]],
            'wta': annual_wta[total_years[i]]
        }
        annual_table.append(dictionary)

    return json.dumps(annual_table)

# monthly averages data API endpoint (requires an int representing the siteid)
@app.route('/api/monthlies/<int:int>')
def get_monthlies(int):
    month = pd.read_json(monthlies)
    site = month.loc[month['siteid'] == int]
    monthly_means = site.groupby('month')['estimate'].mean().round(0)
    monthly_flickr = site.groupby('month')['flickr'].mean().round(0)
    monthly_instag = site.groupby('month')['instag'].mean().round(0)
    monthly_twitter = site.groupby('month')['twitter'].mean().round(0)
    monthly_wta = site.groupby('month')['wta'].mean().round(0)

    monthly_table = []
    for i in range(12):
        dictionary = {
            'avg_pred': monthly_means[i + 1],
            'flickr': monthly_flickr[i + 1],
            'twitter': monthly_twitter[i + 1],
            'instag': monthly_instag[i + 1],
            'wta': monthly_wta[i + 1]
        }
        monthly_table.append(dictionary)

    return json.dumps(monthly_table)
