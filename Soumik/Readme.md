# Flow

## Criteria
- Check photon count > 3000
- Check if visual peaks are present
- Check if not in geotail
- Assign solar flare status if present

# Combine
- Combine all first fits files of a given latitude longitude
- Generate 4,00,000 points uniformly on the surface of moon
- Combine fits files using weighted_average for a specific point
    - for the fits file check if visual peaks are present
- Apply corrective factor due to sun's intensity to boost mg's ratios