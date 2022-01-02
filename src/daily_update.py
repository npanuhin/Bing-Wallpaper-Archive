from peapix import updateRegions, FLAG_LATEST

updateRegions(
    # ["AU", "CA", "CN", "DE", "FR", "IN", "JP", "ES", "GB", "US"],
    ["US"],
    days_action=FLAG_LATEST,
    api_action=FLAG_LATEST,
    image_action=FLAG_LATEST
)
