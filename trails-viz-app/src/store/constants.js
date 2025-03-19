export const COLORS = {
  MODELLED: '#1c3dc8',
    FLICKR: '#d8021f',
    INSTA: '#9620e5',
    TWITTER: '#2b7782',
    WTA: '#0ab652',
    ALLTRAILS: '#36E0BE',
    EBIRD: '#f2e718',
    GRAVY: '#ffa500',
    REVEAL: '#ffa500',
    ON_SITE: '#640b00',
    COMPARE_MODELLED: '#fb9205',
    COMPARE_FLICKR: '#c9c9c4',
    COMPARE_INSTA: '#f90dc3',
    COMPARE_TWITTER: '#12fbf2',
    COMPARE_WTA: '#ff0000',
    COMPARE_ALLTRAILS: '#086351',
    COMPARE_EBIRD: '#e3e84a',
    COMPARE_GRAVY: '#8a2be2',
    COMPARE_REVEAL: '#8a2be2',
    COMPARE_ON_SITE: '#ff6400',
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
  'US National Forests': ['Chatbot (2018 - 2024)', 'Flickr (2005 - 2019)'],
  'Mount Baker-Snoqualmie Wilderness': ['Chatbot (2018 - 2024)', 'Flickr (2005 - 2019)'],
  'Mountain Loop': ['Chatbot (2018 - 2024)', 'Flickr (2005 - 2019)'],
  'South Mountain Loop': ['Chatbot (2018 - 2024)', 'Flickr (2005 - 2019)'],
  // 'Mount Baker-Snoqualmie General Forest': [],
  'East Cascades': ['Chatbot (2020 - 2024)', 'Flickr (2005 - 2019)'],
  'Coronado': ['Chatbot (2022 - 2024)', 'Flickr (2005 - 2019)'],
  'Bridger-Teton': [] //should not show Visitor Characteristics
}


trails-viz-app/src/store/constants.js