"""Client simplifié pour l'API FactPulse avec authentification JWT et polling intégrés."""
import base64
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import requests

import factpulse
from factpulse import ApiClient, Configuration, TraitementFactureApi

from .exceptions import (
    FactPulseAuthError,
    FactPulsePollingTimeout,
    FactPulseValidationError,
    ValidationErrorDetail,
)

logger = logging.getLogger(__name__)


# =============================================================================
# JSON Encoder pour Decimal et autres types non sérialisables
# =============================================================================

class DecimalEncoder(json.JSONEncoder):
    """Encoder JSON personnalisé qui gère les Decimal et autres types Python."""

    def default(self, obj):
        if isinstance(obj, Decimal):
            # Convertir en string pour préserver la précision monétaire
            return str(obj)
        if hasattr(obj, "isoformat"):
            # datetime, date, time
            return obj.isoformat()
        if hasattr(obj, "to_dict"):
            # Modèles Pydantic ou dataclasses avec to_dict
            return obj.to_dict()
        return super().default(obj)


def json_dumps_safe(data: Any, **kwargs) -> str:
    """Sérialise en JSON en gérant les Decimal et autres types Python.

    Args:
        data: Données à sérialiser (dict, list, etc.)
        **kwargs: Arguments supplémentaires pour json.dumps

    Returns:
        String JSON

    Example:
        >>> from decimal import Decimal
        >>> json_dumps_safe({"montant": Decimal("1234.56")})
        '{"montant": "1234.56"}'
    """
    kwargs.setdefault("ensure_ascii", False)
    kwargs.setdefault("cls", DecimalEncoder)
    return json.dumps(data, **kwargs)


# =============================================================================
# Credentials dataclasses - pour une configuration simplifiée
# =============================================================================

@dataclass
class ChorusProCredentials:
    """Credentials Chorus Pro pour le mode Zero-Trust.

    Ces credentials sont passés dans chaque requête et ne sont jamais stockés côté serveur.

    Attributes:
        piste_client_id: Client ID PISTE (portail API gouvernement)
        piste_client_secret: Client Secret PISTE
        chorus_pro_login: Login Chorus Pro
        chorus_pro_password: Mot de passe Chorus Pro
        sandbox: True pour l'environnement sandbox, False pour production
    """
    piste_client_id: str
    piste_client_secret: str
    chorus_pro_login: str
    chorus_pro_password: str
    sandbox: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour l'API."""
        return {
            "piste_client_id": self.piste_client_id,
            "piste_client_secret": self.piste_client_secret,
            "chorus_pro_login": self.chorus_pro_login,
            "chorus_pro_password": self.chorus_pro_password,
            "sandbox": self.sandbox,
        }


