# Guide du pack ComfyUI — OpenJutsu Capsules

Guide interne de décision et de nomenclature. Les identifiants de code et les fichiers publics sont en anglais ; ce document d'opération est en français.

**Version du document :** 1.0 — 2026-10-21
**Statut :** nomenclature arrêtée, dépôt non encore créé, code non encore extrait.

---

## 1. Décision de nommage

Trois noms distincts, à ne pas confondre.

| Objet | Valeur retenue | Où il vit | Règle |
|---|---|---|---|
| **Dépôt GitHub** | `ComfyUI-OpenJutsu-Capsules` | GitHub | Convention communautaire `ComfyUI-<Nom>` ; facilite la découverte |
| **Identifiant Registry** (`[project].name`) | `openjutsu-capsules` | `pyproject.toml` | La spec **interdit de recommander** « ComfyUI » dans ce champ |
| **PublisherId** | `lvsas` | `pyproject.toml` | Doit correspondre au compte GitHub / publisher enregistré |

### Pourquoi cette séparation

La spécification officielle (`docs.comfy.org/registry/specifications`) impose que `[project].name` serve d'identifiant unique global, utilisé dans les URL et dans `comfy node install <node-id>`. Ses règles :

- moins de 100 caractères ;
- uniquement alphanumériques, tirets, underscores et points ;
- pas de caractères spéciaux consécutifs ;
- ne peut pas commencer par un chiffre ou un caractère spécial ;
- comparaison insensible à la casse ;
- **bonne pratique explicite : ne pas inclure « ComfyUI » dans ce nom.**

L'exemple donné par la spec est sans ambiguïté :

```toml
name = "image-processor"    # ✅
name = "ComfyUI-enhancer"   # ❌ inclut ComfyUI
name = "123-tool"           # ❌ commence par un chiffre
```

Le nom du dépôt GitHub, lui, n'est pas contraint par cette règle : `ComfyUI-` reste la convention la plus lisible pour un utilisateur qui parcourt GitHub. Les deux peuvent donc différer légitimement.

### Ce qui est écarté

| Candidat | Verdict |
|---|---|
| `ComfyUI-OpenJutsu-Capsules` (dépôt) | ✅ retenu |
| `openjutsu-capsules` (registry) | ✅ retenu |
| `ComfyUI-OpenGenjutsu-Continuity` | ❌ trop étroit : le pack vise H3, LTX et FLUX |
| `ComfyUI-Capsules` | ❌ générique, collisionnable |
| `ComfyUI-OpenGenjutsu` | ❌ le pack n'est pas toute l'application |
| `OpenGenjutsu-Capsules` (dépôt sans préfixe) | ❌ moins découvrable |

### Noms internes des nodes

> **Décision ouverte — porte à sens unique.** Les classes portent aujourd'hui le préfixe
> `OpenGenjutsu*` (`OpenGenjutsuH3PublishClip`…). Le produit reste *OpenGenjutsu* ; seul le pack
> s'appelle désormais *OpenJutsu*. Renommer les classes en `OpenJutsu*` est encore possible et
> quasi gratuit tant que rien n'est publié ni installé. Après le premier déploiement, c'est un
> changement cassant : les workflows stockent l'identifiant de classe et sa version.
>
> Coût mesuré d'un renommage maintenant : 13 fichiers suivis, dont `src/h3_swap_native.py`,
> `src/h3_family_graphs.py`, `custom_nodes/opengenjutsu_continuity/*`, les tests, le manifeste,
> et la reconstruction du ZIP. Coût après publication : impossible sans MAJOR + migration.
>
> Tant que cette décision n'est pas prise, l'extraction conserve `OpenGenjutsu*` à l'identique.

- Classes Python : `PascalCase` préfixé par la marque pour éviter toute collision — `OpenGenjutsuH3PublishClip`.
- Clés `NODE_CLASS_MAPPINGS` : identiques au nom de classe.
- `NODE_DISPLAY_NAME_MAPPINGS` : libellés lisibles, avec suffixe technique explicite — `OpenGenjutsu H3 Publish Saved Clip (CPU)`.
- `CATEGORY` : `OpenGenjutsu/Continuity`, `OpenGenjutsu/Capsule`, `OpenGenjutsu/H3`.

