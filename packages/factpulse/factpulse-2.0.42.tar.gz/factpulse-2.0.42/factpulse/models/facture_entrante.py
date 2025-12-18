# coding: utf-8

"""
    API REST FactPulse

     API REST pour la facturation électronique en France : Factur-X, AFNOR PDP/PA, signatures électroniques.  ## 🎯 Fonctionnalités principales  ### 📄 Génération de factures Factur-X - **Formats** : XML seul ou PDF/A-3 avec XML embarqué - **Profils** : MINIMUM, BASIC, EN16931, EXTENDED - **Normes** : EN 16931 (directive UE 2014/55), ISO 19005-3 (PDF/A-3), CII (UN/CEFACT) - **🆕 Format simplifié** : Génération à partir de SIRET + auto-enrichissement (API Chorus Pro + Recherche Entreprises)  ### ✅ Validation et conformité - **Validation XML** : Schematron (45 à 210+ règles selon profil) - **Validation PDF** : PDF/A-3, métadonnées XMP Factur-X, signatures électroniques - **VeraPDF** : Validation stricte PDF/A (146+ règles ISO 19005-3) - **Traitement asynchrone** : Support Celery pour validations lourdes (VeraPDF)  ### 📡 Intégration AFNOR PDP/PA (XP Z12-013) - **Soumission de flux** : Envoi de factures vers Plateformes de Dématérialisation Partenaires - **Recherche de flux** : Consultation des factures soumises - **Téléchargement** : Récupération des PDF/A-3 avec XML - **Directory Service** : Recherche d'entreprises (SIREN/SIRET) - **Multi-client** : Support de plusieurs configs PDP par utilisateur (stored credentials ou zero-storage)  ### ✍️ Signature électronique PDF - **Standards** : PAdES-B-B, PAdES-B-T (horodatage RFC 3161), PAdES-B-LT (archivage long terme) - **Niveaux eIDAS** : SES (auto-signé), AdES (CA commerciale), QES (PSCO) - **Validation** : Vérification intégrité cryptographique et certificats - **Génération de certificats** : Certificats X.509 auto-signés pour tests  ### 🔄 Traitement asynchrone - **Celery** : Génération, validation et signature asynchrones - **Polling** : Suivi d'état via `/taches/{id_tache}/statut` - **Pas de timeout** : Idéal pour gros fichiers ou validations lourdes  ## 🔒 Authentification  Toutes les requêtes nécessitent un **token JWT** dans le header Authorization : ``` Authorization: Bearer YOUR_JWT_TOKEN ```  ### Comment obtenir un token JWT ?  #### 🔑 Méthode 1 : API `/api/token/` (Recommandée)  **URL :** `https://www.factpulse.fr/api/token/`  Cette méthode est **recommandée** pour l'intégration dans vos applications et workflows CI/CD.  **Prérequis :** Avoir défini un mot de passe sur votre compte  **Pour les utilisateurs inscrits via email/password :** - Vous avez déjà un mot de passe, utilisez-le directement  **Pour les utilisateurs inscrits via OAuth (Google/GitHub) :** - Vous devez d'abord définir un mot de passe sur : https://www.factpulse.fr/accounts/password/set/ - Une fois le mot de passe créé, vous pourrez utiliser l'API  **Exemple de requête :** ```bash curl -X POST https://www.factpulse.fr/api/token/ \\   -H \"Content-Type: application/json\" \\   -d '{     \"username\": \"votre_email@example.com\",     \"password\": \"votre_mot_de_passe\"   }' ```  **Paramètre optionnel `client_uid` :**  Pour sélectionner les credentials d'un client spécifique (PA/PDP, Chorus Pro, certificats de signature), ajoutez `client_uid` :  ```bash curl -X POST https://www.factpulse.fr/api/token/ \\   -H \"Content-Type: application/json\" \\   -d '{     \"username\": \"votre_email@example.com\",     \"password\": \"votre_mot_de_passe\",     \"client_uid\": \"550e8400-e29b-41d4-a716-446655440000\"   }' ```  Le `client_uid` sera inclus dans le JWT et permettra à l'API d'utiliser automatiquement : - Les credentials AFNOR/PDP configurés pour ce client - Les credentials Chorus Pro configurés pour ce client - Les certificats de signature électronique configurés pour ce client  **Réponse :** ```json {   \"access\": \"eyJ0eXAiOiJKV1QiLCJhbGc...\",  // Token d'accès (validité: 30 min)   \"refresh\": \"eyJ0eXAiOiJKV1QiLCJhbGc...\"  // Token de rafraîchissement (validité: 7 jours) } ```  **Avantages :** - ✅ Automatisation complète (CI/CD, scripts) - ✅ Gestion programmatique des tokens - ✅ Support du refresh token pour renouveler automatiquement l'accès - ✅ Intégration facile dans n'importe quel langage/outil  #### 🖥️ Méthode 2 : Génération via Dashboard (Alternative)  **URL :** https://www.factpulse.fr/dashboard/  Cette méthode convient pour des tests rapides ou une utilisation occasionnelle via l'interface graphique.  **Fonctionnement :** - Connectez-vous au dashboard - Utilisez les boutons \"Generate Test Token\" ou \"Generate Production Token\" - Fonctionne pour **tous** les utilisateurs (OAuth et email/password), sans nécessiter de mot de passe  **Types de tokens :** - **Token Test** : Validité 24h, quota 1000 appels/jour (gratuit) - **Token Production** : Validité 7 jours, quota selon votre forfait  **Avantages :** - ✅ Rapide pour tester l'API - ✅ Aucun mot de passe requis - ✅ Interface visuelle simple  **Inconvénients :** - ❌ Nécessite une action manuelle - ❌ Pas de refresh token - ❌ Moins adapté pour l'automatisation  ### 📚 Documentation complète  Pour plus d'informations sur l'authentification et l'utilisation de l'API : https://www.factpulse.fr/documentation-api/     

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from factpulse.models.format_facture import FormatFacture
from factpulse.models.fournisseur_entrant import FournisseurEntrant
from factpulse.models.type_document import TypeDocument
from typing import Optional, Set
from typing_extensions import Self

class FactureEntrante(BaseModel):
    """
    Facture reçue d'un fournisseur via PDP/PA.  Ce modèle contient les métadonnées essentielles extraites des factures entrantes, quel que soit leur format source (CII, UBL, Factur-X).  Les montants sont en Decimal en Python mais seront sérialisés en string dans le JSON pour préserver la précision monétaire.
    """ # noqa: E501
    flow_id: Optional[StrictStr] = None
    format_source: FormatFacture = Field(description="Format source de la facture")
    ref_fournisseur: StrictStr = Field(description="Numéro de facture émis par le fournisseur (BT-1)")
    type_document: Optional[TypeDocument] = Field(default=None, description="Type de document (BT-3)")
    fournisseur: FournisseurEntrant = Field(description="Émetteur de la facture (SellerTradeParty)")
    site_facturation_nom: StrictStr = Field(description="Nom du destinataire / votre entreprise (BT-44)")
    site_facturation_siret: Optional[StrictStr] = None
    date_de_piece: StrictStr = Field(description="Date de la facture (BT-2) - YYYY-MM-DD")
    date_reglement: Optional[StrictStr] = None
    devise: Optional[StrictStr] = Field(default='EUR', description="Code devise ISO (BT-5)")
    montant_ht: Annotated[str, Field(strict=True)] = Field(description="Montant HT total (BT-109)")
    montant_tva: Annotated[str, Field(strict=True)] = Field(description="Montant TVA total (BT-110)")
    montant_ttc: Annotated[str, Field(strict=True)] = Field(description="Montant TTC total (BT-112)")
    numero_bon_commande: Optional[StrictStr] = None
    reference_contrat: Optional[StrictStr] = None
    objet_facture: Optional[StrictStr] = None
    document_base64: Optional[StrictStr] = None
    document_content_type: Optional[StrictStr] = None
    document_filename: Optional[StrictStr] = None
    __properties: ClassVar[List[str]] = ["flow_id", "format_source", "ref_fournisseur", "type_document", "fournisseur", "site_facturation_nom", "site_facturation_siret", "date_de_piece", "date_reglement", "devise", "montant_ht", "montant_tva", "montant_ttc", "numero_bon_commande", "reference_contrat", "objet_facture", "document_base64", "document_content_type", "document_filename"]

    @field_validator('montant_ht')
    def montant_ht_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if not re.match(r"^(?!^[-+.]*$)[+-]?0*\d*\.?\d*$", value):
            raise ValueError(r"must validate the regular expression /^(?!^[-+.]*$)[+-]?0*\d*\.?\d*$/")
        return value

    @field_validator('montant_tva')
    def montant_tva_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if not re.match(r"^(?!^[-+.]*$)[+-]?0*\d*\.?\d*$", value):
            raise ValueError(r"must validate the regular expression /^(?!^[-+.]*$)[+-]?0*\d*\.?\d*$/")
        return value

    @field_validator('montant_ttc')
    def montant_ttc_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if not re.match(r"^(?!^[-+.]*$)[+-]?0*\d*\.?\d*$", value):
            raise ValueError(r"must validate the regular expression /^(?!^[-+.]*$)[+-]?0*\d*\.?\d*$/")
        return value

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of FactureEntrante from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of fournisseur
        if self.fournisseur:
            _dict['fournisseur'] = self.fournisseur.to_dict()
        # set to None if flow_id (nullable) is None
        # and model_fields_set contains the field
        if self.flow_id is None and "flow_id" in self.model_fields_set:
            _dict['flow_id'] = None

        # set to None if site_facturation_siret (nullable) is None
        # and model_fields_set contains the field
        if self.site_facturation_siret is None and "site_facturation_siret" in self.model_fields_set:
            _dict['site_facturation_siret'] = None

        # set to None if date_reglement (nullable) is None
        # and model_fields_set contains the field
        if self.date_reglement is None and "date_reglement" in self.model_fields_set:
            _dict['date_reglement'] = None

        # set to None if numero_bon_commande (nullable) is None
        # and model_fields_set contains the field
        if self.numero_bon_commande is None and "numero_bon_commande" in self.model_fields_set:
            _dict['numero_bon_commande'] = None

        # set to None if reference_contrat (nullable) is None
        # and model_fields_set contains the field
        if self.reference_contrat is None and "reference_contrat" in self.model_fields_set:
            _dict['reference_contrat'] = None

        # set to None if objet_facture (nullable) is None
        # and model_fields_set contains the field
        if self.objet_facture is None and "objet_facture" in self.model_fields_set:
            _dict['objet_facture'] = None

        # set to None if document_base64 (nullable) is None
        # and model_fields_set contains the field
        if self.document_base64 is None and "document_base64" in self.model_fields_set:
            _dict['document_base64'] = None

        # set to None if document_content_type (nullable) is None
        # and model_fields_set contains the field
        if self.document_content_type is None and "document_content_type" in self.model_fields_set:
            _dict['document_content_type'] = None

        # set to None if document_filename (nullable) is None
        # and model_fields_set contains the field
        if self.document_filename is None and "document_filename" in self.model_fields_set:
            _dict['document_filename'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of FactureEntrante from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "flow_id": obj.get("flow_id"),
            "format_source": obj.get("format_source"),
            "ref_fournisseur": obj.get("ref_fournisseur"),
            "type_document": obj.get("type_document"),
            "fournisseur": FournisseurEntrant.from_dict(obj["fournisseur"]) if obj.get("fournisseur") is not None else None,
            "site_facturation_nom": obj.get("site_facturation_nom"),
            "site_facturation_siret": obj.get("site_facturation_siret"),
            "date_de_piece": obj.get("date_de_piece"),
            "date_reglement": obj.get("date_reglement"),
            "devise": obj.get("devise") if obj.get("devise") is not None else 'EUR',
            "montant_ht": obj.get("montant_ht"),
            "montant_tva": obj.get("montant_tva"),
            "montant_ttc": obj.get("montant_ttc"),
            "numero_bon_commande": obj.get("numero_bon_commande"),
            "reference_contrat": obj.get("reference_contrat"),
            "objet_facture": obj.get("objet_facture"),
            "document_base64": obj.get("document_base64"),
            "document_content_type": obj.get("document_content_type"),
            "document_filename": obj.get("document_filename")
        })
        return _obj


