export const BRAND_COLORS = {
  primary:'#1f78b4',
  secondary:'#a6cee3',
  tertiary:'#b2df8a',
  quaternary:'#33a02c',
}


export const COLORS = {
    MODELLED: '#1f78b4',
    REVEAL: '#a6cee3',
    ALLTRAILS: '#b2df8a',
    WTA: '#33a02c',
    TWITTER: '#c95275',
    INSTA: '#d34636',
    FLICKR: '#7c4034',
    GRAVY: '#c8833d',
    EBIRD: '#cdb295',
    ON_SITE: '#ccc242',
    COMPARE_MODELLED: '#566a32',
    COMPARE_REVEAL: '#85e54c',
    COMPARE_ALLTRAILS: '#6dcfab',
    COMPARE_WTA: '#567977',
    COMPARE_TWITTER: '#6959c4',
    COMPARE_INSTA: '#8633d6',
    COMPARE_FLICKR: '#552c66',
    COMPARE_GRAVY: '#bb8ec0',
    COMPARE_EBIRD: '#342c32',
    COMPARE_ON_SITE: '#ce4db8',
};

export const YEAR_COLORS = {
  2018: '#a6cee3',
  2019: '#1f78b4',
  2020: '#b2df8a',
  2021: '#33a02c',
  2022: '#fb9a99',
  2023: '#e31a1c',
  2024: '#fdbf6f',
  Total: '#b15928'
};

export const MAPBOX_CONSTS = {
  TOKEN: 'pk.eyJ1Ijoid29vZHNwIiwiYSI6ImNrMjEwY3oycTFlcnEzbXFvbzR4bmNqNjgifQ.pM7-As9W2Ce9xXMv3W-NNg',
  OUTDOOR_STYLE_TOKEN: 'pk.eyJ1Ijoid29vZHNwIiwiYSI6ImNrMjEwYjFyaDB2MHMzaW1mbWM0azVnbTMifQ.LE_loUCO3HjjZfyEayX5Sg',
  TILES_API: 'https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}',
  ATTRIBUTION: '© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> © ' +
    '<a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
};

export const VIZ_MODES = {
  PROJECT: 'project',
  SITE: 'site',
  COMPARE: 'compare',
};

// ensure values maintain space seperated format: ['{source} {year range}']
export const DATA_SOURCES = {
  'West Cascades': ['Chatbot (2018 - 2024)', 'Flickr (2005 - 2019)'],
  'Middle Fork': ['Chatbot (2018 - 2024)', 'Flickr (2005 - 2019)'],
  // 'Okanogan-Wenatchee Wilderness (Archived)': [],
  // 'Okanogan-Wenatchee General Forest (Archived)': [],
  'Northern New Mexico': ['Flickr (2005 - 2019)'],
  'King County Parks': ['Chatbot (2023 - 2024)', 'Reveal (2021 - 2024)'],
  'US National Forests': [], //should not show Visitor Characteristics
  'Mount Baker-Snoqualmie Wilderness': ['Chatbot (2018 - 2024)'], // no Flickr data
  'Mountain Loop': ['Chatbot (2018 - 2024)', 'Flickr (2005 - 2019)'],
  'South Mountain Loop': ['Chatbot (2018 - 2024)', 'Flickr (2005 - 2019)'],
  // 'Mount Baker-Snoqualmie General Forest': [],
  'East Cascades': ['Chatbot (2020 - 2024)'], // no Flickr data
  'Coronado': ['Chatbot (2022 - 2024)'],
  'Bridger-Teton': [] //should not show Visitor Characteristics
}
