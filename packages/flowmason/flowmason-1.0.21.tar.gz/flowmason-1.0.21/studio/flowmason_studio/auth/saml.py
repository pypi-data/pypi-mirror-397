"""
FlowMason SAML/SSO Integration

Provides SAML 2.0 authentication for enterprise single sign-on.

Supports:
- Service Provider (SP) initiated SSO
- Identity Provider (IdP) initiated SSO
- Just-in-time (JIT) user provisioning
- Attribute mapping for user profiles
- Organization-level SAML configuration
- XML signature verification (requires signxml library)
"""

import base64
import json
import secrets
import xml.etree.ElementTree as ET
import zlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from urllib.parse import urlencode

# Try to import signxml for signature verification
try:
    from signxml import XMLVerifier
    from signxml.exceptions import InvalidSignature
    SIGNXML_AVAILABLE = True
except ImportError:
    SIGNXML_AVAILABLE = False
    XMLVerifier = None
    InvalidSignature = Exception


class SAMLProvider(str, Enum):
    """Known SAML identity providers"""
    OKTA = "okta"
    AZURE_AD = "azure_ad"
    GOOGLE = "google"
    ONELOGIN = "onelogin"
    PING = "ping"
    AUTH0 = "auth0"
    CUSTOM = "custom"


@dataclass
class SAMLConfig:
    """
    SAML configuration for an organization.

    Stores the IdP metadata and SP settings needed for SAML authentication.
    """
    id: str
    org_id: str
    enabled: bool = False

    # Identity Provider settings
    idp_entity_id: str = ""           # IdP Entity ID / Issuer
    idp_sso_url: str = ""             # IdP SSO URL (for SP-initiated login)
    idp_slo_url: Optional[str] = None # IdP SLO URL (for logout)
    idp_certificate: str = ""          # IdP X.509 certificate (PEM format)

    # Known provider type (for UX hints)
    provider_type: SAMLProvider = SAMLProvider.CUSTOM

    # Service Provider settings (auto-generated)
    sp_entity_id: str = ""            # Our SP Entity ID
    sp_acs_url: str = ""              # Assertion Consumer Service URL
    sp_slo_url: Optional[str] = None  # SP SLO URL

    # Attribute mapping
    # Maps IdP attribute names to FlowMason user fields
    attribute_mapping: Dict[str, str] = field(default_factory=lambda: {
        "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
        "name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
        "first_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname",
        "last_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname",
    })

    # User provisioning
    auto_provision_users: bool = True  # Create users on first login
    default_role: str = "developer"    # Default role for new users

    # Security settings
    require_signed_assertions: bool = True
    require_encrypted_assertions: bool = False

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, org_id: str, base_url: str) -> "SAMLConfig":
        """Create a new SAML configuration for an organization"""
        config_id = f"saml_{secrets.token_hex(12)}"
        return cls(
            id=config_id,
            org_id=org_id,
            sp_entity_id=f"{base_url}/saml/metadata/{org_id}",
            sp_acs_url=f"{base_url}/api/v1/auth/saml/acs/{org_id}",
            sp_slo_url=f"{base_url}/api/v1/auth/saml/slo/{org_id}",
        )


@dataclass
class SAMLRequest:
    """SAML authentication request state"""
    id: str
    org_id: str
    relay_state: str
    created_at: datetime
    return_url: Optional[str] = None

    @classmethod
    def create(cls, org_id: str, return_url: Optional[str] = None) -> "SAMLRequest":
        """Create a new SAML request"""
        return cls(
            id=f"_saml_{secrets.token_hex(16)}",
            org_id=org_id,
            relay_state=secrets.token_urlsafe(32),
            created_at=datetime.utcnow(),
            return_url=return_url,
        )

    def is_expired(self, max_age_seconds: int = 300) -> bool:
        """Check if the request has expired"""
        return (datetime.utcnow() - self.created_at).total_seconds() > max_age_seconds


@dataclass
class SAMLAssertion:
    """Parsed SAML assertion data"""
    issuer: str
    subject: str  # NameID (usually email)
    session_index: Optional[str]
    attributes: Dict[str, List[str]]
    not_before: Optional[datetime]
    not_after: Optional[datetime]
    audience: Optional[str]


