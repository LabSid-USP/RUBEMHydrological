# TODO: Reorganize information in dictionaries
mapSeriesDictFileNames = {
    "Runoff [m³/s]": "rnf",
    "Interception [mm]": "itp",
    "Baseflow [mm]": "bfw",
    "Surface Runoff [mm]": "srn",
    "ETa [mm]": "eta",
    "Lateral Flow [mm]": "lfw",
    "Recharge [mm]": "rec",
    "Soil Moisture Content [mm]": "smc",
}

# TODO: Reorganize information in dictionaries
timeSeriesDictFileNames = {
    "Runoff [m³/s]": "tss_rnf",
    "Interception [mm]": "tss_itp",
    "Baseflow [mm]": "tss_bfw",
    "Surface Runoff [mm]": "tss_srn",
    "ETa [mm]": "tss_eta",
    "Lateral Flow [mm]": "tss_lfw",
    "Recharge [mm]": "tss_rec",
    "Soil Moisture Content [mm]": "tss_smc",
}

# TODO: Reorganize information in dictionaries. Preferably use this format.
# ? Should this dictionary be here or in another specific location?
timeSeriesDict = {
    "tss_rnf": {
        "plot": {
            "title": "Total Runoff",
            "x_label": "Time Steps [month]",
            "y_label": "Value [m³/s]",
        },
    },
    "tss_itp": {
        "plot": {
            "title": "Interception",
            "x_label": "Time Steps [month]",
            "y_label": "Value [mm]",
        },
    },
    "tss_bfw": {
        "plot": {
            "title": "Baseflow",
            "x_label": "Time Steps [month]",
            "y_label": "Value [mm]",
        },
    },
    "tss_srn": {
        "plot": {
            "title": "Surface Runoff",
            "x_label": "Time Steps [month]",
            "y_label": "Value [mm]",
        },
    },
    "tss_eta": {
        "plot": {
            "title": "Actual Evapotranspiration",
            "x_label": "Time Steps [month]",
            "y_label": "Value [mm]",
        },
    },
    "tss_lfw": {
        "plot": {
            "title": "Lateral Flow",
            "x_label": "Time Steps [month]",
            "y_label": "Value [mm]",
        },
    },
    "tss_rec": {
        "plot": {
            "title": "Recharge",
            "x_label": "Time Steps [month]",
            "y_label": "Value [mm]",
        },
    },
    "tss_smc": {
        "plot": {
            "title": "Soil Moisture Content",
            "x_label": "Time Steps [month]",
            "y_label": "Value [mm]",
        },
    },
}