Les trois nodes existants gardent **exactement** leurs identifiants actuels pendant l'extraction : un workflow enregistré les référence.

---

## 2. Rôle du pack dans le MVP

Le pack n'est pas un accessoire. Il a deux couches, avec des statuts différents.

### Couche L1 — pont SDK (bloquante)

Le saver H3 stock écrit MP4 + MCTX + COND sur le disque, puis retourne **une simple chaîne** contenant un chemin. Le SDK officiel ne voit qu'un texte : il ne peut ni lister ni télécharger cette famille. À distance, le backend de l'app ne récupère donc que ce que le graphe déclare explicitement comme sortie.

Nos nodes L1 comblent exactement ce trou :

| Node | Fonction |
|---|---|
| `OpenGenjutsuH3PublishClip` | Consomme la sortie réelle du saver, valide les trois fichiers, les déclare comme sorties `ui.files` du job SDK |
| `OpenGenjutsuH3PublishFamily` | Même publication depuis trois chemins explicites |
| `OpenGenjutsuH3RestageFamily` | Réunit trois assets ré-uploadés sous un stem commun lisible par le loader stock |

**Sans L1, pas de collecte de famille native par le SDK.** C'est un prérequis d'A02/A03, donc du premier Forward réel.

### Couche L2 — moteur propre (parallèle)

Objectif : remplacer OBVPM progressivement, pas le renommer.

| Périmètre | Cible |
|---|---|
| H3 état | Notre lecture/écriture MCTX/COND, format versionné, compatibilité historique en lecture |
| H3 opérations | Root, forward, prepend, bridge, refine via le core natif ComfyUI |
| LTX | Persistance AV complète, puis opérations vérifiées séparément |
| FLUX/Character | Capsule image/recette/références réutilisable hors app |
| Utilitaires OBVPM | Réduction du bruit de graphe (presets, bundles, switches) après preuve de branche réellement consommée |

L2 ne bloque pas le premier Forward : celui-ci peut tourner sur le backend OBVPM actuel. L2 est le livrable d'indépendance et d'innovation.

### Ce que le pack ne fait pas

- Il ne charge pas de modèle et ne fait aucun sampling.
- Il n'implémente ni boucle de candidats, ni soumission récursive à la queue, ni auto-refine.
- Il ne prétend pas qu'un latent est universel entre H3, LTX et FLUX.
- Il ne revendique pas l'invention de MCTX, du seed hunting ou du SDK.

---

## 3. Structure du dépôt

```text
ComfyUI-OpenJutsu-Capsules/
├── __init__.py                  # NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
├── nodes.py                     # nodes L1 (publication/restage)
├── family.py                    # validation, confinement, publication atomique
├── _contract/                   # contrats CPU purs, générés et vérifiés
│   ├── __init__.py
│   ├── timeline_artifacts.py
│   ├── safetensor_header.py
│   ├── h3_conditioning.py
│   ├── media_probe.py
│   └── provenance.json
├── adapters/                    # couche L2 (à venir)
│   ├── __init__.py
│   ├── h3/
│   └── ltx/
├── pyproject.toml
├── .comfyignore
├── LICENSE                      # Apache-2.0
├── README.md                    # public, en anglais
└── docs/
    ├── PACK-GUIDE.md            # ce document
    ├── contracts/
    └── examples/
```

Règles :

- `__init__.py` **à la racine** du dossier installé, jamais un niveau plus bas.
- Aucun poids, média, cache, credential ou preuve privée dans l'arborescence versionnée.
- `_contract/` est généré ; ne pas l'éditer à la main sans régénérer la provenance.

---

## 4. `pyproject.toml`

Fichier complet, prêt à l'emploi :

