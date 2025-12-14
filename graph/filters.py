# Filtre pour récupérer uniquement les chemins de fer (rails)
RAIL_FILTER = '["railway"~"rail"]'

# Filtre pour récupérer rails, tramways et métros
RAIL_TRAM_SUBWAY_FILTER = '["railway"~"rail|tram|subway"]'

# Filtre pour récupérer uniquement les routes pour voiture (network_type "drive")
ROAD_FILTER = '["highway"]'

# Exemple : si tu veux limiter à certaines vitesses ou types
ROAD_HIGHWAY_FILTER = '["highway"~"motorway|trunk|primary|secondary"]'
