# TODO

- Prendre la documentation yml, et définir tous les cas extrêmes (-> erreur)
- Définir les happy path
- 

# 1. Objectif

Ces tests doivent permettre de garantir :
- le fonctionnement correct de l’algorithme de triangulation,
- la conformité de l’API avec la spécification OpenAPI (triangulator.yml),
- la robustesse du service face aux cas limites,
- la performance des opérations critiques (triangulation, sérialisation/désérialisation).

# 2. Tests unitaires et d'intégration
## 2.1. Client - PointSetManager
### 2.1.1. Import d'un PointSet - HappyPath
- Récupération cohérente avec l'Import
### 2.1.2. Import d'un PointSet - ErrorPath
- Taille incorrecte (N incompatible avec taille du binaire)
- contient des bits incompatibles (\in 2-9)
- Envoi vide
### 2.1.3. Récupération du PointSet- HappyPath
> Dans le 2.1.1
### 2.1.4. Récupération du PointSet- ErrorPath
- Database non joignable
- ID forme incorrecte
- ID inexistant


## 2.2. Triangulator - PointSetManager
### 2.2.1. Récupération du PointSet - HappyPath
- Forme correcte
- PointSet N<3
### 2.2.2. Récupération du PointSet - ErrorPath
- PointSetManager non joignable
- ID forme incorrecte
- ID inexistant


## 2.3. Triangulator
Selon la [page Wikipédia des Triangles](https://fr.wikipedia.org/wiki/Triangle#:~:text=D%27autre%20part%2C%20tout%20polygone%20peut%20%C3%AAtre%20d%C3%A9coup%C3%A9%20en%20un%20nombre%20fini%20de%20triangles%20qui%20forment%20alors%20une%20triangulation%20de%20ce%20polygone.%20Le%20nombre%20minimal%20de%20triangles%20n%C3%A9cessaire%20%C3%A0%20ce%20d%C3%A9coupage%20est%20n%2D2%2C), 
un polygône à n côtés (= n sommets) peut être décomposé en un minimum de n-2 triangles.
Dans mes tests, je partirais du principe que tout découpage composé de au moins `n-2` triangles sera correct.  
J'envisage de vérifier que tous les points sont présents au moins une fois dans les triangles renvoyés.
 - HappyPath
 - ErrorPath
### 2.3.1. PointSet vide ou N<3
- Retour d'un ensemble vide de Triangle
### 2.3.2. PointSet correct
- Retour d'un ensemble de plus de `n-2` triangles

# 3. Tests de performance
Cas testés :
- Triangulation d'un grand nombre de points.
- Requêtes répétées.

**Méthode :**
- Temps moyen d’exécution.
- requetes répétées
- Mesure mémoire.
- Tag `@pytest.mark.performance` pour exclusion via `make unit_test`.


# 4. Qualité 
- `ruff check` : aucun avertissement.
- `coverage` : couverture > 90 %.
- `pdoc3` : documentation générée sans erreur.
- `make` : toutes les commandes fonctionnelles (`test`, `lint`, `doc`, etc.).


# 5. Périmètre de TP
Le TP ne concernant que la partie `Triangulator`, il est possible que les `PointSetManager` et `Client` soient mockés.  
Dans ce cas, les tests de la section 2.1 ne seront pas à implémenter, car hors du périmètre du TP.  