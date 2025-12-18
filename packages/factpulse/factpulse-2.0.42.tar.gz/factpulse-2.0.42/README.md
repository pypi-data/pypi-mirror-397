# FactPulse SDK Python

Client Python officiel pour l'API FactPulse - Facturation électronique française.

## Fonctionnalités

- **Factur-X** : Génération et validation de factures électroniques (profils MINIMUM, BASIC, EN16931, EXTENDED)
- **Chorus Pro** : Intégration avec la plateforme de facturation publique française
- **AFNOR PDP/PA** : Soumission de flux conformes à la norme XP Z12-013
- **Signature électronique** : Signature PDF (PAdES-B-B, PAdES-B-T, PAdES-B-LT)
- **Client simplifié** : Authentification JWT et polling intégrés via `factpulse_helpers`

## Installation

```bash
pip install factpulse
```

## Démarrage rapide

Le module `factpulse_helpers` offre une API simplifiée avec authentification et polling automatiques :

```python
from factpulse_helpers import (
    FactPulseClient,
    montant,
    montant_total,
    ligne_de_poste,
    ligne_de_tva,
    fournisseur,
    destinataire,
)

# Créer le client
client = FactPulseClient(
    email="votre_email@example.com",
    password="votre_mot_de_passe"
)

# Construire la facture avec les helpers
facture_data = {
    "numeroFacture": "FAC-2025-001",
    "dateFacture": "2025-01-15",
    "fournisseur": fournisseur(
        nom="Mon Entreprise SAS",
        siret="12345678901234",
        adresse_ligne1="123 Rue Example",
        code_postal="75001",
        ville="Paris",
    ),
    "destinataire": destinataire(
        nom="Client SARL",
        siret="98765432109876",
        adresse_ligne1="456 Avenue Test",
        code_postal="69001",
        ville="Lyon",
    ),
    "montantTotal": montant_total(
        ht=1000.00,
        tva=200.00,
        ttc=1200.00,
        a_payer=1200.00,
    ),
    "lignesDePoste": [
        ligne_de_poste(
            numero=1,
            denomination="Prestation de conseil",
            quantite=10,
            montant_unitaire_ht=100.00,
            montant_total_ligne_ht=1000.00,
        )
    ],
    "lignesDeTva": [
        ligne_de_tva(
            montant_base_ht=1000.00,
            montant_tva=200.00,
            taux_manuel="20.00",
        )
    ],
}

# Générer le PDF Factur-X
with open("facture_source.pdf", "rb") as f:
    pdf_source = f.read()

pdf_bytes = client.generer_facturx(
    facture_data=facture_data,
    pdf_source=pdf_source,
    profil="EN16931",
    sync=True,
)

with open("facture_facturx.pdf", "wb") as f:
    f.write(pdf_bytes)
```

## Helpers disponibles

### montant(value)

Convertit une valeur en string formaté pour les montants monétaires.

```python
from factpulse_helpers import montant

montant(1234.5)      # "1234.50"
montant("1234.56")   # "1234.56"
montant(None)        # "0.00"
```

### montant_total(ht, tva, ttc, a_payer, ...)

Crée un objet MontantTotal complet.

```python
from factpulse_helpers import montant_total

total = montant_total(
    ht=1000.00,
    tva=200.00,
    ttc=1200.00,
    a_payer=1200.00,
    remise_ttc=50.00,          # Optionnel
    motif_remise="Fidélité",   # Optionnel
    acompte=100.00,            # Optionnel
)
```

### ligne_de_poste(numero, denomination, quantite, montant_unitaire_ht, montant_total_ligne_ht, ...)

Crée une ligne de facturation.

```python
from factpulse_helpers import ligne_de_poste

ligne = ligne_de_poste(
    numero=1,
    denomination="Prestation de conseil",
    quantite=5,
    montant_unitaire_ht=200.00,
    montant_total_ligne_ht=1000.00,  # Requis
    taux_tva="TVA20",                # Ou taux_tva_manuel="20.00"
    categorie_tva="S",               # S, Z, E, AE, K
    unite="HEURE",                   # FORFAIT, PIECE, HEURE, JOUR...
    reference="REF-001",             # Optionnel
)
```

### ligne_de_tva(montant_base_ht, montant_tva, ...)

Crée une ligne de ventilation TVA.

```python
from factpulse_helpers import ligne_de_tva

tva = ligne_de_tva(
    montant_base_ht=1000.00,
    montant_tva=200.00,
    taux="TVA20",            # Ou taux_manuel="20.00"
    categorie="S",           # S, Z, E, AE, K
)
```

### adresse_postale(ligne1, code_postal, ville, ...)

Crée une adresse postale structurée.

```python
from factpulse_helpers import adresse_postale

adresse = adresse_postale(
    ligne1="123 Rue de la République",
    code_postal="75001",
    ville="Paris",
    pays="FR",               # Défaut: "FR"
    ligne2="Bâtiment A",     # Optionnel
)
```

### adresse_electronique(identifiant, scheme_id)

Crée une adresse électronique (identifiant numérique).

```python
from factpulse_helpers import adresse_electronique

# SIRET (scheme_id="0225")
adresse = adresse_electronique("12345678901234", "0225")

# SIREN (scheme_id="0009")
adresse = adresse_electronique("123456789", "0009")
```

### fournisseur(nom, siret, adresse_ligne1, code_postal, ville, ...)

Crée un fournisseur complet avec calcul automatique du SIREN et TVA intra.

```python
from factpulse_helpers import fournisseur

f = fournisseur(
    nom="Ma Société SAS",
    siret="12345678901234",
    adresse_ligne1="123 Rue Example",
    code_postal="75001",
    ville="Paris",
    iban="FR7630006000011234567890189",  # Optionnel
)
# SIREN et TVA intracommunautaire calculés automatiquement
```

### destinataire(nom, siret, adresse_ligne1, code_postal, ville, ...)

Crée un destinataire (client) avec calcul automatique du SIREN.

```python
from factpulse_helpers import destinataire

d = destinataire(
    nom="Client SARL",
    siret="98765432109876",
    adresse_ligne1="456 Avenue Test",
    code_postal="69001",
    ville="Lyon",
)
```

## Mode Zero-Trust (Chorus Pro / AFNOR)

Pour passer vos propres credentials sans stockage côté serveur :

```python
from factpulse_helpers import (
    FactPulseClient,
    ChorusProCredentials,
    AFNORCredentials,
)

# Chorus Pro
chorus_creds = ChorusProCredentials(
    piste_client_id="votre_client_id",
    piste_client_secret="votre_client_secret",
    chorus_pro_login="votre_login",
    chorus_pro_password="votre_password",
    sandbox=True,
)

# AFNOR PDP
afnor_creds = AFNORCredentials(
    flow_service_url="https://api.pdp.fr/flow/v1",
    token_url="https://auth.pdp.fr/oauth/token",
    client_id="votre_client_id",
    client_secret="votre_client_secret",
)

client = FactPulseClient(
    email="votre_email@example.com",
    password="votre_mot_de_passe",
    chorus_credentials=chorus_creds,
    afnor_credentials=afnor_creds,
)
```

## Ressources

- **Documentation API** : https://factpulse.fr/api/facturation/documentation
- **Exemple complet** : Voir `exemple_complet_python.py` dans ce package
- **Support** : contact@factpulse.fr

## Licence

MIT License - Copyright (c) 2025 FactPulse
