from astropy.io import fits
from astropy.stats import mad_std
from photutils.detection import DAOStarFinder
import matplotlib.pyplot as plt
from astropy.visualization import ZScaleInterval, LogStretch, ImageNormalize


# 🔍 Kép betöltése
hdul = fits.open('MAST_2025-09-06T20_06_58.826Z/HST/U2782D04T/u2782d04t_drz.fits')
image_data = hdul['SCI'].data
hdul.close()

# 📈 Háttér zaj becslése
bkg_sigma = mad_std(image_data)

# 🌟 Csillagdetektálás
daofind = DAOStarFinder(fwhm=2.0, threshold=2.5*bkg_sigma)
sources = daofind(image_data)

# 📋 Eredmények
print(sources)  # első 5 detektált csillag

# 🔧 Automatikus kontraszt beállítás (mint DS9)
interval = ZScaleInterval()
vmin, vmax = interval.get_limits(image_data)

# 🔍 Logaritmikus skála + normalizálás
norm = ImageNormalize(vmin=vmin, vmax=vmax, stretch=LogStretch())

# 🖼️ Vizualizáció
plt.figure(figsize=(10, 10))
plt.imshow(image_data, cmap='grey', origin='lower', norm=norm)
plt.scatter(sources['xcentroid'], sources['ycentroid'], s=30, edgecolor='red', facecolor='none')
plt.title("Detektált csillagok (log skála + zscale)")
plt.show()
