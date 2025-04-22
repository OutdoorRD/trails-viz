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
    TWITTER: '#fb9a99',
    INSTA: '#e31a1c',
    FLICKR: '#fdbf6f',
    GRAVY: '#ff7f00',
    EBIRD: '#cab2d6',
    ON_SITE: '#6a3d9a',
    COMPARE_MODELLED: '#419fde',
    COMPARE_REVEAL: '#e0eef5',
    COMPARE_ALLTRAILS: '#daefc6',
    COMPARE_WTA: '#53ce4b',
    COMPARE_TWITTER: '#fee3e3',
    COMPARE_INSTA: '#ec5d5e',
    COMPARE_FLICKR: '#fee1ba',
    COMPARE_GRAVY: '#ffa54d',
    COMPARE_EBIRD: '#ece4f1',
    COMPARE_ON_SITE: '#9062c1',
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
