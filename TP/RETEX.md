
## Choix de l'algo
- Divide & Conquer
> Dur à implémenter
> Existe en librairie
- **Bowyer-Watson**
> Simple à implémenter
> Choix pendant les tests, même si pas de modifs relatifs 

## PLAN.md
Je n'ai pas testé la section 2.2 : lien `Triangulator - PointSetManager`

La section 2.1 est implémentée, mais en contournant la partie où le `PointSet` est récupéré, vu que le `PointSetManager` n'existe pas

Tests de performance : je ne teste pas l'API, donc section 3. `- Requêtes répétées.` ne sera pas faîte

Deux fichiers <90% :
- `Triangulator` : Je ne teste pas la partie `PointSet`, vu qu'elle serait toujours en échec (+ certains sur-vérifications ne se déclenchent pas)
- `Triangle` : Une des vérifications est trop précise sur les bytes, et n'est pas couverte

J'ai fait le choix de ne pas créer de test pour la fonction `Point.to_tuple`, juste pour en avoir moins dans le TP