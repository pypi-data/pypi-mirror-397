"""
 FactPulse Helpers - Client simplifié avec authentification JWT et polling intégrés.

Ce module fournit :
- FactPulseClient : Client avec auth JWT et polling automatique
- ChorusProCredentials / AFNORCredentials : Dataclasses pour le mode Zero-Trust
- Helpers montants : montant(), montant_total(), ligne_de_poste(), ligne_de_tva()
- Helpers JSON : DecimalEncoder, json_dumps_safe() pour sérialiser Decimal/datetime

Example:
    >>> from factpulse_helpers import (
    ...     FactPulseClient,
    ...     ChorusProCredentials,
    ...     AFNORCredentials,
    ...     montant_total,
    ...     ligne_de_poste,
    ... )
    >>>
    >>> client = FactPulseClient(
    ...     email="user@example.com",
    ...     password="password",
    ...     chorus_credentials=ChorusProCredentials(
    ...         piste_client_id="...",
    ...         piste_client_secret="...",
    ...         chorus_pro_login="...",
    ...         chorus_pro_password="..."
    ...     )
    ... )
"""
from .client import (
    FactPulseClient,
    ChorusProCredentials,
    AFNORCredentials,
    montant,
    montant_total,
    ligne_de_poste,
    ligne_de_tva,
    adresse_postale,
    adresse_electronique,
    fournisseur,
    destinataire,
    # Utilitaires JSON
    DecimalEncoder,
    json_dumps_safe,
)
from .exceptions import (
    FactPulseError,
    FactPulseAuthError,
    FactPulsePollingTimeout,
    FactPulseValidationError,
    FactPulseNotFoundError,
    FactPulseServiceUnavailableError,
    FactPulseAPIError,
    ValidationErrorDetail,
    parse_api_error,
    api_exception_to_validation_error,
)

__all__ = [
    # Client principal
    "FactPulseClient",
    # Credentials
    "ChorusProCredentials",
    "AFNORCredentials",
    # Helpers montants et lignes
    "montant",
    "montant_total",
    "ligne_de_poste",
    "ligne_de_tva",
    # Helpers parties (fournisseur/destinataire)
    "adresse_postale",
    "adresse_electronique",
    "fournisseur",
    "destinataire",
    # Utilitaires JSON (gestion Decimal, datetime, etc.)
    "DecimalEncoder",
    "json_dumps_safe",
    # Exceptions
    "FactPulseError",
    "FactPulseAuthError",
    "FactPulsePollingTimeout",
    "FactPulseValidationError",
    "FactPulseNotFoundError",
    "FactPulseServiceUnavailableError",
    "FactPulseAPIError",
    "ValidationErrorDetail",
    # Helpers pour parser les erreurs API
    "parse_api_error",
    "api_exception_to_validation_error",
]


# Alias pour rétrocompatibilité
def format_montant(value) -> str:
    """Formate un montant pour l'API FactPulse. Alias de montant()."""
    return montant(value)
