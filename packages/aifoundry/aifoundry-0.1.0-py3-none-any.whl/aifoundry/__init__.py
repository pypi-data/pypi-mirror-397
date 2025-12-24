"""
AI Foundry: Enterprise AI implementation tools.
"""

__version__ = "0.1.0"
__author__ = "AI Foundry Team"

# Don't try to import AuditLogger if it doesn't exist
# Only import what we know exists
try:
    from aifoundry.compliance.pii_detector import PIIDetector
    PIIDetector_available = True
except ImportError:
    PIIDetector_available = False

try:
    from aifoundry.core import ComplianceAwareRAG
    ComplianceAwareRAG_available = True
except ImportError:
    ComplianceAwareRAG_available = False

# Build __all__ based on what's available
__all__ = []
if PIIDetector_available:
    __all__.append("PIIDetector")
if ComplianceAwareRAG_available:
    __all__.append("ComplianceAwareRAG")
