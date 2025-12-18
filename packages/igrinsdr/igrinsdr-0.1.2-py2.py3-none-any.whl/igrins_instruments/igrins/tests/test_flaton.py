import astrodata
import igrins_instruments

ad = astrodata.open("test_data/sample_flaton/N20251106S0434_H.fits")
print(ad.tags)
print(ad.observation_type())
print(ad.descriptors)
print(ad.exposure_time())

