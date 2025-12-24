"""
Custom Python UBL (Universal Business Language) Library

A pure Python library for generating and parsing UBL 2.1 XML documents
with full PEPPOL BIS Billing 3.0 compliance.

Designed for eventual PyPI publication.
"""

from .__version__ import __version__
from .models import (
    Amount,
    BaseElement,
    BaseXMLNS,
    CacMixin,
    CbcMixin,
    Code,
    FromXMLMixin,
    Identifier,
    Quantity,
    ToXMLMixin,
    UblMixin,
)

__all__ = [
    "__version__",
    # Basic components
    "Amount",
    "Code",
    "Identifier",
    "Quantity",
    # Base classes and mixins
    "BaseElement",
    "BaseXMLNS",
    "CacMixin",
    "CbcMixin",
    "FromXMLMixin",
    "ToXMLMixin",
    "UblMixin",
]
