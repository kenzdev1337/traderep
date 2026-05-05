# TradeRep

Un bot Discord de réputation pour transactions entre utilisateurs

## Fonctionnalités

- Possibilité de laisser des avis aux membres
- Système de score en fonction des avis positifs/négatifs entre membres
- Liste des avis de chaque membre
- Informations sur la valeur de la transaction


## Installation

- Clonez le repo

```bash
  git clone https://github.com/kenzdev1337/traderep.git
```

- Nécessite l'installation du module `discord.py` et `python-mysql`, inclus dans `requirements.txt`

```bash
  pip install -r requirements.txt
```

- Remplissez le fichier .env.example et retirez son extension
- Lancez `main.py`

```bash
  python3 main.py
```

    
## Structure de la BDD

Le bot utilise deux base de données :

- Une BDD pour les avis des utilisateurs 
- Une BDD pour le profil des utilisateurs

BDD avis :

- Chaque utilisateur à sa propre table
- Aucune configuration nécessaire, les tables sont créées automatiquement, fournissez simplement les identifiants

BDD profil :

- Toutes les données sont stockées dans une table 
- Elle stocke l'ID utilisateur Discord (BIGINT), le socre (INT), la valeur d'échange maximale (INT) et le nombre d'avis (INT)
- Créez la table suivante :

```sql
CREATE TABLE reputation
(
    user_id BIGINT(20),
    score INT(11),
    max_value INT(11),
    review_count INT(11)
)
```


## Issues

N'hésitez pas a créer une [issue](https://github.com/kenzdev1337/traderep/issues) si vous rencontrez un problème avec le bot