@dataclass
class SAMLSession:
    """
    Active SAML session for tracking logout.

    Stores the session information needed to perform Single Logout.
    """
    id: str
    user_id: str
    org_id: str
    name_id: str  # The NameID from the assertion
    session_index: Optional[str]  # IdP session index
    idp_entity_id: str
    created_at: datetime
    expires_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        user_id: str,
        org_id: str,
        name_id: str,
        session_index: Optional[str],
        idp_entity_id: str,
        expires_at: Optional[datetime] = None,
    ) -> "SAMLSession":
        """Create a new SAML session"""
        return cls(
            id=f"saml_session_{secrets.token_hex(16)}",
            user_id=user_id,
            org_id=org_id,
            name_id=name_id,
            session_index=session_index,
            idp_entity_id=idp_entity_id,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
        )


@dataclass
class SAMLLogoutRequest:
    """Parsed SAML LogoutRequest data"""
    id: str
    issuer: str
    name_id: str
    session_index: Optional[str]
    destination: Optional[str]
    issue_instant: datetime


class SAMLService:
    """
    SAML Service Provider implementation.

    Handles SAML authentication flow:
    1. Generate AuthnRequest (SP-initiated SSO)
    2. Parse SAML Response/Assertion
    3. Verify XML signatures
    4. Create/update user and session
    """

    def __init__(self):
        """Initialize SAML service"""
        # In-memory storage for pending requests (should use Redis in production)
        self._pending_requests: Dict[str, SAMLRequest] = {}

        # Session storage for Single Logout
        self._saml_sessions: Dict[str, SAMLSession] = {}
        self._user_sessions: Dict[str, List[str]] = {}  # user_id -> [session_ids]
        self._pending_logout_requests: Dict[str, Dict] = {}  # request_id -> metadata

    def verify_signature(
        self,
        xml_string: str,
        idp_certificate: str,
        require_signature: bool = True,
    ) -> tuple[bool, Optional[str]]:
        """
        Verify XML signature on SAML response or assertion.

        Args:
            xml_string: The XML document as a string
            idp_certificate: The IdP's X.509 certificate (PEM format)
            require_signature: If True, fail if no signature is present

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not SIGNXML_AVAILABLE:
            if require_signature:
                return False, "signxml library not installed - cannot verify SAML signatures"
            return True, None

        if not idp_certificate:
            if require_signature:
                return False, "No IdP certificate configured for signature verification"
            return True, None

        try:
            # Parse the XML
            root = ET.fromstring(xml_string)

            # Check if there's a signature to verify
            ns = {'ds': 'http://www.w3.org/2000/09/xmldsig#'}
            signature = root.find('.//ds:Signature', ns)

            if signature is None:
                if require_signature:
                    return False, "SAML response has no signature but signature is required"
                return True, None

            # Clean up certificate (ensure proper PEM format)
            cert = idp_certificate.strip()
            if not cert.startswith('-----BEGIN CERTIFICATE-----'):
                cert = f"-----BEGIN CERTIFICATE-----\n{cert}\n-----END CERTIFICATE-----"

            # Verify the signature
            verifier = XMLVerifier()
            verifier.verify(root, x509_cert=cert)

            return True, None

        except InvalidSignature as e:
            return False, f"Invalid SAML signature: {str(e)}"
        except ET.ParseError as e:
            return False, f"Failed to parse SAML XML: {str(e)}"
        except Exception as e:
            return False, f"Signature verification failed: {str(e)}"

    def verify_assertion_signature(
        self,
        assertion_xml: str,
        idp_certificate: str,
    ) -> tuple[bool, Optional[str]]:
        """
        Verify signature on a SAML assertion specifically.

        Some IdPs sign only the assertion, not the entire response.
        """
        return self.verify_signature(assertion_xml, idp_certificate, require_signature=True)

    def generate_authn_request(
        self,
        config: SAMLConfig,
        return_url: Optional[str] = None,
    ) -> tuple[str, SAMLRequest]:
        """
        Generate a SAML AuthnRequest for SP-initiated SSO.

        Returns:
            Tuple of (redirect_url, saml_request)
        """
        # Create request state
        request = SAMLRequest.create(config.org_id, return_url)

        # Generate AuthnRequest XML
        request_id = request.id
        issue_instant = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        authn_request = f'''<?xml version="1.0" encoding="UTF-8"?>
<samlp:AuthnRequest
    xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
    ID="{request_id}"
    Version="2.0"
    IssueInstant="{issue_instant}"
    Destination="{config.idp_sso_url}"
    AssertionConsumerServiceURL="{config.sp_acs_url}"
    ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST">
    <saml:Issuer>{config.sp_entity_id}</saml:Issuer>
    <samlp:NameIDPolicy
        Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
        AllowCreate="true"/>
</samlp:AuthnRequest>'''

        # Encode request (deflate + base64 for redirect binding)
        compressed = zlib.compress(authn_request.encode('utf-8'))[2:-4]  # Strip zlib header/trailer
        encoded = base64.b64encode(compressed).decode('utf-8')

        # Build redirect URL
        params = {
            'SAMLRequest': encoded,
            'RelayState': request.relay_state,
        }
        redirect_url = f"{config.idp_sso_url}?{urlencode(params)}"

        # Store request for validation
        self._pending_requests[request.relay_state] = request

        return redirect_url, request

    def parse_saml_response(
        self,
        config: SAMLConfig,
        saml_response: str,
        relay_state: str,
    ) -> tuple[SAMLAssertion, SAMLRequest]:
        """
        Parse and validate a SAML Response.

        Args:
            config: SAML configuration
            saml_response: Base64-encoded SAML Response
            relay_state: RelayState from the response

        Returns:
            Tuple of (parsed_assertion, original_request)

        Raises:
            ValueError: If response is invalid, signature is invalid, or expired
        """
        # Validate relay state and retrieve original request
        if relay_state not in self._pending_requests:
            raise ValueError("Invalid RelayState - request not found or expired")

        original_request = self._pending_requests.pop(relay_state)

        if original_request.is_expired():
            raise ValueError("SAML request has expired")

        # Decode response
        try:
            response_xml = base64.b64decode(saml_response).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to decode SAML response: {e}")

        # Verify signature if required
        if config.require_signed_assertions:
            is_valid, error = self.verify_signature(
                response_xml,
                config.idp_certificate,
                require_signature=True,
            )
            if not is_valid:
                raise ValueError(f"SAML signature verification failed: {error}")

        # Parse XML (basic parsing - production should use proper SAML library)
        try:
            root = ET.fromstring(response_xml)
        except ET.ParseError as e:
            raise ValueError(f"Invalid SAML response XML: {e}")

        # Define namespaces
        ns = {
            'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
            'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
        }

        # Check response status
        status = root.find('.//samlp:StatusCode', ns)
        if status is not None:
            status_value = status.get('Value', '')
            if 'Success' not in status_value:
                raise ValueError(f"SAML authentication failed: {status_value}")

        # Extract assertion
        assertion = root.find('.//saml:Assertion', ns)
        if assertion is None:
            raise ValueError("No assertion found in SAML response")

        # Extract issuer
        issuer_elem = assertion.find('saml:Issuer', ns)
        issuer = issuer_elem.text if issuer_elem is not None else ""

        # Validate issuer matches configured IdP
        if issuer != config.idp_entity_id:
            raise ValueError(f"Issuer mismatch: expected {config.idp_entity_id}, got {issuer}")

        # Extract subject (NameID)
        name_id = assertion.find('.//saml:NameID', ns)
        subject = name_id.text if name_id is not None else ""

        if not subject:
            raise ValueError("No NameID found in assertion")

        # Extract session index
        authn_statement = assertion.find('.//saml:AuthnStatement', ns)
        session_index = None
        if authn_statement is not None:
            session_index = authn_statement.get('SessionIndex')

        # Extract conditions
        conditions = assertion.find('.//saml:Conditions', ns)
        not_before = None
        not_after = None
        audience = None

        if conditions is not None:
            not_before_str = conditions.get('NotBefore')
            not_after_str = conditions.get('NotOnOrAfter')

            if not_before_str:
                not_before = datetime.fromisoformat(not_before_str.replace('Z', '+00:00'))
            if not_after_str:
                not_after = datetime.fromisoformat(not_after_str.replace('Z', '+00:00'))

            audience_elem = conditions.find('.//saml:Audience', ns)
            if audience_elem is not None:
                audience = audience_elem.text

        # Validate time conditions
        now = datetime.utcnow()
        if not_before and now < not_before.replace(tzinfo=None):
            raise ValueError("Assertion not yet valid")
        if not_after and now > not_after.replace(tzinfo=None):
            raise ValueError("Assertion has expired")

        # Extract attributes
        attributes: Dict[str, List[str]] = {}
        attr_statement = assertion.find('.//saml:AttributeStatement', ns)

        if attr_statement is not None:
            for attr in attr_statement.findall('saml:Attribute', ns):
                attr_name = attr.get('Name', '')
                values = [v.text for v in attr.findall('saml:AttributeValue', ns) if v.text]
                if attr_name and values:
                    attributes[attr_name] = values

        return SAMLAssertion(
            issuer=issuer,
            subject=subject,
            session_index=session_index,
            attributes=attributes,
            not_before=not_before,
            not_after=not_after,
            audience=audience,
        ), original_request

    def extract_user_info(
        self,
        assertion: SAMLAssertion,
        config: SAMLConfig,
    ) -> Dict[str, str]:
        """
        Extract user information from SAML assertion using attribute mapping.

        Returns:
            Dict with email, name, first_name, last_name, etc.
        """
        user_info = {
            'email': assertion.subject,  # Default to NameID
            'name': assertion.subject,
        }

        # Apply attribute mapping
        for field_name, attr_name in config.attribute_mapping.items():
            if attr_name in assertion.attributes:
                values = assertion.attributes[attr_name]
                if values:
                    user_info[field_name] = values[0]

        # Build full name if we have first/last
        if 'first_name' in user_info and 'last_name' in user_info:
            if 'name' not in config.attribute_mapping:
                user_info['name'] = f"{user_info['first_name']} {user_info['last_name']}"

        return user_info

    def generate_sp_metadata(self, config: SAMLConfig) -> str:
        """
        Generate SAML SP metadata XML.

        This metadata is provided to the IdP for configuration.
        """
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<md:EntityDescriptor
    xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
    entityID="{config.sp_entity_id}">
    <md:SPSSODescriptor
        AuthnRequestsSigned="false"
        WantAssertionsSigned="{str(config.require_signed_assertions).lower()}"
        protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
        <md:NameIDFormat>urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress</md:NameIDFormat>
        <md:AssertionConsumerService
            Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            Location="{config.sp_acs_url}"
            index="0"
            isDefault="true"/>
        {f'<md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="{config.sp_slo_url}"/>' if config.sp_slo_url else ''}
    </md:SPSSODescriptor>
</md:EntityDescriptor>'''

    # ===== Single Logout (SLO) Methods =====

    def create_saml_session(
        self,
        user_id: str,
        org_id: str,
        assertion: SAMLAssertion,
        config: SAMLConfig,
    ) -> SAMLSession:
        """
        Create a SAML session from a successful authentication.

        This session is used for Single Logout to notify the IdP when the user logs out.
        """
        session = SAMLSession.create(
            user_id=user_id,
            org_id=org_id,
            name_id=assertion.subject,
            session_index=assertion.session_index,
            idp_entity_id=assertion.issuer,
            expires_at=assertion.not_after,
        )

        # Store the session
        self._saml_sessions[session.id] = session
        # Also index by user_id for quick lookup during logout
        if user_id not in self._user_sessions:
            self._user_sessions[user_id] = []
        self._user_sessions[user_id].append(session.id)

        return session

    def get_user_saml_sessions(self, user_id: str) -> List[SAMLSession]:
        """Get all SAML sessions for a user"""
        session_ids = self._user_sessions.get(user_id, [])
        sessions = []
        for sid in session_ids:
            session = self._saml_sessions.get(sid)
            if session:
                sessions.append(session)
        return sessions

    def remove_saml_session(self, session_id: str) -> None:
        """Remove a SAML session"""
        session = self._saml_sessions.pop(session_id, None)
        if session and session.user_id in self._user_sessions:
            self._user_sessions[session.user_id] = [
                sid for sid in self._user_sessions[session.user_id]
                if sid != session_id
            ]

    def generate_logout_request(
        self,
        config: SAMLConfig,
        session: SAMLSession,
    ) -> tuple[str, str]:
        """
        Generate a SAML LogoutRequest for SP-initiated logout.

        Args:
            config: SAML configuration
            session: The SAML session to terminate

        Returns:
            Tuple of (redirect_url, request_id)
        """
        if not config.idp_slo_url:
            raise ValueError("IdP SLO URL not configured")

        request_id = f"_logout_{secrets.token_hex(16)}"
        issue_instant = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Build SessionIndex element if available
        session_index_elem = ""
        if session.session_index:
            session_index_elem = f'<samlp:SessionIndex>{session.session_index}</samlp:SessionIndex>'

        logout_request = f'''<?xml version="1.0" encoding="UTF-8"?>
<samlp:LogoutRequest
    xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
    ID="{request_id}"
    Version="2.0"
    IssueInstant="{issue_instant}"
    Destination="{config.idp_slo_url}">
    <saml:Issuer>{config.sp_entity_id}</saml:Issuer>
    <saml:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress">{session.name_id}</saml:NameID>
    {session_index_elem}
</samlp:LogoutRequest>'''

        # Encode request (deflate + base64 for redirect binding)
        compressed = zlib.compress(logout_request.encode('utf-8'))[2:-4]
        encoded = base64.b64encode(compressed).decode('utf-8')

        # Build redirect URL
        relay_state = secrets.token_urlsafe(32)
        params = {
            'SAMLRequest': encoded,
            'RelayState': relay_state,
        }
        redirect_url = f"{config.idp_slo_url}?{urlencode(params)}"

        # Store pending logout request
        self._pending_logout_requests[request_id] = {
            'session_id': session.id,
            'relay_state': relay_state,
            'created_at': datetime.utcnow(),
        }

        return redirect_url, request_id

    def parse_logout_request(
        self,
        config: SAMLConfig,
        saml_request: str,
    ) -> SAMLLogoutRequest:
        """
        Parse a SAML LogoutRequest from the IdP (IdP-initiated logout).

        Args:
            config: SAML configuration
            saml_request: Base64-encoded LogoutRequest

        Returns:
            Parsed LogoutRequest data
        """
        # Decode request
        try:
            # Try base64 + deflate first (redirect binding)
            decoded = base64.b64decode(saml_request)
            try:
                request_xml = zlib.decompress(decoded, -zlib.MAX_WBITS).decode('utf-8')
            except zlib.error:
                # Maybe not compressed (POST binding)
                request_xml = decoded.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to decode LogoutRequest: {e}")

        # Verify signature if configured
        if config.require_signed_assertions:
            is_valid, error = self.verify_signature(
                request_xml,
                config.idp_certificate,
                require_signature=True,
            )
            if not is_valid:
                raise ValueError(f"LogoutRequest signature verification failed: {error}")

        # Parse XML
        try:
            root = ET.fromstring(request_xml)
        except ET.ParseError as e:
            raise ValueError(f"Invalid LogoutRequest XML: {e}")

        # Define namespaces
        ns = {
            'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
            'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
        }

        # Extract fields
        request_id = root.get('ID', '')
        destination = root.get('Destination')
        issue_instant_str = root.get('IssueInstant', '')

        issuer_elem = root.find('saml:Issuer', ns)
        issuer = issuer_elem.text if issuer_elem is not None else ""

        name_id_elem = root.find('saml:NameID', ns)
        name_id = name_id_elem.text if name_id_elem is not None else ""

        session_index_elem = root.find('samlp:SessionIndex', ns)
        session_index = session_index_elem.text if session_index_elem is not None else None

        # Validate issuer
        if issuer != config.idp_entity_id:
            raise ValueError(f"LogoutRequest issuer mismatch: expected {config.idp_entity_id}, got {issuer}")

        # Parse issue instant
        try:
            issue_instant = datetime.fromisoformat(issue_instant_str.replace('Z', '+00:00'))
        except ValueError:
            issue_instant = datetime.utcnow()

        return SAMLLogoutRequest(
            id=request_id,
            issuer=issuer,
            name_id=name_id,
            session_index=session_index,
            destination=destination,
            issue_instant=issue_instant,
        )

    def generate_logout_response(
        self,
        config: SAMLConfig,
        in_response_to: str,
        success: bool = True,
        status_message: Optional[str] = None,
    ) -> str:
        """
        Generate a SAML LogoutResponse.

        Args:
            config: SAML configuration
            in_response_to: The ID of the LogoutRequest we're responding to
            success: Whether logout was successful
            status_message: Optional status message

        Returns:
            Base64-encoded LogoutResponse
        """
        response_id = f"_logout_resp_{secrets.token_hex(16)}"
        issue_instant = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        status_code = "urn:oasis:names:tc:SAML:2.0:status:Success" if success else "urn:oasis:names:tc:SAML:2.0:status:Requester"

        status_message_elem = ""
        if status_message:
            status_message_elem = f'<samlp:StatusMessage>{status_message}</samlp:StatusMessage>'

        logout_response = f'''<?xml version="1.0" encoding="UTF-8"?>
<samlp:LogoutResponse
    xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
    ID="{response_id}"
    Version="2.0"
    IssueInstant="{issue_instant}"
    InResponseTo="{in_response_to}"
    Destination="{config.idp_slo_url}">
    <saml:Issuer>{config.sp_entity_id}</saml:Issuer>
    <samlp:Status>
        <samlp:StatusCode Value="{status_code}"/>
        {status_message_elem}
    </samlp:Status>
</samlp:LogoutResponse>'''

        # Base64 encode for POST binding
        encoded = base64.b64encode(logout_response.encode('utf-8')).decode('utf-8')
        return encoded

    def parse_logout_response(
        self,
        config: SAMLConfig,
        saml_response: str,
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Parse a SAML LogoutResponse from the IdP.

        Args:
            config: SAML configuration
            saml_response: Base64-encoded LogoutResponse

        Returns:
            Tuple of (success, in_response_to, error_message)
        """
        # Decode response
        try:
            decoded = base64.b64decode(saml_response)
            try:
                response_xml = zlib.decompress(decoded, -zlib.MAX_WBITS).decode('utf-8')
            except zlib.error:
                response_xml = decoded.decode('utf-8')
        except Exception as e:
            return False, None, f"Failed to decode LogoutResponse: {e}"

        # Verify signature if configured
        if config.require_signed_assertions:
            is_valid, error = self.verify_signature(
                response_xml,
                config.idp_certificate,
                require_signature=False,  # Logout responses often aren't signed
            )
            if not is_valid:
                return False, None, f"LogoutResponse signature verification failed: {error}"

        # Parse XML
        try:
            root = ET.fromstring(response_xml)
        except ET.ParseError as e:
            return False, None, f"Invalid LogoutResponse XML: {e}"

        ns = {
            'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
            'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
        }

        in_response_to = root.get('InResponseTo')

        # Check status
        status_code = root.find('.//samlp:StatusCode', ns)
        if status_code is not None:
            status_value = status_code.get('Value', '')
            if 'Success' in status_value:
                return True, in_response_to, None
            else:
                status_message_elem = root.find('.//samlp:StatusMessage', ns)
                status_message = status_message_elem.text if status_message_elem is not None else status_value
                return False, in_response_to, f"Logout failed: {status_message}"

        return False, in_response_to, "No status code in LogoutResponse"

    def handle_sp_initiated_logout(
        self,
        user_id: str,
        config: SAMLConfig,
    ) -> Optional[str]:
        """
        Handle SP-initiated logout - generates logout requests for all user's SAML sessions.

        Args:
            user_id: The user logging out
            config: SAML configuration

        Returns:
            Redirect URL to IdP SLO endpoint, or None if no SAML sessions
        """
        sessions = self.get_user_saml_sessions(user_id)
        if not sessions:
            return None

        # For simplicity, logout the first session
        # In production, you might want to handle multiple IdPs
        session = sessions[0]

        try:
            redirect_url, _ = self.generate_logout_request(config, session)
            return redirect_url
        except ValueError:
            # No SLO URL configured, just clean up locally
            for s in sessions:
                self.remove_saml_session(s.id)
            return None

    def handle_idp_initiated_logout(
        self,
        config: SAMLConfig,
        logout_request: SAMLLogoutRequest,
    ) -> tuple[str, List[str]]:
        """
        Handle IdP-initiated logout.

        Args:
            config: SAML configuration
            logout_request: Parsed LogoutRequest

        Returns:
            Tuple of (logout_response, list of terminated session IDs)
        """
        terminated_sessions = []

        # Find and terminate sessions matching the NameID and SessionIndex
        for session_id, session in list(self._saml_sessions.items()):
            if session.name_id == logout_request.name_id:
                if logout_request.session_index is None or session.session_index == logout_request.session_index:
                    self.remove_saml_session(session_id)
                    terminated_sessions.append(session_id)

        # Generate response
        response = self.generate_logout_response(
            config,
            in_response_to=logout_request.id,
            success=True,
        )

        return response, terminated_sessions


