from astroquery.mast import Observations

obs_table = Observations.query_criteria(
    objectname="NGC4414",
    obs_collection="HST",
    instrument_name="WFPC2",
    dataproduct_type="image"
)



wfpc2_obs = obs_table[
    (obs_table['instrument_name'] == 'WFPC2') &
    (obs_table['distance'] < 0.01)
]

products = Observations.get_product_list(wfpc2_obs)


filtered = products[[fn.endswith('c0f.fits') for fn in products['productFilename']]]


manifest = Observations.download_products(filtered, download_dir="ngc4414_fits")