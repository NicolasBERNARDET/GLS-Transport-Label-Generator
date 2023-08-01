get_credentials_query = """
                        SELECT Texte1 as SHIPPERID, ClientCompte as USERNAME, ClientMotDePasse as PASSWORD 
                        FROM TRANSPORT_PRODUIT 
                        WHERE KeyEtiquette = 'GLS' AND CodeProduitTransporteur = 'BP'
"""