# The freezer: edit this file to change flavors, prices or what is sold out.
#
# category   gelato (milk based) | sorbet (dairy free) | toppers
# sweetness  1 (barely sweet) to 5 (very sweet)
# tags       used by the offline Flavor Lab to match moods to flavors
# color      the flavor's color, used for the scoops on the website

menu_items = [
    # ---------- Gelato ----------
    {"id": 1, "name": "Madagascar Vanilla Bean", "category": "gelato", "price": 90.0,
     "description": "Vanilla pods steeped in fresh milk. Plain on purpose, and the one that makes the others taste better.",
     "available": True, "color": "#f3e0a8", "vegan": False, "sweetness": 3, "tags": ["creamy", "indulgent"]},
    {"id": 2, "name": "Filter Coffee", "category": "gelato", "price": 100.0,
     "description": "South Indian decoction with a little chicory, bitter at the edges the way it should be.",
     "available": True, "color": "#8a5a3c", "vegan": False, "sweetness": 2, "tags": ["coffee", "creamy"]},
    {"id": 3, "name": "Jaggery Caramel", "category": "gelato", "price": 100.0,
     "description": "Dark palm jaggery cooked down slowly, finished with a pinch of sea salt.",
     "available": True, "color": "#c8803a", "vegan": False, "sweetness": 4, "tags": ["caramel", "indulgent"]},
    {"id": 4, "name": "Dark Chocolate Sea Salt", "category": "gelato", "price": 110.0,
     "description": "70% cocoa and flaked salt. Not shy about the bitterness.",
     "available": True, "color": "#4a2a22", "vegan": False, "sweetness": 2, "tags": ["chocolate", "indulgent"]},
    {"id": 5, "name": "Kesar Pista", "category": "gelato", "price": 120.0,
     "description": "Saffron steeped overnight in warm milk, with roasted pistachio folded through.",
     "available": True, "color": "#e8c24a", "vegan": False, "sweetness": 3, "tags": ["nutty", "floral", "indulgent"]},
    {"id": 6, "name": "Rose Cardamom", "category": "gelato", "price": 110.0,
     "description": "Damask rose and green cardamom. Smells like a wedding.",
     "available": True, "color": "#f29bb5", "vegan": False, "sweetness": 3, "tags": ["floral", "spiced"]},
    {"id": 7, "name": "Thandai", "category": "gelato", "price": 110.0,
     "description": "Almond, fennel, black pepper and rose, the Holi drink turned into gelato.",
     "available": True, "color": "#e3c7a1", "vegan": False, "sweetness": 3, "tags": ["spiced", "nutty", "floral"]},
    {"id": 8, "name": "Paan", "category": "gelato", "price": 100.0,
     "description": "Betel leaf, gulkand and fennel. Tastes like the end of a good dinner.",
     "available": False, "color": "#5f9a4d", "vegan": False, "sweetness": 3, "tags": ["herbal", "floral", "refreshing"]},
    {"id": 9, "name": "Chikoo Malai", "category": "gelato", "price": 100.0,
     "description": "Ripe chikoo blended into malai. A milkshake that grew up.",
     "available": True, "color": "#c9a27a", "vegan": False, "sweetness": 4, "tags": ["creamy", "caramel"]},

    # ---------- Sorbet (dairy free) ----------
    {"id": 10, "name": "Alphonso Mango", "category": "sorbet", "price": 100.0,
     "description": "Ratnagiri Alphonso pulp with a squeeze of lime. Seasonal: when it is gone, it is gone.",
     "available": True, "color": "#ffb627", "vegan": True, "sweetness": 4, "tags": ["fruity", "refreshing"]},
    {"id": 11, "name": "Guava Chilli", "category": "sorbet", "price": 90.0,
     "description": "Pink guava with a pinch of chilli salt. The roadside cart, in a cup.",
     "available": True, "color": "#ef6f6c", "vegan": True, "sweetness": 3, "tags": ["fruity", "tangy", "spiced"]},
    {"id": 12, "name": "Black Jamun", "category": "sorbet", "price": 90.0,
     "description": "Deep purple, tart and a little astringent. It will stain your tongue.",
     "available": True, "color": "#5a2d6e", "vegan": True, "sweetness": 2, "tags": ["fruity", "tangy"]},
    {"id": 13, "name": "Tender Coconut", "category": "sorbet", "price": 90.0,
     "description": "Coconut water and soft malai, cool and quiet.",
     "available": True, "color": "#e3f0df", "vegan": True, "sweetness": 2, "tags": ["refreshing", "creamy"]},
    {"id": 14, "name": "Kokum Cooler", "category": "sorbet", "price": 90.0,
     "description": "Konkan kokum with roasted cumin, the summer drink frozen solid.",
     "available": True, "color": "#b8325f", "vegan": True, "sweetness": 2, "tags": ["tangy", "refreshing", "spiced"]},

    # ---------- Toppers ----------
    {"id": 15, "name": "Salted Caramel Drizzle", "category": "toppers", "price": 20.0,
     "description": "Warm jaggery caramel, poured at the counter.",
     "available": True, "color": "#d28a2f", "vegan": False, "sweetness": 4, "tags": ["caramel", "indulgent"]},
    {"id": 16, "name": "Crushed Pistachio", "category": "toppers", "price": 25.0,
     "description": "Roasted and chopped by hand each morning.",
     "available": True, "color": "#8fbf5f", "vegan": True, "sweetness": 1, "tags": ["nutty", "crunchy"]},
    {"id": 17, "name": "Rose Petals", "category": "toppers", "price": 15.0,
     "description": "Dried damask petals, mostly for looks and a little for scent.",
     "available": True, "color": "#e86a92", "vegan": True, "sweetness": 1, "tags": ["floral"]},
    {"id": 18, "name": "Waffle Crumble", "category": "toppers", "price": 20.0,
     "description": "Broken pieces of our butter waffle cones.",
     "available": True, "color": "#d9a85b", "vegan": False, "sweetness": 3, "tags": ["crunchy", "caramel"]},
]
