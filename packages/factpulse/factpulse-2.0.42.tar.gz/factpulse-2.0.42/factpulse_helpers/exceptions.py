"""Exceptions personnalisées pour le client FactPulse.

Ce module définit une hiérarchie d'exceptions alignée sur le format d'erreur
de l'API FactPulse (APIError, ValidationErrorDetail) conforme à la norme AFNOR.

Hiérarchie des exceptions:
- FactPulseError (base)
  ├── FactPulseAuthError (401)
  ├── FactPulseValidationError (400, 422) - avec détails structurés
  ├── FactPulsePollingTimeout (timeout polling)
  ├── FactPulseNotFoundError (404)
  ├── FactPulseServiceUnavailableError (503)
  └── FactPulseAPIError (générique avec error_code)
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class FactPulseError(Exception):
    """Classe de base pour toutes les erreurs FactPulse."""
    pass


class FactPulseAuthError(FactPulseError):
    """Erreur d'authentification FactPulse (401).

    Levée quand:
    - Email/mot de passe invalides
    - Token JWT expiré ou invalide
    - client_uid non trouvé
    """
    def __init__(self, message: str = "Authentification requise"):
        self.message = message
        super().__init__(message)


class FactPulsePollingTimeout(FactPulseError):
    """Timeout lors du polling d'une tâche asynchrone."""
    def __init__(self, task_id: str, timeout: int):
        self.task_id = task_id
        self.timeout = timeout
        super().__init__(f"Timeout ({timeout}ms) atteint pour la tâche {task_id}")


@dataclass
class ValidationErrorDetail:
    """Détail d'une erreur de validation au format AFNOR.

    Aligné sur le schéma AcknowledgementDetail de la norme AFNOR XP Z12-013.

    Attributes:
        level: Niveau de gravité ('Error' ou 'Warning')
        item: Identifiant de l'élément concerné (règle BR-FR, champ, XPath)
        reason: Description de l'erreur
        source: Source de l'erreur (schematron, pydantic, pdfa, afnor, chorus_pro)
        code: Code d'erreur unique (ex: SCHEMATRON_BR_FR_01)
    """
    level: str = ""
    item: str = ""
    reason: str = ""
    source: Optional[str] = None
    code: Optional[str] = None

    def __str__(self) -> str:
        item = self.item or "unknown"
        reason = self.reason or "Unknown error"
        source_str = f" [{self.source}]" if self.source else ""
        return f"[{item}]{source_str} {reason}"


class FactPulseValidationError(FactPulseError):
    """Erreur de validation avec détails structurés (400, 422).

    Contient une liste de ValidationErrorDetail pour le diagnostic.

    Attributes:
        errors: Liste des erreurs détaillées
        error_code: Code d'erreur API (ex: VALIDATION_FAILED, SCHEMATRON_VALIDATION_FAILED)
    """
    def __init__(
        self,
        message: str,
        errors: Optional[List[ValidationErrorDetail]] = None,
        error_code: str = "VALIDATION_FAILED",
    ):
        self.errors = errors or []
        self.error_code = error_code
        if self.errors:
            details = "\n".join(f"  - {e}" for e in self.errors)
            message = f"{message}\n\nDétails:\n{details}"
        super().__init__(message)


class FactPulseNotFoundError(FactPulseError):
    """Ressource non trouvée (404).

    Attributes:
        resource: Type de ressource (facture, structure, flux, client)
        identifier: Identifiant de la ressource
    """
    def __init__(self, resource: str, identifier: str = ""):
        self.resource = resource
        self.identifier = identifier
        message = f"{resource.capitalize()} non trouvé(e)"
        if identifier:
            message = f"{resource.capitalize()} '{identifier}' non trouvé(e)"
        super().__init__(message)


class FactPulseServiceUnavailableError(FactPulseError):
    """Service externe indisponible (503).

    Attributes:
        service_name: Nom du service (AFNOR PDP, Chorus Pro, Django)
        original_error: Exception originale (optionnel)
    """
    def __init__(self, service_name: str, original_error: Optional[Exception] = None):
        self.service_name = service_name
        self.original_error = original_error
        message = f"Le service {service_name} est indisponible"
        if original_error:
            message = f"{message}: {str(original_error)}"
        super().__init__(message)