```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "openjutsu-capsules"
version = "0.1.0"
description = "Portable, inspectable and continuable AI video/image Takes for ComfyUI: validated H3 family publication, SDK asset transport and typed capsule contracts."
readme = "README.md"
requires-python = ">=3.10"
license = { file = "LICENSE" }
dependencies = []

classifiers = [
  "Operating System :: POSIX :: Linux",
  "Programming Language :: Python :: 3",
]

[project.urls]
Repository = "https://github.com/lvsas/ComfyUI-OpenJutsu-Capsules"
"Bug Tracker" = "https://github.com/lvsas/ComfyUI-OpenJutsu-Capsules/issues"

[tool.comfy]
PublisherId = "lvsas"
DisplayName = "OpenJutsu Capsules"
requires-comfyui = ">=0.40.0"
```

### Points à confirmer avant publication

| Champ | Statut |
|---|---|
| `name` | arrêté : `openjutsu-capsules` |
| `PublisherId` | `lvsas` à enregistrer sur le Registry avant le premier `publish` |
| `requires-comfyui` | `>=0.40.0` correspond à la version vérifiée sur la cible ; à réévaluer quand L2 dépendra des keyframes H3 natifs |
| `Icon` / `Banner` | non renseignés : ajouter seulement quand un asset carré 400×400 / 21:9 existera réellement |
| Classifiers | Linux seul : `renameat2(RENAME_NOREPLACE)` et `/proc` sont requis. Pas de claim Windows/macOS avant portage testé |

---

## 5. Versionnement

Semver strict `X.Y.Z`, et une version publiée est **immuable** sur le Registry.

| Type de changement | Incrément | Exemple |
|---|---|---|
| Correction de validation, message d'erreur | PATCH | `0.1.1` |
| Nouveau node, nouveau moteur, nouvelle opération | MINOR | `0.2.0` |
| Changement d'identifiant de node, de socket, de format de capsule | MAJOR | `1.0.0` |

Règle interne : **aucun changement d'identifiant de node ou de format de capsule sans MAJOR**, car un workflow enregistré stocke la version du node utilisée.

---

## 6. Installation et preuve

### Installation locale (après autorisation explicite)

```bash
cd /chemin/vers/ComfyUI/custom_nodes
git clone https://github.com/lvsas/ComfyUI-OpenJutsu-Capsules.git
```

Puis redémarrer ComfyUI normalement, quand sa file est vide.

### Vérification que le pack est réellement actif

```bash
curl -s http://<hote>:8188/object_info/OpenGenjutsuH3PublishClip \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(list(d)[0])"
```

Attendu : `OpenGenjutsuH3PublishClip`. Le nom de classe dans `/object_info` est la seule preuve d'enregistrement.

### Ce que l'installation seule ne prouve pas

- que le SDK récupère la famille (il faut un vrai job) ;
- que les états sont rechargeables ;
- que la continuité artistique fonctionne ;
- que le pack est disponible sur Comfy Cloud.

---

## 7. Interdits

1. Installer sur une machine sans accord explicite de son propriétaire.
2. Redémarrer ComfyUI pendant qu'une file tourne.
3. Copier ou renommer l'implémentation d'OBVPM pour produire le moteur propre.
4. Patcher globalement `PackedLayout` ou une fonction core à l'import.
5. Publier une capsule contenant un graphe privé, un token ou un chemin absolu.
6. Déclarer « Native Ready » à partir d'un simple exit code, d'un fichier présent ou d'un test vert.
7. Ajouter un modèle ou un moteur au seul motif d'élargir la vitrine du pack.

---

## 8. Séquence de création

1. **Toi** : créer le dépôt GitHub vide `lvsas/ComfyUI-OpenJutsu-Capsules`, sans README ni licence auto-générés.
2. **Moi** : extraire les trois nodes, `family.py`, `_contract/`, LICENSE et README ; ajouter `pyproject.toml`, `.comfyignore`, ce guide.
3. **Moi** : tests autonomes dans le nouveau dépôt, hash parity avec la source APP, commit initial local.
4. **Toi** : confirmer l'URL, puis je pousse et je vérifie le SHA distant.
5. **Ensuite** : épinglage `UPSTREAM.json` côté APP, puis démarrage de L2.
