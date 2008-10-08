var bC_google_api = {
  api_url: 'http://maps.google.com/maps?file=api&amp;v=2&amp;key=',

  api_keys: {
    'tripplanner.bycycle.org': 'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhQ8y5tnWrQRsyOlME1eHkOS3wQveBSeFCpOUAfP10H6ec-HcFWPgiJOCA',

    'satellite.bycycle.org:5000':
'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhRY_I4CLwGh95qVWYjrRjsuZNzP3BSOxRXLsVSuuatyFhv0hQfFohQxBQ',

    'prototype.bycycle.org': 'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhTPU6PNPDk7LC31EIff_k4JZWpNmBQshai4v8RM5FaT-4FRWeyJA4VHaQ',

    'bycycle.metro-region.org':
'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhR7upyhxOh7UQa5Yu3ebGZe2uQ8SxRPJtyMUYYgIBQsAROpcOySx6G1RQ',

    'dev.bycycle.org': 'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhQSskL_eAzZotWlegWekqLPLda0sxQZNf0_IshFell3z8qP8s0Car117A',

    'dev.bycycle.org:5000': 'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhTkxokDJkt52pLJLqHCpDW3lL7iXBTREVLn9gCRhMUesO754WIidhTq2g',

    'www.bycycle.org': 'ABQIAAAAd_4WmZlgvQzchd_BQM0MPhR8QNZ8KuqqtskDzJsLddnT1fGweRTgDdVI-oPLr79jrZgA_-87uWVc5w',

    'bycycle.org': 'ABQIAAAAupb-OM5MU-8ZDqS4tVNkBBRa1vtdiGjU4Osv1KyKd6Mlr4BuWxQrO1eNXOimVbjcfI1DiLeH-XnIuw'
  },

  getAPIKey: function (domain) {
    domain = 'dev.bycycle.org:5000';
    var api_key = bC_google_api.api_keys[domain];
    if (api_key) {
      return bC_google_api.api_url + api_key;
    } else {
      return null;
    }
  }
};