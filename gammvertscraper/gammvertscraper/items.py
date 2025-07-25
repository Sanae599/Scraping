import scrapy

class CategoryItem(scrapy.Item):
    """
    Représente une catégorie de produits extraite du site.

    Attributs :
        name (scrapy.Field) : Nom de la catégorie.
        url (scrapy.Field) : URL vers la page de la catégorie.
        category_id (scrapy.Field) : Identifiant unique de la catégorie.
        parent_id (scrapy.Field) : Identifiant de la catégorie parente (s'il y en a une).
        is_pagelist (scrapy.Field) : Booléen indiquant si la catégorie contient une liste paginée de produits.
    """
    name = scrapy.Field()
    url = scrapy.Field()
    category_id = scrapy.Field()
    parent_id = scrapy.Field()
    is_pagelist = scrapy.Field()


class ProductItem(scrapy.Item):
    """
    Représente un produit extrait du site.

    Attributs :
        product_id (scrapy.Field) : Identifiant unique du produit.
        name (scrapy.Field) : Nom du produit.
        url (scrapy.Field) : URL vers la fiche produit.
        category_id (scrapy.Field) : Identifiant de la catégorie parente (référence à CategoryItem).
        price (scrapy.Field) : Prix affiché (peut inclure réduction).
        price_init (scrapy.Field) : Prix initial avant réduction.
        price_reduc (scrapy.Field) : Montant ou pourcentage de la réduction.
        price_final (scrapy.Field) : Prix final calculé après réduction.
        categories (scrapy.Field) : Liste des catégories auxquelles le produit appartient.
        currency (scrapy.Field) : Devise utilisée pour les prix.
        availability (scrapy.Field) : Disponibilité du produit (en stock, épuisé...).
        stock_qty (scrapy.Field) : Quantité disponible en stock.
        pickup_available (scrapy.Field) : Booléen indiquant si le retrait en magasin est possible.
        shipping_cost (scrapy.Field) : Coût de la livraison.
        shipping_volume (scrapy.Field) : Dimensions ou volume utilisé pour l’expédition.
        brand (scrapy.Field) : Marque du produit.
        description (scrapy.Field) : Description textuelle du produit.
        rating (scrapy.Field) : Note moyenne donnée par les utilisateurs.
        num_reviews (scrapy.Field) : Nombre d’avis clients.
        page_number (scrapy.Field) : Numéro de page d’où le produit a été extrait (utile pour le debug).
    """
    product_id      = scrapy.Field()
    name            = scrapy.Field()
    url             = scrapy.Field()
    category_id     = scrapy.Field()
    price           = scrapy.Field()
    price_init      = scrapy.Field()
    price_reduc     = scrapy.Field()
    price_final     = scrapy.Field()
    categories      = scrapy.Field()
    currency        = scrapy.Field()
    availability    = scrapy.Field()
    stock_qty       = scrapy.Field()
    pickup_available= scrapy.Field()
    shipping_cost   = scrapy.Field()
    shipping_volume = scrapy.Field()
    brand           = scrapy.Field()
    description     = scrapy.Field()
    rating          = scrapy.Field()
    num_reviews     = scrapy.Field()
    page_number     = scrapy.Field()