# Global SAML service instance
_saml_service: Optional[SAMLService] = None


def get_saml_service() -> SAMLService:
    """Get the global SAML service instance"""
    global _saml_service
    if _saml_service is None:
        _saml_service = SAMLService()
    return _saml_service


class SAMLConfigService:
    """
    Service for managing SAML configurations.

    Handles storage and retrieval of organization SAML settings.
    """

    def __init__(self):
        """Initialize and create tables"""
        self._init_tables()

    def _init_tables(self) -> None:
        """Create SAML config table if it doesn't exist"""
        from ..services.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saml_configs (
                id TEXT PRIMARY KEY,
                org_id TEXT UNIQUE NOT NULL,
                enabled INTEGER DEFAULT 0,
                provider_type TEXT DEFAULT 'custom',
                idp_entity_id TEXT,
                idp_sso_url TEXT,
                idp_slo_url TEXT,
                idp_certificate TEXT,
                sp_entity_id TEXT,
                sp_acs_url TEXT,
                sp_slo_url TEXT,
                attribute_mapping TEXT DEFAULT '{}',
                auto_provision_users INTEGER DEFAULT 1,
                default_role TEXT DEFAULT 'developer',
                require_signed_assertions INTEGER DEFAULT 1,
                require_encrypted_assertions INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (org_id) REFERENCES organizations(id)
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_saml_org ON saml_configs(org_id)")
        conn.commit()

    def get_config(self, org_id: str) -> Optional[SAMLConfig]:
        """Get SAML configuration for an organization"""
        from ..services.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM saml_configs WHERE org_id = ?", (org_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_config(row)

    def save_config(self, config: SAMLConfig) -> SAMLConfig:
        """Save or update SAML configuration"""
        from ..services.database import get_connection

        config.updated_at = datetime.utcnow()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO saml_configs (
                id, org_id, enabled, provider_type, idp_entity_id, idp_sso_url,
                idp_slo_url, idp_certificate, sp_entity_id, sp_acs_url, sp_slo_url,
                attribute_mapping, auto_provision_users, default_role,
                require_signed_assertions, require_encrypted_assertions,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            config.id, config.org_id, config.enabled, config.provider_type.value,
            config.idp_entity_id, config.idp_sso_url, config.idp_slo_url,
            config.idp_certificate, config.sp_entity_id, config.sp_acs_url,
            config.sp_slo_url, json.dumps(config.attribute_mapping),
            config.auto_provision_users, config.default_role,
            config.require_signed_assertions, config.require_encrypted_assertions,
            config.created_at.isoformat(), config.updated_at.isoformat()
        ))
        conn.commit()

        return config

    def delete_config(self, org_id: str) -> bool:
        """Delete SAML configuration for an organization"""
        from ..services.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM saml_configs WHERE org_id = ?", (org_id,))
        conn.commit()

        return cursor.rowcount > 0

    def _row_to_config(self, row) -> SAMLConfig:
        """Convert database row to SAMLConfig"""
        return SAMLConfig(
            id=row[0],
            org_id=row[1],
            enabled=bool(row[2]),
            provider_type=SAMLProvider(row[3]) if row[3] else SAMLProvider.CUSTOM,
            idp_entity_id=row[4] or "",
            idp_sso_url=row[5] or "",
            idp_slo_url=row[6],
            idp_certificate=row[7] or "",
            sp_entity_id=row[8] or "",
            sp_acs_url=row[9] or "",
            sp_slo_url=row[10],
            attribute_mapping=json.loads(row[11]) if row[11] else {},
            auto_provision_users=bool(row[12]),
            default_role=row[13] or "developer",
            require_signed_assertions=bool(row[14]),
            require_encrypted_assertions=bool(row[15]),
            created_at=datetime.fromisoformat(row[16]),
            updated_at=datetime.fromisoformat(row[17]),
        )


# Global config service instance
_saml_config_service: Optional[SAMLConfigService] = None


def get_saml_config_service() -> SAMLConfigService:
    """Get the global SAML config service instance"""
    global _saml_config_service
    if _saml_config_service is None:
        _saml_config_service = SAMLConfigService()
    return _saml_config_service