class FactPulseAPIError(FactPulseError):
    """Erreur API générique avec code d'erreur structuré.

    Utilisée pour les erreurs non couvertes par les exceptions spécifiques.

    Attributes:
        status_code: Code HTTP de la réponse
        error_code: Code d'erreur API (ex: INTERNAL_ERROR)
        error_message: Message d'erreur de l'API
        details: Détails optionnels (ValidationErrorDetail)
    """
    def __init__(
        self,
        status_code: int,
        error_code: str,
        error_message: str,
        details: Optional[List[ValidationErrorDetail]] = None,
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.error_message = error_message
        self.details = details or []
        super().__init__(f"[{error_code}] {error_message}")


def parse_api_error(response_json: Dict[str, Any], status_code: int = 400) -> FactPulseError:
    """Parse une réponse d'erreur API et retourne l'exception appropriée.

    Cette fonction parse le format d'erreur unifié de l'API FactPulse
    (APIError avec errorCode, errorMessage, details) et retourne
    l'exception Python appropriée.

    Args:
        response_json: JSON de la réponse d'erreur (dict)
        status_code: Code HTTP de la réponse

    Returns:
        Exception appropriée selon le status_code et error_code

    Example:
        >>> response = requests.post(url, json=data)
        >>> if response.status_code >= 400:
        ...     error = parse_api_error(response.json(), response.status_code)
        ...     raise error
    """
    # Extraire les champs de l'erreur API
    # Support des deux formats : camelCase (API) et snake_case
    error_code = response_json.get("errorCode") or response_json.get("error_code") or "UNKNOWN_ERROR"
    error_message = response_json.get("errorMessage") or response_json.get("error_message") or "Erreur inconnue"
    details_raw = response_json.get("details") or []

    # Parfois l'erreur est dans un wrapper "detail"
    if "detail" in response_json and isinstance(response_json["detail"], dict):
        detail = response_json["detail"]
        error_code = detail.get("error") or detail.get("errorCode") or error_code
        error_message = detail.get("message") or detail.get("errorMessage") or error_message
        details_raw = detail.get("details") or details_raw

    # Parser les détails en ValidationErrorDetail
    details = []
    for d in details_raw:
        if isinstance(d, dict):
            details.append(ValidationErrorDetail(
                level=d.get("level", "Error"),
                item=d.get("item", ""),
                reason=d.get("reason", ""),
                source=d.get("source"),
                code=d.get("code"),
            ))

    # Retourner l'exception appropriée selon le status_code
    if status_code == 401:
        return FactPulseAuthError(error_message)
    elif status_code == 404:
        # Essayer d'extraire la ressource depuis le message
        resource = "ressource"
        if "client" in error_message.lower():
            resource = "client"
        elif "flux" in error_message.lower() or "flow" in error_message.lower():
            resource = "flux"
        elif "facture" in error_message.lower():
            resource = "facture"
        elif "structure" in error_message.lower():
            resource = "structure"
        return FactPulseNotFoundError(resource)
    elif status_code == 503:
        service_name = "API"
        if "afnor" in error_message.lower() or "pdp" in error_message.lower():
            service_name = "AFNOR PDP"
        elif "chorus" in error_message.lower():
            service_name = "Chorus Pro"
        return FactPulseServiceUnavailableError(service_name)
    elif status_code in (400, 422) and details:
        return FactPulseValidationError(error_message, details, error_code)
    else:
        return FactPulseAPIError(status_code, error_code, error_message, details)


def api_exception_to_validation_error(api_exception) -> FactPulseValidationError:
    """Convertit une ApiException du SDK généré en FactPulseValidationError.

    Le SDK openapi-generator génère des exceptions ApiException qui ne sont
    pas très pratiques à utiliser. Cette fonction les convertit en exceptions
    FactPulse avec parsing intelligent des erreurs.

    Args:
        api_exception: Exception ApiException du SDK généré

    Returns:
        FactPulseValidationError avec détails structurés
    """
    import json

    status_code = getattr(api_exception, "status", 400)
    body = getattr(api_exception, "body", "{}")

    try:
        response_json = json.loads(body) if isinstance(body, str) else body
    except (json.JSONDecodeError, TypeError):
        response_json = {"errorMessage": str(api_exception)}

    error = parse_api_error(response_json, status_code)

    # Convertir en FactPulseValidationError si ce n'est pas déjà le cas
    if isinstance(error, FactPulseValidationError):
        return error
    else:
        return FactPulseValidationError(str(error))