@dataclass
class AFNORCredentials:
    """Credentials AFNOR PDP pour le mode Zero-Trust.

    Ces credentials sont passés dans chaque requête et ne sont jamais stockés côté serveur.
    L'API FactPulse utilise ces credentials pour s'authentifier auprès de la PDP AFNOR
    et obtenir un token OAuth2 spécifique.

    Attributes:
        flow_service_url: URL du Flow Service de la PDP (ex: https://api.pdp.fr/flow/v1)
        token_url: URL du serveur OAuth2 de la PDP (ex: https://auth.pdp.fr/oauth/token)
        client_id: Client ID OAuth2 de la PDP
        client_secret: Client Secret OAuth2 de la PDP
        directory_service_url: URL du Directory Service (optionnel, déduit de flow_service_url)
    """
    flow_service_url: str
    token_url: str
    client_id: str
    client_secret: str
    directory_service_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour l'API."""
        result = {
            "flow_service_url": self.flow_service_url,
            "token_url": self.token_url,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        if self.directory_service_url:
            result["directory_service_url"] = self.directory_service_url
        return result


# =============================================================================
# Helpers pour les types anyOf - évite la verbosité des wrappers générés
# =============================================================================

def montant(value: Union[str, float, int, Decimal, None]) -> str:
    """Convertit une valeur en string de montant pour l'API.

    L'API FactPulse accepte les montants comme strings ou floats.
    Cette fonction normalise en string pour garantir la précision monétaire.
    """
    if value is None:
        return "0.00"
    if isinstance(value, Decimal):
        return f"{value:.2f}"
    if isinstance(value, (int, float)):
        return f"{value:.2f}"
    if isinstance(value, str):
        return value
    return "0.00"


def montant_total(
    ht: Union[str, float, int, Decimal],
    tva: Union[str, float, int, Decimal],
    ttc: Union[str, float, int, Decimal],
    a_payer: Union[str, float, int, Decimal],
    remise_ttc: Union[str, float, int, Decimal, None] = None,
    motif_remise: Optional[str] = None,
    acompte: Union[str, float, int, Decimal, None] = None,
) -> Dict[str, Any]:
    """Crée un objet MontantTotal simplifié.

    Évite d'avoir à utiliser les wrappers MontantHtTotal, MontantTvaTotal, etc.
    """
    result = {
        "montantHtTotal": montant(ht),
        "montantTva": montant(tva),
        "montantTtcTotal": montant(ttc),
        "montantAPayer": montant(a_payer),
    }
    if remise_ttc is not None:
        result["montantRemiseGlobaleTtc"] = montant(remise_ttc)
    if motif_remise is not None:
        result["motifRemiseGlobaleTtc"] = motif_remise
    if acompte is not None:
        result["acompte"] = montant(acompte)
    return result


def ligne_de_poste(
    numero: int,
    denomination: str,
    quantite: Union[str, float, int, Decimal],
    montant_unitaire_ht: Union[str, float, int, Decimal],
    montant_total_ligne_ht: Union[str, float, int, Decimal],
    taux_tva: Optional[str] = None,
    taux_tva_manuel: Union[str, float, int, Decimal, None] = "20.00",
    categorie_tva: str = "S",
    unite: str = "FORFAIT",
    reference: Optional[str] = None,
    montant_remise_ht: Union[str, float, int, Decimal, None] = None,
    code_raison_reduction: Optional[str] = None,
    raison_reduction: Optional[str] = None,
    date_debut_periode: Optional[str] = None,
    date_fin_periode: Optional[str] = None,
) -> Dict[str, Any]:
    """Crée une ligne de poste pour l'API FactPulse.

    Les clés JSON sont en camelCase (convention API FactPulse).
    Les champs correspondent exactement à LigneDePoste dans models.py.

    Pour le taux de TVA, vous pouvez utiliser soit:
    - taux_tva: Code prédéfini (ex: "TVA20", "TVA10", "TVA5.5")
    - taux_tva_manuel: Valeur numérique (ex: "20.00", 20, 20.0)

    Args:
        numero: Numéro de la ligne
        denomination: Libellé du produit/service
        quantite: Quantité
        montant_unitaire_ht: Prix unitaire HT
        montant_total_ligne_ht: Montant total HT de la ligne
        taux_tva: Code TVA prédéfini (ex: "TVA20") - optionnel
        taux_tva_manuel: Taux de TVA en valeur (défaut: "20.00") - utilisé si taux_tva non fourni
        categorie_tva: Catégorie TVA - S (standard), Z (zéro), E (exonéré), AE (autoliquidation), K (intracommunautaire)
        unite: Unité de facturation (défaut: "FORFAIT")
        reference: Référence article
        montant_remise_ht: Montant de remise HT (optionnel)
        code_raison_reduction: Code raison de la réduction
        raison_reduction: Description textuelle de la réduction
        date_debut_periode: Date début période de facturation (YYYY-MM-DD)
        date_fin_periode: Date fin période de facturation (YYYY-MM-DD)
    """
    result = {
        "numero": numero,
        "denomination": denomination,
        "quantite": montant(quantite),
        "montantUnitaireHt": montant(montant_unitaire_ht),
        "montantTotalLigneHt": montant(montant_total_ligne_ht),
        "categorieTva": categorie_tva,
        "unite": unite,
    }
    # Soit taux_tva (code) soit taux_tva_manuel (valeur)
    if taux_tva is not None:
        result["tauxTva"] = taux_tva
    elif taux_tva_manuel is not None:
        result["tauxTvaManuel"] = montant(taux_tva_manuel)
    if reference is not None:
        result["reference"] = reference
    if montant_remise_ht is not None:
        result["montantRemiseHt"] = montant(montant_remise_ht)
    if code_raison_reduction is not None:
        result["codeRaisonReduction"] = code_raison_reduction
    if raison_reduction is not None:
        result["raisonReduction"] = raison_reduction
    if date_debut_periode is not None:
        result["dateDebutPeriode"] = date_debut_periode
    if date_fin_periode is not None:
        result["dateFinPeriode"] = date_fin_periode
    return result


def ligne_de_tva(
    montant_base_ht: Union[str, float, int, Decimal],
    montant_tva: Union[str, float, int, Decimal],
    taux: Optional[str] = None,
    taux_manuel: Union[str, float, int, Decimal, None] = "20.00",
    categorie: str = "S",
) -> Dict[str, Any]:
    """Crée une ligne de TVA pour l'API FactPulse.

    Les clés JSON sont en camelCase (convention API FactPulse).
    Les champs correspondent exactement à LigneDeTVA dans models.py.

    Pour le taux de TVA, vous pouvez utiliser soit:
    - taux: Code prédéfini (ex: "TVA20", "TVA10", "TVA5.5")
    - taux_manuel: Valeur numérique (ex: "20.00", 20, 20.0)

    Args:
        montant_base_ht: Montant de la base HT
        montant_tva: Montant de la TVA
        taux: Code TVA prédéfini (ex: "TVA20") - optionnel
        taux_manuel: Taux de TVA en valeur (défaut: "20.00") - utilisé si taux non fourni
        categorie: Catégorie de TVA (défaut: "S" pour standard)
    """
    result = {
        "montantBaseHt": montant(montant_base_ht),
        "montantTva": montant(montant_tva),
        "categorie": categorie,
    }
    # Soit taux (code) soit taux_manuel (valeur)
    if taux is not None:
        result["taux"] = taux
    elif taux_manuel is not None:
        result["tauxManuel"] = montant(taux_manuel)
    return result


def adresse_postale(
    ligne1: str,
    code_postal: str,
    ville: str,
    pays: str = "FR",
    ligne2: Optional[str] = None,
    ligne3: Optional[str] = None,
) -> Dict[str, Any]:
    """Crée une adresse postale pour l'API FactPulse.

    Args:
        ligne1: Première ligne d'adresse (numéro, rue)
        code_postal: Code postal
        ville: Nom de la ville
        pays: Code pays ISO (défaut: "FR")
        ligne2: Deuxième ligne d'adresse (optionnel)
        ligne3: Troisième ligne d'adresse (optionnel)

    Example:
        >>> adresse = adresse_postale("123 rue Example", "75001", "Paris")
    """
    result = {
        "ligneUn": ligne1,
        "codePostal": code_postal,
        "nomVille": ville,
        "paysCodeIso": pays,
    }
    if ligne2:
        result["ligneDeux"] = ligne2
    if ligne3:
        result["ligneTrois"] = ligne3
    return result


def adresse_electronique(
    identifiant: str,
    scheme_id: str = "0009",
) -> Dict[str, Any]:
    """Crée une adresse électronique pour l'API FactPulse.

    Args:
        identifiant: Identifiant de l'adresse (SIRET, SIREN, etc.)
        scheme_id: Schéma d'identification (défaut: "0009" pour SIREN)
            - "0009": SIREN
            - "0088": EAN
            - "0096": DUNS
            - "0130": Codification propre
            - "0225": FR - SIRET (schéma français)

    Example:
        >>> adresse = adresse_electronique("12345678901234", "0225")  # SIRET
    """
    return {
        "identifiant": identifiant,
        "schemeId": scheme_id,
    }


def fournisseur(
    nom: str,
    siret: str,
    adresse_ligne1: str,
    code_postal: str,
    ville: str,
    id_fournisseur: int = 0,
    siren: Optional[str] = None,
    numero_tva_intra: Optional[str] = None,
    iban: Optional[str] = None,
    pays: str = "FR",
    adresse_ligne2: Optional[str] = None,
    code_service: Optional[int] = None,
    code_coordonnees_bancaires: Optional[int] = None,
) -> Dict[str, Any]:
    """Crée un fournisseur (émetteur de la facture) pour l'API FactPulse.

    Cette fonction simplifie la création d'un fournisseur en générant automatiquement:
    - L'adresse postale structurée
    - L'adresse électronique (basée sur le SIRET)
    - Le SIREN (extrait du SIRET si non fourni)
    - Le numéro de TVA intracommunautaire (calculé depuis le SIREN si non fourni)

    Args:
        nom: Raison sociale / dénomination
        siret: Numéro SIRET (14 chiffres)
        adresse_ligne1: Première ligne d'adresse
        code_postal: Code postal
        ville: Ville
        id_fournisseur: ID Chorus Pro du fournisseur (défaut: 0)
        siren: Numéro SIREN (9 chiffres) - calculé depuis SIRET si absent
        numero_tva_intra: Numéro TVA intracommunautaire - calculé si absent
        iban: IBAN pour le paiement
        pays: Code pays ISO (défaut: "FR")
        adresse_ligne2: Deuxième ligne d'adresse (optionnel)
        code_service: ID du service fournisseur Chorus Pro (optionnel)
        code_coordonnees_bancaires: Code coordonnées bancaires Chorus Pro (optionnel)

    Returns:
        Dict prêt à être utilisé dans une facture

    Example:
        >>> f = fournisseur(
        ...     nom="Ma Société SAS",
        ...     siret="12345678900001",
        ...     adresse_ligne1="123 Rue de la République",
        ...     code_postal="75001",
        ...     ville="Paris",
        ...     iban="FR7630006000011234567890189",
        ... )
    """
    # Auto-calcul SIREN depuis SIRET
    if not siren and len(siret) == 14:
        siren = siret[:9]

    # Auto-calcul TVA intracommunautaire française
    if not numero_tva_intra and siren and len(siren) == 9:
        # Clé TVA = (12 + 3 * (SIREN % 97)) % 97
        try:
            cle = (12 + 3 * (int(siren) % 97)) % 97
            numero_tva_intra = f"FR{cle:02d}{siren}"
        except ValueError:
            pass  # SIREN non numérique, on skip

    result: Dict[str, Any] = {
        "nom": nom,
        "idFournisseur": id_fournisseur,
        "siret": siret,
        "adresseElectronique": adresse_electronique(siret, "0225"),
        "adressePostale": adresse_postale(adresse_ligne1, code_postal, ville, pays, adresse_ligne2),
    }

    if siren:
        result["siren"] = siren
    if numero_tva_intra:
        result["numeroTvaIntra"] = numero_tva_intra
    if iban:
        result["iban"] = iban
    if code_service:
        result["idServiceFournisseur"] = code_service
    if code_coordonnees_bancaires:
        result["codeCoordonnesBancairesFournisseur"] = code_coordonnees_bancaires

    return result


def destinataire(
    nom: str,
    siret: str,
    adresse_ligne1: str,
    code_postal: str,
    ville: str,
    siren: Optional[str] = None,
    pays: str = "FR",
    adresse_ligne2: Optional[str] = None,
    code_service_executant: Optional[str] = None,
) -> Dict[str, Any]:
    """Crée un destinataire (client de la facture) pour l'API FactPulse.

    Cette fonction simplifie la création d'un destinataire en générant automatiquement:
    - L'adresse postale structurée
    - L'adresse électronique (basée sur le SIRET)
    - Le SIREN (extrait du SIRET si non fourni)

    Args:
        nom: Raison sociale / dénomination
        siret: Numéro SIRET (14 chiffres)
        adresse_ligne1: Première ligne d'adresse
        code_postal: Code postal
        ville: Ville
        siren: Numéro SIREN (9 chiffres) - calculé depuis SIRET si absent
        pays: Code pays ISO (défaut: "FR")
        adresse_ligne2: Deuxième ligne d'adresse (optionnel)
        code_service_executant: Code du service destinataire (optionnel)

    Returns:
        Dict prêt à être utilisé dans une facture

    Example:
        >>> d = destinataire(
        ...     nom="Client SARL",
        ...     siret="98765432109876",
        ...     adresse_ligne1="456 Avenue des Champs",
        ...     code_postal="69001",
        ...     ville="Lyon",
        ... )
    """
    # Auto-calcul SIREN depuis SIRET
    if not siren and len(siret) == 14:
        siren = siret[:9]

    result: Dict[str, Any] = {
        "nom": nom,
        "siret": siret,
        "adresseElectronique": adresse_electronique(siret, "0225"),
        "adressePostale": adresse_postale(adresse_ligne1, code_postal, ville, pays, adresse_ligne2),
    }

    if siren:
        result["siren"] = siren
    if code_service_executant:
        result["codeServiceExecutant"] = code_service_executant

    return result


def beneficiaire(
    nom: str,
    siret: Optional[str] = None,
    siren: Optional[str] = None,
    iban: Optional[str] = None,
    bic: Optional[str] = None,
) -> Dict[str, Any]:
    """Crée un bénéficiaire (factor) pour l'affacturage.

    Le bénéficiaire (BG-10 / PayeeTradeParty) est utilisé lorsque le paiement
    doit être effectué à un tiers différent du fournisseur, typiquement un
    factor (société d'affacturage).

    Pour les factures affacturées, il faut aussi:
    - Utiliser un type de document affacturé (393, 396, 501, 502, 472, 473)
    - Ajouter une note ACC avec la mention de subrogation
    - L'IBAN du bénéficiaire sera utilisé pour le paiement

    Args:
        nom: Raison sociale du factor (BT-59)
        siret: Numéro SIRET du factor (BT-60, schemeID 0009) - 14 chiffres
        siren: Numéro SIREN du factor (BT-61, schemeID 0002) - calculé depuis SIRET si absent
        iban: IBAN du factor - pour recevoir le paiement
        bic: BIC de la banque du factor (optionnel)

    Returns:
        Dict prêt à être utilisé dans une facture affacturée

    Example:
        >>> # Facture affacturée simple
        >>> factor = beneficiaire(
        ...     nom="FACTOR SAS",
        ...     siret="30000000700033",
        ...     iban="FR76 3000 4000 0500 0012 3456 789",
        ... )
        >>> facture = {
        ...     "numeroFacture": "FAC-2025-001-AFF",
        ...     "fournisseur": fournisseur(...),
        ...     "destinataire": destinataire(...),
        ...     "beneficiaire": factor,  # Le factor reçoit le paiement
        ...     "references": {
        ...         "typeFacture": "393",  # Facture affacturée
        ...         ...
        ...     },
        ...     "notes": [
        ...         {
        ...             "contenu": "Cette créance a été cédée à FACTOR SAS. Contrat n° AFF-2025",
        ...             "codeObjet": "ACC",  # Code subrogation obligatoire
        ...         },
        ...         ...
        ...     ],
        ...     ...
        ... }

    See Also:
        - Guide affacturage: docs/guide_affacturage.md
        - Types de documents affacturés: 393 (facture), 396 (avoir), 501, 502, 472, 473
        - Note ACC: Clause de subrogation factoring (obligatoire)
    """
    # Auto-calcul SIREN depuis SIRET
    if not siren and siret and len(siret) == 14:
        siren = siret[:9]

    result: Dict[str, Any] = {
        "nom": nom,
    }

    if siret:
        result["siret"] = siret
    if siren:
        result["siren"] = siren
    if iban:
        result["iban"] = iban
    if bic:
        result["bic"] = bic

    return result


class FactPulseClient:
    """Client simplifié pour l'API FactPulse.

    Gère l'authentification JWT, le polling des tâches asynchrones,
    et permet de configurer les credentials Chorus Pro / AFNOR à l'initialisation.
    """

    DEFAULT_API_URL = "https://factpulse.fr"
    DEFAULT_POLLING_INTERVAL = 2000  # ms
    DEFAULT_POLLING_TIMEOUT = 120000  # ms
    DEFAULT_MAX_RETRIES = 1

    def __init__(
        self,
        email: str,
        password: str,
        api_url: Optional[str] = None,
        client_uid: Optional[str] = None,
        chorus_credentials: Optional[ChorusProCredentials] = None,
        afnor_credentials: Optional[AFNORCredentials] = None,
        polling_interval: Optional[int] = None,
        polling_timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ):
        self.email = email
        self.password = password
        self.api_url = (api_url or self.DEFAULT_API_URL).rstrip("/")
        self.client_uid = client_uid
        self.chorus_credentials = chorus_credentials
        self.afnor_credentials = afnor_credentials
        self.polling_interval = polling_interval or self.DEFAULT_POLLING_INTERVAL
        self.polling_timeout = polling_timeout or self.DEFAULT_POLLING_TIMEOUT
        self.max_retries = max_retries if max_retries is not None else self.DEFAULT_MAX_RETRIES

        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._api_client: Optional[ApiClient] = None

    def get_chorus_credentials_for_api(self) -> Optional[Dict[str, Any]]:
        """Retourne les credentials Chorus Pro au format API."""
        return self.chorus_credentials.to_dict() if self.chorus_credentials else None

    def get_afnor_credentials_for_api(self) -> Optional[Dict[str, Any]]:
        """Retourne les credentials AFNOR au format API."""
        return self.afnor_credentials.to_dict() if self.afnor_credentials else None

    # Alias plus courts pour faciliter l'usage
    def get_chorus_pro_credentials(self) -> Optional[Dict[str, Any]]:
        """Alias pour get_chorus_credentials_for_api()."""
        return self.get_chorus_credentials_for_api()

    def get_afnor_credentials(self) -> Optional[Dict[str, Any]]:
        """Alias pour get_afnor_credentials_for_api()."""
        return self.get_afnor_credentials_for_api()

    def _obtain_token(self) -> Dict[str, str]:
        """Obtient un nouveau token JWT."""
        token_url = f"{self.api_url}/api/token/"
        payload = {"username": self.email, "password": self.password}
        if self.client_uid:
            payload["client_uid"] = self.client_uid

        try:
            response = requests.post(token_url, json=payload, timeout=30)
            response.raise_for_status()
            logger.info("Token JWT obtenu pour %s", self.email)
            return response.json()
        except requests.RequestException as e:
            error_detail = ""
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_detail = e.response.json().get("detail", str(e))
                except Exception:
                    error_detail = str(e)
            raise FactPulseAuthError(f"Impossible d'obtenir le token JWT: {error_detail or e}")

    def _refresh_access_token(self) -> str:
        """Rafraîchit le token d'accès."""
        if not self._refresh_token:
            raise FactPulseAuthError("Aucun refresh token disponible")

        refresh_url = f"{self.api_url}/api/token/refresh/"
        try:
            response = requests.post(
                refresh_url, json={"refresh": self._refresh_token}, timeout=30
            )
            response.raise_for_status()
            logger.info("Token rafraîchi avec succès")
            return response.json()["access"]
        except requests.RequestException:
            logger.warning("Refresh échoué, ré-obtention d'un nouveau token")
            tokens = self._obtain_token()
            self._refresh_token = tokens["refresh"]
            return tokens["access"]

    def ensure_authenticated(self, force_refresh: bool = False) -> None:
        """S'assure que le client est authentifié."""
        now = datetime.now()

        if force_refresh or not self._access_token or not self._token_expires_at or now >= self._token_expires_at:
            if self._refresh_token and self._token_expires_at and not force_refresh:
                try:
                    self._access_token = self._refresh_access_token()
                    self._token_expires_at = now + timedelta(minutes=28)
                    return
                except FactPulseAuthError:
                    pass

            tokens = self._obtain_token()
            self._access_token = tokens["access"]
            self._refresh_token = tokens["refresh"]
            self._token_expires_at = now + timedelta(minutes=28)

    def reset_auth(self) -> None:
        """Réinitialise l'authentification."""
        self._access_token = None
        self._refresh_token = None
        self._token_expires_at = None
        self._api_client = None
        logger.info("Authentification réinitialisée")

    def get_traitement_api(self) -> TraitementFactureApi:
        """Retourne l'API de traitement de factures."""
        self.ensure_authenticated()
        config = Configuration(host=f"{self.api_url}/api/facturation")
        config.access_token = self._access_token
        self._api_client = ApiClient(configuration=config)
        return TraitementFactureApi(api_client=self._api_client)

    def poll_task(self, task_id: str, timeout: Optional[int] = None, interval: Optional[int] = None) -> Dict[str, Any]:
        """Effectue un polling sur une tâche jusqu'à son achèvement."""
        timeout_ms = timeout or self.polling_timeout
        interval_ms = interval or self.polling_interval

        start_time = time.time() * 1000
        current_interval = float(interval_ms)

        logger.info("Début du polling pour la tâche %s (timeout: %dms)", task_id, timeout_ms)

        while True:
            elapsed = (time.time() * 1000) - start_time

            if elapsed > timeout_ms:
                raise FactPulsePollingTimeout(task_id, timeout_ms)

            try:
                logger.debug("Polling tâche %s (elapsed: %.0fms)...", task_id, elapsed)
                api = self.get_traitement_api()
                statut = api.obtenir_statut_tache_api_v1_traitement_taches_id_tache_statut_get(id_tache=task_id)
                logger.debug("Réponse statut reçue: %s", statut)

                status_value = statut.statut.value if hasattr(statut.statut, "value") else str(statut.statut)
                logger.info("Tâche %s: statut=%s (%.0fms)", task_id, status_value, elapsed)

                if status_value == "SUCCESS":
                    logger.info("Tâche %s terminée avec succès", task_id)
                    if statut.resultat:
                        if hasattr(statut.resultat, "to_dict"):
                            return statut.resultat.to_dict()
                        return dict(statut.resultat)
                    return {}

                if status_value == "FAILURE":
                    error_msg = "Erreur inconnue"
                    errors = []
                    if statut.resultat:
                        result = statut.resultat.to_dict() if hasattr(statut.resultat, "to_dict") else dict(statut.resultat)
                        # Format AFNOR: errorMessage, details
                        error_msg = result.get("errorMessage", error_msg)
                        for err in result.get("details", []):
                            errors.append(ValidationErrorDetail(
                                level=err.get("level", ""),
                                item=err.get("item", ""),
                                reason=err.get("reason", ""),
                                source=err.get("source"),
                                code=err.get("code"),
                            ))
                    raise FactPulseValidationError(f"La tâche {task_id} a échoué: {error_msg}", errors)

            except (FactPulseValidationError, FactPulsePollingTimeout):
                raise
            except Exception as e:
                error_str = str(e)
                logger.warning("Erreur lors du polling: %s", error_str)

                # Rate limit (429) - attendre et réessayer avec backoff
                if "429" in error_str:
                    wait_time = min(current_interval * 2, 30000)  # Max 30s
                    logger.warning("Rate limit (429), attente de %.1fs avant retry...", wait_time / 1000)
                    time.sleep(wait_time / 1000)
                    current_interval = wait_time
                    continue

                # Token expiré (401) - re-authentification
                if "401" in error_str:
                    logger.warning("Token expiré, re-authentification...")
                    self.reset_auth()
                    continue

                # Erreur serveur temporaire (502, 503, 504) - retry avec backoff
                if any(code in error_str for code in ("502", "503", "504")):
                    wait_time = min(current_interval * 1.5, 15000)
                    logger.warning("Erreur serveur temporaire, attente de %.1fs avant retry...", wait_time / 1000)
                    time.sleep(wait_time / 1000)
                    current_interval = wait_time
                    continue

                raise FactPulseValidationError(f"Erreur API: {e}")

            time.sleep(current_interval / 1000)
            current_interval = min(current_interval * 1.5, 10000)

    def generer_facturx(
        self,
        facture_data: Union[Dict, str, Any],
        pdf_source: Union[bytes, str, Path],
        profil: str = "EN16931",
        format_sortie: str = "pdf",
        sync: bool = True,
        timeout: Optional[int] = None,
    ) -> bytes:
        """Génère une facture Factur-X.

        Accepte les données de facture sous plusieurs formes :
        - Dict : dictionnaire Python (recommandé avec les helpers montant_total(), ligne_de_poste(), etc.)
        - str : JSON sérialisé
        - Modèle Pydantic : modèle généré par le SDK (sera converti via .to_dict())

        Args:
            facture_data: Données de la facture (dict, JSON string, ou modèle Pydantic)
            pdf_source: Chemin vers le PDF source, ou bytes du PDF
            profil: Profil Factur-X (MINIMUM, BASIC, EN16931, EXTENDED)
            format_sortie: Format de sortie (pdf, xml, both)
            sync: Si True, attend la fin de la tâche et retourne le résultat
            timeout: Timeout en ms pour le polling

        Returns:
            bytes: Contenu du fichier généré (PDF ou XML)
        """
        # Conversion des données en JSON string (gère Decimal, datetime, etc.)
        if isinstance(facture_data, str):
            json_data = facture_data
        elif isinstance(facture_data, dict):
            json_data = json_dumps_safe(facture_data)
        elif hasattr(facture_data, "to_dict"):
            # Modèle Pydantic généré par le SDK
            json_data = json_dumps_safe(facture_data.to_dict())
        else:
            raise FactPulseValidationError(f"Type de données non supporté: {type(facture_data)}")

        # Préparation du PDF
        if isinstance(pdf_source, (str, Path)):
            pdf_path = Path(pdf_source)
            pdf_bytes = pdf_path.read_bytes()
            pdf_filename = pdf_path.name
        else:
            pdf_bytes = pdf_source
            pdf_filename = "source.pdf"

        # Envoi direct via requests (bypass des modèles Pydantic du SDK)
        for attempt in range(self.max_retries + 1):
            self.ensure_authenticated()
            try:
                url = f"{self.api_url}/api/v1/traitement/generer-facture"
                files = {
                    "donnees_facture": (None, json_data, "application/json"),
                    "profil": (None, profil),
                    "format_sortie": (None, format_sortie),
                    "source_pdf": (pdf_filename, pdf_bytes, "application/pdf"),
                }
                headers = {"Authorization": f"Bearer {self._access_token}"}
                response = requests.post(url, files=files, headers=headers, timeout=60)

                if response.status_code == 401 and attempt < self.max_retries:
                    logger.warning("Erreur 401, réinitialisation du token (tentative %d/%d)", attempt + 1, self.max_retries + 1)
                    self.reset_auth()
                    continue

                # Gérer les erreurs HTTP avec extraction du corps de réponse
                if response.status_code >= 400:
                    error_body = None
                    try:
                        error_body = response.json()
                    except Exception:
                        error_body = {"detail": response.text or f"HTTP {response.status_code}"}

                    # Log détaillé de l'erreur
                    logger.error("Erreur API %d: %s", response.status_code, error_body)

                    # Extraire les détails d'erreur au format standardisé
                    errors = []
                    error_msg = f"Erreur HTTP {response.status_code}"

                    if isinstance(error_body, dict):
                        # Format FastAPI/Pydantic: {"detail": [{"loc": [...], "msg": "...", "type": "..."}]}
                        if "detail" in error_body:
                            detail = error_body["detail"]
                            if isinstance(detail, list):
                                # Liste d'erreurs de validation Pydantic
                                error_msg = "Erreur de validation"
                                for err in detail:
                                    if isinstance(err, dict):
                                        loc = err.get("loc", [])
                                        loc_str = " -> ".join(str(l) for l in loc) if loc else ""
                                        errors.append(ValidationErrorDetail(
                                            level="ERROR",
                                            item=loc_str,
                                            reason=err.get("msg", str(err)),
                                            source="validation",
                                            code=err.get("type"),
                                        ))
                            elif isinstance(detail, str):
                                error_msg = detail
                        # Format AFNOR: {"errorMessage": "...", "details": [...]}
                        elif "errorMessage" in error_body:
                            error_msg = error_body["errorMessage"]
                            for err in error_body.get("details", []):
                                errors.append(ValidationErrorDetail(
                                    level=err.get("level", "ERROR"),
                                    item=err.get("item", ""),
                                    reason=err.get("reason", ""),
                                    source=err.get("source"),
                                    code=err.get("code"),
                                ))

                    # Pour les erreurs 422 (validation), ne pas réessayer
                    if response.status_code == 422:
                        raise FactPulseValidationError(error_msg, errors)

                    # Pour les autres erreurs client (4xx), ne pas réessayer non plus
                    if 400 <= response.status_code < 500:
                        raise FactPulseValidationError(error_msg, errors)

                    # Pour les erreurs serveur (5xx), réessayer si possible
                    if attempt < self.max_retries:
                        logger.warning("Erreur serveur %d (tentative %d/%d)", response.status_code, attempt + 1, self.max_retries + 1)
                        continue
                    raise FactPulseValidationError(error_msg, errors)

                result = response.json()
                task_id = result.get("id_tache")

                if not task_id:
                    raise FactPulseValidationError("Pas d'ID de tâche dans la réponse")

                if not sync:
                    return task_id.encode()

                poll_result = self.poll_task(task_id, timeout)

                if poll_result.get("statut") == "ERREUR":
                    # Format AFNOR: errorMessage, details
                    error_msg = poll_result.get("errorMessage", "Erreur de validation")
                    errors = [
                        ValidationErrorDetail(
                            level=e.get("level", ""),
                            item=e.get("item", ""),
                            reason=e.get("reason", ""),
                            source=e.get("source"),
                            code=e.get("code"),
                        )
                        for e in poll_result.get("details", [])
                    ]
                    raise FactPulseValidationError(error_msg, errors)

                if "contenu_b64" in poll_result:
                    return base64.b64decode(poll_result["contenu_b64"])

                raise FactPulseValidationError("Le résultat ne contient pas de contenu")

            except requests.RequestException as e:
                # Erreurs réseau (connexion, timeout, etc.) - pas d'erreur HTTP
                if attempt < self.max_retries:
                    logger.warning("Erreur réseau (tentative %d/%d): %s", attempt + 1, self.max_retries + 1, e)
                    continue
                raise FactPulseValidationError(f"Erreur réseau: {e}")

        raise FactPulseValidationError("Échec après toutes les tentatives")

    @staticmethod
    def format_montant(montant) -> str:
        """Formate un montant pour l'API FactPulse."""
        if montant is None:
            return "0.00"
        if isinstance(montant, Decimal):
            return f"{montant:.2f}"
        if isinstance(montant, (int, float)):
            return f"{montant:.2f}"
        if isinstance(montant, str):
            return montant
        return "0.00"

    # =========================================================================
    # AFNOR PDP/PA - Flow Service
    # =========================================================================
    #
    # ARCHITECTURE GRAVÉE DANS LE MARBRE - NE PAS MODIFIER SANS COMPRENDRE
    #
    # Le proxy AFNOR est 100% TRANSPARENT. Il a le même OpenAPI que l'AFNOR.
    # Le SDK doit TOUJOURS :
    # 1. Obtenir les credentials AFNOR (mode stored: via /credentials, mode zero-trust: fournis)
    # 2. Faire l'OAuth AFNOR lui-même
    # 3. Appeler les endpoints avec le token AFNOR + header X-PDP-Base-URL
    #
    # Le token JWT FactPulse n'est JAMAIS utilisé pour appeler la PDP !
    # =========================================================================

    def _get_afnor_credentials(self) -> "AFNORCredentials":
        """Obtient les credentials AFNOR (mode stored ou zero-trust).

        **Mode zero-trust** : Retourne les afnor_credentials fournis au constructeur.
        **Mode stored** : Récupère les credentials via GET /api/v1/afnor/credentials.

        Returns:
            AFNORCredentials avec flow_service_url, token_url, client_id, client_secret

        Raises:
            FactPulseAuthError: Si pas de credentials disponibles
            FactPulseServiceUnavailableError: Si le serveur est indisponible
        """
        from .exceptions import FactPulseServiceUnavailableError

        # Mode zero-trust : credentials fournis au constructeur
        if self.afnor_credentials:
            logger.info("Mode zero-trust: utilisation des AFNORCredentials fournis")
            return self.afnor_credentials

        # Mode stored : récupérer les credentials via l'API
        logger.info("Mode stored: récupération des credentials via /api/v1/afnor/credentials")

        self.ensure_authenticated()  # S'assurer qu'on a un token JWT FactPulse

        url = f"{self.api_url}/api/v1/afnor/credentials"
        headers = {"Authorization": f"Bearer {self._access_token}"}

        try:
            response = requests.get(url, headers=headers, timeout=10)
        except requests.RequestException as e:
            raise FactPulseServiceUnavailableError("FactPulse AFNOR credentials", e)

        if response.status_code == 400:
            error_json = response.json()
            error_detail = error_json.get("detail", {})
            if isinstance(error_detail, dict) and error_detail.get("error") == "NO_CLIENT_UID":
                raise FactPulseAuthError(
                    "Aucun client_uid dans le JWT. "
                    "Pour utiliser les endpoints AFNOR, soit :\n"
                    "1. Générez un token avec un client_uid (mode stored)\n"
                    "2. Fournissez AFNORCredentials au constructeur du client (mode zero-trust)"
                )
            raise FactPulseAuthError(f"Erreur credentials AFNOR: {error_detail}")

        if response.status_code != 200:
            try:
                error_json = response.json()
                error_msg = error_json.get("detail", str(error_json))
            except Exception:
                error_msg = response.text or f"HTTP {response.status_code}"
            raise FactPulseAuthError(f"Échec récupération credentials AFNOR: {error_msg}")

        creds = response.json()
        logger.info(f"Credentials AFNOR récupérés pour PDP: {creds.get('flow_service_url')}")

        # Créer un AFNORCredentials temporaire
        return AFNORCredentials(
            flow_service_url=creds["flow_service_url"],
            token_url=creds["token_url"],
            client_id=creds["client_id"],
            client_secret=creds["client_secret"],
        )

    def _get_afnor_token_and_url(self) -> Tuple[str, str]:
        """Obtient le token OAuth2 AFNOR et l'URL de la PDP.

        Cette méthode :
        1. Récupère les credentials AFNOR (mode stored ou zero-trust)
        2. Fait l'OAuth AFNOR pour obtenir un token
        3. Retourne le token et l'URL de la PDP

        Returns:
            Tuple (afnor_token, pdp_base_url)

        Raises:
            FactPulseAuthError: Si l'authentification échoue
            FactPulseServiceUnavailableError: Si le service est indisponible
        """
        from .exceptions import FactPulseServiceUnavailableError

        # Étape 1: Obtenir les credentials AFNOR
        credentials = self._get_afnor_credentials()

        # Étape 2: Faire l'OAuth AFNOR
        logger.info(f"OAuth AFNOR vers: {credentials.token_url}")

        url = f"{self.api_url}/api/v1/afnor/oauth/token"
        oauth_data = {
            "grant_type": "client_credentials",
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
        }
        headers = {
            "X-PDP-Token-URL": credentials.token_url,
        }

        try:
            response = requests.post(url, data=oauth_data, headers=headers, timeout=10)
        except requests.RequestException as e:
            raise FactPulseServiceUnavailableError("AFNOR OAuth", e)

        if response.status_code != 200:
            try:
                error_json = response.json()
                error_msg = error_json.get("detail", error_json.get("error", str(error_json)))
            except Exception:
                error_msg = response.text or f"HTTP {response.status_code}"
            raise FactPulseAuthError(f"Échec OAuth2 AFNOR: {error_msg}")

        token_data = response.json()
        afnor_token = token_data.get("access_token")

        if not afnor_token:
            raise FactPulseAuthError("Réponse OAuth2 AFNOR invalide: access_token manquant")

        logger.info("Token OAuth2 AFNOR obtenu avec succès")
        return afnor_token, credentials.flow_service_url

    def _make_afnor_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> requests.Response:
        """Effectue une requête vers l'API AFNOR avec gestion d'auth et d'erreurs.

        ================================================================================
        ARCHITECTURE GRAVÉE DANS LE MARBRE
        ================================================================================

        Cette méthode :
        1. Récupère les credentials AFNOR (mode stored: API, mode zero-trust: fournis)
        2. Fait l'OAuth AFNOR pour obtenir un token AFNOR
        3. Appelle l'endpoint avec :
           - Authorization: Bearer {token_afnor}  ← TOKEN AFNOR, PAS JWT FACTPULSE !
           - X-PDP-Base-URL: {url_pdp}  ← Pour que le proxy route vers la bonne PDP

        Le token JWT FactPulse n'est JAMAIS utilisé pour appeler la PDP.
        Il sert uniquement à récupérer les credentials en mode stored.

        ================================================================================

        Args:
            method: Méthode HTTP (GET, POST, etc.)
            endpoint: Endpoint relatif (ex: /flow/v1/flows)
            json_data: Données JSON (optionnel)
            files: Fichiers multipart (optionnel)
            params: Query params (optionnel)

        Returns:
            Response de l'API

        Raises:
            FactPulseAuthError: Si 401 ou credentials manquants
            FactPulseNotFoundError: Si 404
            FactPulseServiceUnavailableError: Si 503
            FactPulseValidationError: Si 400/422
            FactPulseAPIError: Autres erreurs
        """
        from .exceptions import (
            parse_api_error,
            FactPulseServiceUnavailableError,
        )

        # Obtenir le token AFNOR et l'URL de la PDP
        # (mode stored: récupère credentials via API, mode zero-trust: utilise credentials fournis)
        afnor_token, pdp_base_url = self._get_afnor_token_and_url()

        url = f"{self.api_url}/api/v1/afnor{endpoint}"

        # TOUJOURS utiliser le token AFNOR + header X-PDP-Base-URL
        # Le token JWT FactPulse n'est JAMAIS utilisé pour appeler la PDP !
        headers = {
            "Authorization": f"Bearer {afnor_token}",
            "X-PDP-Base-URL": pdp_base_url,
        }

        try:
            if files:
                response = requests.request(
                    method, url, files=files, headers=headers, params=params, timeout=60
                )
            else:
                response = requests.request(
                    method, url, json=json_data, headers=headers, params=params, timeout=30
                )
        except requests.RequestException as e:
            raise FactPulseServiceUnavailableError("AFNOR PDP", e)

        if response.status_code >= 400:
            try:
                error_json = response.json()
            except Exception:
                error_json = {"errorMessage": response.text or f"Erreur HTTP {response.status_code}"}
            raise parse_api_error(error_json, response.status_code)

        return response

    def soumettre_facture_afnor(
        self,
        flow_name: str,
        pdf_path: Optional[Union[str, Path]] = None,
        pdf_bytes: Optional[bytes] = None,
        pdf_filename: str = "facture.pdf",
        flow_syntax: str = "CII",
        flow_profile: str = "EN16931",
        tracking_id: Optional[str] = None,
        sha256: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Soumet une facture Factur-X à une PDP via l'API AFNOR.

        L'authentification utilise soit le client_uid du JWT (mode stocké),
        soit les afnor_credentials fournis au constructeur (mode zero-trust).

        Args:
            flow_name: Nom du flux (ex: "Facture FAC-2025-001")
            pdf_path: Chemin vers le fichier PDF/A-3 (exclusif avec pdf_bytes)
            pdf_bytes: Contenu PDF en bytes (exclusif avec pdf_path)
            pdf_filename: Nom du fichier pour les bytes (défaut: "facture.pdf")
            flow_syntax: Syntaxe du flux (CII ou UBL)
            flow_profile: Profil Factur-X (MINIMUM, BASIC, EN16931, EXTENDED)
            tracking_id: Identifiant de suivi métier (optionnel)
            sha256: Empreinte SHA-256 du fichier (calculée auto si absent)

        Returns:
            Dict avec flowId, trackingId, status, sha256, etc.

        Raises:
            FactPulseValidationError: Si le PDF n'est pas valide
            FactPulseServiceUnavailableError: Si la PDP est indisponible
            ValueError: Si ni pdf_path ni pdf_bytes n'est fourni

        Example:
            >>> # Avec un chemin de fichier
            >>> result = client.soumettre_facture_afnor(
            ...     flow_name="Facture FAC-2025-001",
            ...     pdf_path="facture.pdf",
            ...     tracking_id="FAC-2025-001",
            ... )
            >>> print(result["flowId"])

            >>> # Avec des bytes (ex: après génération Factur-X)
            >>> result = client.soumettre_facture_afnor(
            ...     flow_name="Facture FAC-2025-001",
            ...     pdf_bytes=pdf_content,
            ...     pdf_filename="FAC-2025-001.pdf",
            ...     tracking_id="FAC-2025-001",
            ... )
        """
        import hashlib

        # Charger le PDF depuis le chemin si fourni
        filename = pdf_filename
        if pdf_path:
            pdf_path = Path(pdf_path)
            pdf_bytes = pdf_path.read_bytes()
            filename = pdf_path.name

        if not pdf_bytes:
            raise ValueError("pdf_path ou pdf_bytes requis")

        # Calculer SHA-256 si non fourni
        if not sha256:
            sha256 = hashlib.sha256(pdf_bytes).hexdigest()

        # Préparer flowInfo
        flow_info = {
            "name": flow_name,
            "flowSyntax": flow_syntax,
            "flowProfile": flow_profile,
            "sha256": sha256,
        }
        if tracking_id:
            flow_info["trackingId"] = tracking_id

        files = {
            "file": (filename, pdf_bytes, "application/pdf"),
            "flowInfo": (None, json_dumps_safe(flow_info), "application/json"),
        }

        response = self._make_afnor_request("POST", "/flow/v1/flows", files=files)
        return response.json()

    def rechercher_flux_afnor(
        self,
        tracking_id: Optional[str] = None,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 25,
    ) -> Dict[str, Any]:
        """Recherche des flux de facturation AFNOR.

        Args:
            tracking_id: Filtrer par trackingId
            status: Filtrer par status (submitted, processing, delivered, etc.)
            offset: Index de début (pagination)
            limit: Nombre max de résultats

        Returns:
            Dict avec flows (liste), total, offset, limit

        Example:
            >>> results = client.rechercher_flux_afnor(tracking_id="FAC-2025-001")
            >>> for flux in results["flows"]:
            ...     print(flux["flowId"], flux["status"])
        """
        search_body = {
            "offset": offset,
            "limit": limit,
            "where": {},
        }
        if tracking_id:
            search_body["where"]["trackingId"] = tracking_id
        if status:
            search_body["where"]["status"] = status

        response = self._make_afnor_request("POST", "/flow/v1/flows/search", json_data=search_body)
        return response.json()

    def telecharger_flux_afnor(self, flow_id: str) -> bytes:
        """Télécharge le fichier PDF d'un flux AFNOR.

        Args:
            flow_id: Identifiant du flux (UUID)

        Returns:
            Contenu du fichier PDF

        Raises:
            FactPulseNotFoundError: Si le flux n'existe pas

        Example:
            >>> pdf_bytes = client.telecharger_flux_afnor("550e8400-e29b-41d4-a716-446655440000")
            >>> with open("facture.pdf", "wb") as f:
            ...     f.write(pdf_bytes)
        """
        response = self._make_afnor_request("GET", f"/flow/v1/flows/{flow_id}")
        return response.content

    def obtenir_facture_entrante_afnor(
        self,
        flow_id: str,
        include_document: bool = False,
    ) -> Dict[str, Any]:
        """Récupère les métadonnées JSON d'un flux entrant (facture fournisseur).

        Télécharge un flux entrant depuis la PDP AFNOR et extrait les métadonnées
        de la facture vers un format JSON unifié. Supporte les formats Factur-X, CII et UBL.

        Note: Cet endpoint utilise l'authentification JWT FactPulse (pas OAuth AFNOR).
        Le serveur FactPulse se charge d'appeler la PDP avec les credentials stockés.

        Args:
            flow_id: Identifiant du flux (UUID)
            include_document: Si True, inclut le document original encodé en base64

        Returns:
            Dict avec les métadonnées de la facture:
                - flow_id: Identifiant du flux
                - format_source: Format détecté (Factur-X, CII, UBL)
                - ref_fournisseur: Numéro de facture fournisseur
                - type_document: Code type (380=facture, 381=avoir, etc.)
                - fournisseur: Dict avec nom, siret, numero_tva_intra
                - site_facturation_nom: Nom du destinataire
                - site_facturation_siret: SIRET du destinataire
                - date_de_piece: Date de la facture (YYYY-MM-DD)
                - date_reglement: Date d'échéance (YYYY-MM-DD)
                - devise: Code devise (EUR, USD, etc.)
                - montant_ht: Montant HT
                - montant_tva: Montant TVA
                - montant_ttc: Montant TTC
                - document_base64: (si include_document=True) Document encodé
                - document_content_type: (si include_document=True) Type MIME
                - document_filename: (si include_document=True) Nom de fichier

        Raises:
            FactPulseNotFoundError: Si le flux n'existe pas
            FactPulseValidationError: Si le format n'est pas supporté

        Example:
            >>> # Récupérer les métadonnées d'une facture entrante
            >>> facture = client.obtenir_facture_entrante_afnor("550e8400-e29b-41d4-a716-446655440000")
            >>> print(f"Fournisseur: {facture['fournisseur']['nom']}")
            >>> print(f"Montant TTC: {facture['montant_ttc']} {facture['devise']}")

            >>> # Avec le document original
            >>> facture = client.obtenir_facture_entrante_afnor(flow_id, include_document=True)
            >>> if facture.get('document_base64'):
            ...     import base64
            ...     pdf_bytes = base64.b64decode(facture['document_base64'])
            ...     with open(facture['document_filename'], 'wb') as f:
            ...         f.write(pdf_bytes)
        """
        from .exceptions import FactPulseNotFoundError, FactPulseServiceUnavailableError, parse_api_error

        self.ensure_authenticated()

        url = f"{self.api_url}/api/v1/afnor/flux-entrants/{flow_id}"
        params = {}
        if include_document:
            params["include_document"] = "true"

        headers = {"Authorization": f"Bearer {self._access_token}"}

        try:
            response = requests.get(url, headers=headers, params=params if params else None, timeout=60)
        except requests.RequestException as e:
            raise FactPulseServiceUnavailableError("FactPulse AFNOR flux-entrants", e)

        if response.status_code >= 400:
            try:
                error_json = response.json()
            except Exception:
                error_json = {"detail": response.text or f"Erreur HTTP {response.status_code}"}
            raise parse_api_error(error_json, response.status_code)

        return response.json()

    def healthcheck_afnor(self) -> Dict[str, Any]:
        """Vérifie la disponibilité du Flow Service AFNOR.

        Returns:
            Dict avec status et service

        Example:
            >>> status = client.healthcheck_afnor()
            >>> print(status["status"])  # "ok"
        """
        response = self._make_afnor_request("GET", "/flow/v1/healthcheck")
        return response.json()

    # =========================================================================
    # Chorus Pro
    # =========================================================================

    def _make_chorus_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> requests.Response:
        """Effectue une requête vers l'API Chorus Pro avec gestion d'auth et d'erreurs.

        Args:
            method: Méthode HTTP (GET, POST, etc.)
            endpoint: Endpoint relatif (ex: /structures/rechercher)
            json_data: Données JSON (optionnel)
            params: Query params (optionnel)

        Returns:
            Response de l'API
        """
        from .exceptions import (
            parse_api_error,
            FactPulseServiceUnavailableError,
        )

        self.ensure_authenticated()
        url = f"{self.api_url}/api/v1/chorus-pro{endpoint}"

        headers = {"Authorization": f"Bearer {self._access_token}"}

        # Ajouter credentials dans le body si mode zero-trust
        if json_data is None:
            json_data = {}
        if self.chorus_credentials:
            json_data["credentials"] = self.chorus_credentials.to_dict()

        try:
            response = requests.request(
                method, url, json=json_data, headers=headers, params=params, timeout=30
            )
        except requests.RequestException as e:
            raise FactPulseServiceUnavailableError("Chorus Pro", e)

        if response.status_code >= 400:
            try:
                error_json = response.json()
            except Exception:
                error_json = {"errorMessage": response.text or f"Erreur HTTP {response.status_code}"}
            raise parse_api_error(error_json, response.status_code)

        return response

    def rechercher_structure_chorus(
        self,
        identifiant_structure: Optional[str] = None,
        raison_sociale: Optional[str] = None,
        type_identifiant: str = "SIRET",
        restreindre_privees: bool = True,
    ) -> Dict[str, Any]:
        """Recherche des structures sur Chorus Pro.

        Args:
            identifiant_structure: SIRET ou SIREN de la structure
            raison_sociale: Raison sociale (recherche partielle)
            type_identifiant: Type d'identifiant (SIRET, SIREN, etc.)
            restreindre_privees: Si True, limite aux structures privées

        Returns:
            Dict avec liste_structures, total, code_retour, libelle

        Example:
            >>> result = client.rechercher_structure_chorus(identifiant_structure="12345678901234")
            >>> for struct in result["liste_structures"]:
            ...     print(struct["id_structure_cpp"], struct["designation_structure"])
        """
        body = {
            "restreindre_structures_privees": restreindre_privees,
        }
        if identifiant_structure:
            body["identifiant_structure"] = identifiant_structure
        if raison_sociale:
            body["raison_sociale_structure"] = raison_sociale
        if type_identifiant:
            body["type_identifiant_structure"] = type_identifiant

        response = self._make_chorus_request("POST", "/structures/rechercher", json_data=body)
        return response.json()

    def consulter_structure_chorus(self, id_structure_cpp: int) -> Dict[str, Any]:
        """Consulte les détails d'une structure Chorus Pro.

        Retourne notamment les paramètres obligatoires pour soumettre une facture :
        - code_service_doit_etre_renseigne
        - numero_ej_doit_etre_renseigne

        Args:
            id_structure_cpp: ID Chorus Pro de la structure

        Returns:
            Dict avec les détails de la structure et ses paramètres

        Example:
            >>> details = client.consulter_structure_chorus(12345)
            >>> if details["parametres"]["code_service_doit_etre_renseigne"]:
            ...     print("Code service obligatoire")
        """
        body = {"id_structure_cpp": id_structure_cpp}
        response = self._make_chorus_request("POST", "/structures/consulter", json_data=body)
        return response.json()

    def obtenir_id_chorus_depuis_siret(
        self,
        siret: str,
        type_identifiant: str = "SIRET",
    ) -> Dict[str, Any]:
        """Obtient l'ID Chorus Pro d'une structure depuis son SIRET.

        Raccourci pratique pour obtenir l'id_structure_cpp avant de soumettre une facture.

        Args:
            siret: Numéro SIRET ou SIREN
            type_identifiant: Type d'identifiant (SIRET ou SIREN)

        Returns:
            Dict avec id_structure_cpp, designation_structure, message

        Example:
            >>> result = client.obtenir_id_chorus_depuis_siret("12345678901234")
            >>> id_cpp = result["id_structure_cpp"]
            >>> if id_cpp > 0:
            ...     print(f"Structure trouvée: {result['designation_structure']}")
        """
        body = {
            "siret": siret,
            "type_identifiant": type_identifiant,
        }
        response = self._make_chorus_request("POST", "/structures/obtenir-id-depuis-siret", json_data=body)
        return response.json()

    def lister_services_structure_chorus(self, id_structure_cpp: int) -> Dict[str, Any]:
        """Liste les services d'une structure Chorus Pro.

        Args:
            id_structure_cpp: ID Chorus Pro de la structure

        Returns:
            Dict avec liste_services, total, code_retour, libelle

        Example:
            >>> services = client.lister_services_structure_chorus(12345)
            >>> for svc in services["liste_services"]:
            ...     if svc["est_actif"]:
            ...         print(svc["code_service"], svc["libelle_service"])
        """
        response = self._make_chorus_request("GET", f"/structures/{id_structure_cpp}/services")
        return response.json()

    def soumettre_facture_chorus(
        self,
        numero_facture: str,
        date_facture: str,
        date_echeance_paiement: str,
        id_structure_cpp: int,
        montant_ht_total: str,
        montant_tva: str,
        montant_ttc_total: str,
        piece_jointe_principale_id: Optional[int] = None,
        piece_jointe_principale_designation: str = "Facture",
        code_service: Optional[str] = None,
        numero_engagement: Optional[str] = None,
        numero_bon_commande: Optional[str] = None,
        numero_marche: Optional[str] = None,
        commentaire: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Soumet une facture à Chorus Pro.

        **Workflow complet** :
        1. Obtenir l'id_structure_cpp via rechercher_structure_chorus()
        2. Vérifier les paramètres obligatoires via consulter_structure_chorus()
        3. Uploader le PDF via l'API /transverses/ajouter-fichier
        4. Soumettre la facture avec cette méthode

        Args:
            numero_facture: Numéro de la facture
            date_facture: Date de la facture (YYYY-MM-DD)
            date_echeance_paiement: Date d'échéance (YYYY-MM-DD)
            id_structure_cpp: ID Chorus Pro du destinataire
            montant_ht_total: Montant HT total (ex: "1000.00")
            montant_tva: Montant TVA (ex: "200.00")
            montant_ttc_total: Montant TTC total (ex: "1200.00")
            piece_jointe_principale_id: ID de la pièce jointe (optionnel)
            piece_jointe_principale_designation: Désignation (défaut: "Facture")
            code_service: Code service (si requis par la structure)
            numero_engagement: Numéro d'engagement (si requis)
            numero_bon_commande: Numéro de bon de commande
            numero_marche: Numéro de marché
            commentaire: Commentaire libre

        Returns:
            Dict avec identifiant_facture_cpp, numero_flux_depot, code_retour, libelle

        Example:
            >>> result = client.soumettre_facture_chorus(
            ...     numero_facture="FAC-2025-001",
            ...     date_facture="2025-01-15",
            ...     date_echeance_paiement="2025-02-15",
            ...     id_structure_cpp=12345,
            ...     montant_ht_total="1000.00",
            ...     montant_tva="200.00",
            ...     montant_ttc_total="1200.00",
            ... )
            >>> print(f"Facture soumise: {result['identifiant_facture_cpp']}")
        """
        body = {
            "numero_facture": numero_facture,
            "date_facture": date_facture,
            "date_echeance_paiement": date_echeance_paiement,
            "id_structure_cpp": id_structure_cpp,
            "montant_ht_total": montant_ht_total,
            "montant_tva": montant_tva,
            "montant_ttc_total": montant_ttc_total,
        }
        if piece_jointe_principale_id:
            body["piece_jointe_principale_id"] = piece_jointe_principale_id
            body["piece_jointe_principale_designation"] = piece_jointe_principale_designation
        if code_service:
            body["code_service"] = code_service
        if numero_engagement:
            body["numero_engagement"] = numero_engagement
        if numero_bon_commande:
            body["numero_bon_commande"] = numero_bon_commande
        if numero_marche:
            body["numero_marche"] = numero_marche
        if commentaire:
            body["commentaire"] = commentaire

        response = self._make_chorus_request("POST", "/factures/soumettre", json_data=body)
        return response.json()

    def consulter_facture_chorus(self, identifiant_facture_cpp: int) -> Dict[str, Any]:
        """Consulte le statut d'une facture Chorus Pro.

        Args:
            identifiant_facture_cpp: ID Chorus Pro de la facture

        Returns:
            Dict avec statut_courant, numero_facture, date_facture, montant_ttc_total, etc.

        Example:
            >>> status = client.consulter_facture_chorus(12345)
            >>> print(f"Statut: {status['statut_courant']['code']}")
        """
        body = {"identifiant_facture_cpp": identifiant_facture_cpp}
        response = self._make_chorus_request("POST", "/factures/consulter", json_data=body)
        return response.json()

    # ==================== AFNOR Directory ====================

    def rechercher_siret_afnor(self, siret: str) -> Dict[str, Any]:
        """Recherche une entreprise par SIRET dans l'annuaire AFNOR.

        Args:
            siret: Numéro SIRET (14 chiffres)

        Returns:
            Dict avec informations entreprise: raison_sociale, adresse, etc.

        Example:
            >>> result = client.rechercher_siret_afnor("12345678901234")
            >>> print(f"Entreprise: {result['raison_sociale']}")
        """
        response = self._make_afnor_request("GET", f"/directory/siret/{siret}")
        return response.json()

    def rechercher_siren_afnor(self, siren: str) -> Dict[str, Any]:
        """Recherche une entreprise par SIREN dans l'annuaire AFNOR.

        Args:
            siren: Numéro SIREN (9 chiffres)

        Returns:
            Dict avec informations entreprise et liste des établissements

        Example:
            >>> result = client.rechercher_siren_afnor("123456789")
            >>> for etab in result.get('etablissements', []):
            ...     print(f"SIRET: {etab['siret']}")
        """
        response = self._make_afnor_request("GET", f"/directory/siren/{siren}")
        return response.json()

    def lister_codes_routage_afnor(self, siren: str) -> List[Dict[str, Any]]:
        """Liste les codes de routage disponibles pour un SIREN.

        Args:
            siren: Numéro SIREN (9 chiffres)

        Returns:
            Liste des codes de routage avec leurs paramètres

        Example:
            >>> codes = client.lister_codes_routage_afnor("123456789")
            >>> for code in codes:
            ...     print(f"Code: {code['code_routage']}")
        """
        response = self._make_afnor_request("GET", f"/directory/siren/{siren}/routing-codes")
        return response.json()

    # ==================== Validation ====================

    def valider_pdf_facturx(
        self,
        pdf_path: Optional[str] = None,
        pdf_bytes: Optional[bytes] = None,
        profil: Optional[str] = None,
        use_verapdf: bool = False,
    ) -> Dict[str, Any]:
        """Valide un PDF Factur-X.

        Args:
            pdf_path: Chemin vers le fichier PDF (exclusif avec pdf_bytes)
            pdf_bytes: Contenu PDF en bytes (exclusif avec pdf_path)
            profil: Profil Factur-X attendu (MINIMUM, BASIC, EN16931, EXTENDED).
                Si None, le profil est auto-détecté depuis le XML embarqué.
            use_verapdf: Active la validation stricte PDF/A avec VeraPDF (défaut: False).
                - False: Validation rapide par métadonnées (~100ms)
                - True: Validation stricte ISO 19005 avec 146+ règles (2-10s, recommandé en production)

        Returns:
            Dict avec:
                - est_conforme (bool): True si le PDF est conforme
                - xml_present (bool): True si XML Factur-X embarqué
                - xml_conforme (bool): True si XML valide selon Schematron
                - profil_detecte (str): Profil détecté (MINIMUM, BASIC, EN16931, EXTENDED)
                - erreurs_xml (list): Erreurs de validation XML
                - pdfa_conforme (bool): True si conforme PDF/A
                - version_pdfa (str): Version PDF/A détectée (ex: "PDF/A-3B")
                - methode_validation_pdfa (str): "metadata" ou "verapdf"
                - erreurs_pdfa (list): Erreurs de conformité PDF/A

        Example:
            >>> # Validation avec auto-détection du profil
            >>> result = client.valider_pdf_facturx("facture.pdf")
            >>> print(f"Profil détecté: {result['profil_detecte']}")

            >>> # Validation stricte avec VeraPDF (recommandé en production)
            >>> result = client.valider_pdf_facturx("facture.pdf", use_verapdf=True)
            >>> if result['est_conforme']:
            ...     print("PDF Factur-X valide!")
            >>> else:
            ...     for err in result.get('erreurs_pdfa', []):
            ...         print(f"Erreur PDF/A: {err}")
        """
        if pdf_path:
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
        if not pdf_bytes:
            raise ValueError("pdf_path ou pdf_bytes requis")

        files = {"fichier_pdf": ("facture.pdf", pdf_bytes, "application/pdf")}
        data: Dict[str, Any] = {"use_verapdf": str(use_verapdf).lower()}
        if profil:
            data["profil"] = profil
        response = self._request("POST", "/traitement/valider-pdf-facturx", files=files, data=data)
        return response.json()

    def valider_signature_pdf(
        self,
        pdf_path: Optional[str] = None,
        pdf_bytes: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """Valide la signature d'un PDF signé.

        Args:
            pdf_path: Chemin vers le fichier PDF signé
            pdf_bytes: Contenu PDF en bytes

        Returns:
            Dict avec: is_signed (bool), signatures (list), etc.

        Example:
            >>> result = client.valider_signature_pdf("facture_signee.pdf")
            >>> if result['is_signed']:
            ...     print("PDF signé!")
            ...     for sig in result.get('signatures', []):
            ...         print(f"Signé par: {sig.get('signer_cn')}")
        """
        if pdf_path:
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
        if not pdf_bytes:
            raise ValueError("pdf_path ou pdf_bytes requis")

        files = {"fichier_pdf": ("document.pdf", pdf_bytes, "application/pdf")}
        response = self._request("POST", "/traitement/valider-signature-pdf", files=files)
        return response.json()

    # ==================== Signature ====================

    def signer_pdf(
        self,
        pdf_path: Optional[str] = None,
        pdf_bytes: Optional[bytes] = None,
        raison: Optional[str] = None,
        localisation: Optional[str] = None,
        contact: Optional[str] = None,
        use_pades_lt: bool = False,
        use_timestamp: bool = True,
        output_path: Optional[str] = None
    ) -> Union[bytes, str]:
        """Signe un PDF avec le certificat configuré côté serveur.

        Le certificat doit être préalablement configuré dans Django Admin
        pour le client identifié par le client_uid du JWT.

        Args:
            pdf_path: Chemin vers le PDF à signer
            pdf_bytes: Contenu PDF en bytes
            raison: Raison de la signature (optionnel)
            localisation: Lieu de signature (optionnel)
            contact: Email de contact (optionnel)
            use_pades_lt: Activer PAdES-B-LT archivage long terme (défaut: False)
            use_timestamp: Activer l'horodatage RFC 3161 (défaut: True)
            output_path: Si fourni, sauvegarde le PDF signé à ce chemin

        Returns:
            bytes du PDF signé, ou chemin si output_path fourni

        Example:
            >>> pdf_signe = client.signer_pdf(
            ...     pdf_path="facture.pdf",
            ...     raison="Conformité Factur-X",
            ...     output_path="facture_signee.pdf"
            ... )
        """
        if pdf_path:
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

        if not pdf_bytes:
            raise ValueError("pdf_path ou pdf_bytes requis")

        files = {
            "fichier_pdf": ("document.pdf", pdf_bytes, "application/pdf"),
        }
        data: Dict[str, Any] = {
            "use_pades_lt": str(use_pades_lt).lower(),
            "use_timestamp": str(use_timestamp).lower(),
        }
        if raison:
            data["raison"] = raison
        if localisation:
            data["localisation"] = localisation
        if contact:
            data["contact"] = contact

        response = self._request("POST", "/traitement/signer-pdf", files=files, data=data)
        result = response.json()

        # L'API retourne du JSON avec pdf_signe_base64
        pdf_signe_b64 = result.get("pdf_signe_base64")
        if not pdf_signe_b64:
            raise FactPulseValidationError("Réponse de signature invalide")

        import base64
        pdf_signe = base64.b64decode(pdf_signe_b64)

        if output_path:
            with open(output_path, "wb") as f:
                f.write(pdf_signe)
            return output_path

        return pdf_signe

    def generer_certificat_test(
        self,
        cn: str = "Test Organisation",
        organisation: str = "Test Organisation",
        email: str = "test@example.com",
        duree_jours: int = 365,
        taille_cle: int = 2048,
    ) -> Dict[str, Any]:
        """Génère un certificat de test pour la signature (NON PRODUCTION).

        Le certificat généré doit ensuite être configuré dans Django Admin.

        Args:
            cn: Common Name du certificat
            organisation: Nom de l'organisation
            email: Email associé au certificat
            duree_jours: Durée de validité en jours (défaut: 365)
            taille_cle: Taille de la clé RSA (2048 ou 4096)

        Returns:
            Dict avec certificat_pem, cle_privee_pem, pkcs12_base64, etc.

        Example:
            >>> result = client.generer_certificat_test(
            ...     cn="Ma Société - Cachet",
            ...     organisation="Ma Société SAS",
            ...     email="contact@masociete.fr",
            ... )
            >>> print(result["certificat_pem"])
        """
        data = {
            "cn": cn,
            "organisation": organisation,
            "email": email,
            "duree_jours": duree_jours,
            "taille_cle": taille_cle,
        }
        response = self._request("POST", "/traitement/generer-certificat-test", json_data=data)
        return response.json()

    # ==================== Workflow complet ====================

    def generer_facturx_complet(
        self,
        facture: Dict[str, Any],
        pdf_source_path: Optional[str] = None,
        pdf_source_bytes: Optional[bytes] = None,
        profil: str = "EN16931",
        valider: bool = True,
        signer: bool = False,
        soumettre_afnor: bool = False,
        afnor_flow_name: Optional[str] = None,
        afnor_tracking_id: Optional[str] = None,
        output_path: Optional[str] = None,
        timeout: int = 120000
    ) -> Dict[str, Any]:
        """Génère un PDF Factur-X complet avec validation, signature et soumission optionnelles.

        Cette méthode enchaîne automatiquement:
        1. Génération du PDF Factur-X
        2. Validation (optionnelle)
        3. Signature (optionnelle, utilise le certificat côté serveur)
        4. Soumission à la PDP AFNOR (optionnelle)

        Note: La signature utilise le certificat configuré dans Django Admin
        pour le client identifié par le client_uid du JWT.

        Args:
            facture: Données de la facture (format FactureFacturX)
            pdf_source_path: Chemin vers le PDF source
            pdf_source_bytes: PDF source en bytes
            profil: Profil Factur-X (MINIMUM, BASIC, EN16931, EXTENDED)
            valider: Si True, valide le PDF généré
            signer: Si True, signe le PDF (certificat côté serveur)
            soumettre_afnor: Si True, soumet le PDF à la PDP AFNOR
            afnor_flow_name: Nom du flux AFNOR (défaut: "Facture {numero_facture}")
            afnor_tracking_id: Tracking ID AFNOR (défaut: numero_facture)
            output_path: Chemin de sortie pour le PDF final
            timeout: Timeout en ms pour le polling

        Returns:
            Dict avec:
                - pdf_bytes: bytes du PDF final
                - pdf_path: chemin si output_path fourni
                - validation: résultat de validation si valider=True
                - signature: infos signature si signer=True
                - afnor: résultat soumission AFNOR si soumettre_afnor=True

        Example:
            >>> result = client.generer_facturx_complet(
            ...     facture=ma_facture,
            ...     pdf_source_path="devis.pdf",
            ...     profil="EN16931",
            ...     valider=True,
            ...     signer=True,
            ...     soumettre_afnor=True,
            ...     output_path="facture_finale.pdf"
            ... )
            >>> if result['validation']['valide']:
            ...     print(f"Facture soumise! Flow ID: {result['afnor']['flowId']}")
        """
        result: Dict[str, Any] = {}

        # 1. Génération
        if pdf_source_path:
            with open(pdf_source_path, "rb") as f:
                pdf_source_bytes = f.read()

        pdf_bytes = self.generer_facturx(
            facture_data=facture,
            pdf_source=pdf_source_bytes,
            profil=profil,
            timeout=timeout
        )
        result["pdf_bytes"] = pdf_bytes

        # 2. Validation
        if valider:
            validation = self.valider_pdf_facturx(pdf_bytes=pdf_bytes, profil=profil)
            result["validation"] = validation
            if not validation.get("est_conforme", False):
                # Retourne quand même le résultat mais avec les erreurs
                if output_path:
                    with open(output_path, "wb") as f:
                        f.write(pdf_bytes)
                    result["pdf_path"] = output_path
                return result

        # 3. Signature (utilise le certificat côté serveur)
        if signer:
            pdf_bytes = self.signer_pdf(pdf_bytes=pdf_bytes)
            result["pdf_bytes"] = pdf_bytes
            result["signature"] = {"signe": True}

        # 4. Soumission AFNOR
        if soumettre_afnor:
            numero_facture = facture.get("numeroFacture", facture.get("numero_facture", "FACTURE"))
            flow_name = afnor_flow_name or f"Facture {numero_facture}"
            tracking_id = afnor_tracking_id or numero_facture

            # Soumission directe avec bytes (plus de fichier temporaire nécessaire)
            afnor_result = self.soumettre_facture_afnor(
                flow_name=flow_name,
                pdf_bytes=pdf_bytes,
                pdf_filename=f"{numero_facture}.pdf",
                tracking_id=tracking_id,
            )
            result["afnor"] = afnor_result

        # Sauvegarde finale
        if output_path:
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)
            result["pdf_path"] = output_path

        return result
