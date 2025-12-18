# sso_client/webhooks.py (Service Provider - FIXED)

"""
Webhook Handler for Onehux SSO Events - FIXED VERSION
Handles user profile updates, role changes, and Single Logout events from Onehux.

CRITICAL FIX: Updated to work with single-organization role model.

Events:
- user.updated: User profile changed at Onehux
- user.role_updated: User role changed in THIS organization
- user.logout: User logged out at Onehux (trigger SLO)
- user.deleted: User deleted their account
"""

import hmac
import hashlib
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.cache import SessionStore
from django.utils import timezone
import logging
from .models import SSOSession

User = get_user_model()
logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(['POST'])
def onehux_webhook_handler(request):
    """
    Handle webhooks from Onehux Accounts.
    
    Security:
    - Verifies HMAC signature
    - Validates webhook secret
    - Logs all webhook events
    """
    
    # Verify webhook signature
    signature = request.META.get('HTTP_X_ONEHUX_SIGNATURE')
    if not signature:
        logger.warning("Webhook received without signature")
        return HttpResponse("Missing signature", status=401)
    
    # Compute expected signature
    webhook_secret = settings.ONEHUX_SSO['WEBHOOK_SECRET']
    payload = request.body
    
    expected_signature = hmac.new(
        webhook_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        logger.warning("Webhook signature mismatch")
        return HttpResponse("Invalid signature", status=401)
    
    # Parse webhook payload
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        return HttpResponse("Invalid JSON", status=400)
    
    event_type = data.get('event')
    
    logger.info(f"Received webhook: {event_type}")
    
    # Route to appropriate handler
    if event_type == 'user.updated':
        _handle_user_updated(data)
    elif event_type == 'user.role_updated':
        _handle_user_role_updated(data)
    elif event_type == 'user.logout':
        _handle_user_logout(data)
    elif event_type == 'user.deleted':
        _handle_user_deleted(data)
    elif event_type == 'user.created':
        _handle_user_created(data)
    else:
        logger.warning(f"Unknown webhook event type: {event_type}")
    
    return HttpResponse("OK", status=200)



# ============================================================================
# SINGLE LOGOUT HANDLER
# ============================================================================

def _handle_user_logout(data):
    """
    IdP-initiated Single Logout (SLO)

    Handle Single Logout event from Onehux.
    Terminate user's session in this application.
    
    Payload format:
    {
        "event": "user.logout",
        "timestamp": "2024-01-01T00:00:00Z",
        "data": {
            "user_id": "uuid",
            "email": "user@example.com",
            "session_id": "session-uuid"
        }
    }
   
    """
    idp_session_id = data.get('data', {}).get('session_id')

    mapping = SSOSession.objects.filter(
        idp_session_id=idp_session_id
    ).first()

    if not mapping:
        logger.info("Duplicate SLO ignored: %s", idp_session_id)
        return

    django_session_key = mapping.django_session_key

    # 🔥 THIS IS THE CRITICAL LINE
    deleted, _ = Session.objects.filter(
        session_key=django_session_key
    ).delete()

    # Delete Cache session
    store = SessionStore(session_key=django_session_key)
    store.delete()
    

    
    logger.info(
        "✓ SLO OK: idp_session_id=%s django_session=%s deleted=%s",
        idp_session_id,
        django_session_key,
        deleted
    )
    logger.info("✓ Django cache session deleted")

    mapping.delete()





# ============================================================================
# USER PROFILE UPDATE HANDLER
# ============================================================================

def _handle_user_updated(data):
    """
    Handle user profile update from Onehux.
    Syncs user data including role for THIS organization only.
    
    Payload format:
    {
        "event": "user.updated",
        "timestamp": "2024-01-01T00:00:00Z",
        "data": {
            "user_id": "uuid",
            "email": "user@example.com",
            "username": "johndoe",
            "first_name": "John",
            "last_name": "Doe",
            "profile_picture": "https://...",
            "bio": "...",
            "country": "...",
            "region": "...",
            ... other fields
        }
    }
    """
    try:
        user_data = data.get('data', {})
        email = user_data.get('email')
        user_id = user_data.get('user_id')
        
        if not email and not user_id:
            logger.warning("Missing user identifiers in webhook")
            return
        
        # Find local user (prefer onehux_user_id, fallback to email)
        user = None
        if user_id:
            try:
                user = User.objects.get(onehux_user_id=user_id)
            except User.DoesNotExist:
                pass
        
        if not user and email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                pass
        
        if not user:
            logger.warning(f"User not found for sync: email={email}, user_id={user_id}")
            return
        
        # Update user with synced data
        user.update_from_idp(user_data)
        
        logger.info(f"✓ Synced user profile from Onehux: {user.email}")
        
    except Exception as e:
        logger.error(f"Error handling user.updated webhook: {str(e)}", exc_info=True)


# ============================================================================
# USER ROLE UPDATE HANDLER - FIXED FOR SINGLE ORGANIZATION
# ============================================================================

def _handle_user_role_updated(data):
    """
    Handle user role changes from Onehux.
    
    CRITICAL FIX: Updated to work with single-organization model.
    Only updates role if this webhook is for THIS application's organization.
    
    Payload format:
    {
        "event": "user.role_updated",
        "timestamp": "2024-01-01T00:00:00Z",
        "data": {
            "user_id": "uuid",
            "email": "user@example.com",
            "organization_id": "uuid",
            "organization_name": "Acme Corp",
            "new_role": "admin",  # Single role string
            "full_name": "John Doe"
        }
    }
    """
    try:
        user_data = data.get('data', {})
        email = user_data.get('email')
        user_id = user_data.get('user_id')
        new_role = user_data.get('new_role')
        webhook_org_id = user_data.get('organization_id')
        webhook_org_name = user_data.get('organization_name')
        
        if not email and not user_id:
            logger.warning("Missing user identifiers in role update webhook")
            return
        
        if not new_role:
            logger.warning("Missing new_role in role update webhook")
            return
        
        # Find local user
        user = None
        if user_id:
            try:
                user = User.objects.get(onehux_user_id=user_id)
            except User.DoesNotExist:
                pass
        
        if not user and email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                pass
        
        if not user:
            logger.warning(f"User not found for role update: email={email}, user_id={user_id}")
            return
        
        # ====================================================================
        # CRITICAL CHECK: Only update if this is for OUR organization
        # ====================================================================
        
        # Check if this role change is for THIS application's organization
        if webhook_org_id and user.organization_id:
            if str(webhook_org_id) != str(user.organization_id):
                logger.info(
                    f"Ignoring role update for user {user.email}: "
                    f"Webhook is for org {webhook_org_id}, but user is in org {user.organization_id}"
                )
                return
        
        # Update role (single string field)
        old_role = user.role
        user.role = new_role
        
        # Also update organization name if provided
        if webhook_org_name:
            user.organization_name = webhook_org_name
        
        user.save(update_fields=['role', 'organization_name', 'updated_at'])
        
        logger.info(
            f"✓ Updated user role for {user.email}: "
            f"{old_role or 'no-role'} → {new_role} in {user.organization_name}"
        )
        
    except Exception as e:
        logger.error(f"Error handling user.role_updated webhook: {str(e)}", exc_info=True)


# ============================================================================
# USER CREATED HANDLER
# ============================================================================

def _handle_user_created(data):
    """
    Handle new user creation from Onehux.
    
    This is useful when users are created at IdP and need to be
    pre-provisioned at the SP before they login.
    """
    try:
        user_data = data.get('data', {})
        email = user_data.get('email')
        user_id = user_data.get('user_id')
        
        if not email or not user_id:
            logger.warning("Missing user identifiers in user.created webhook")
            return
        
        # Check if user already exists
        if User.objects.filter(onehux_user_id=user_id).exists():
            logger.info(f"User already exists: {email}")
            return
        
        if User.objects.filter(email=email).exists():
            logger.info(f"User with email already exists: {email}")
            return
        
        # Create new user
        username = user_data.get('username') or email.split('@')[0]
        
        # Ensure unique username
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User.objects.create(
            username=username,
            email=email,
            first_name=user_data.get('given_name', ''),
            last_name=user_data.get('family_name', ''),
            is_active=True,
            onehux_user_id=user_id,
        )
        
        # Update with full profile data
        user.update_from_idp(user_data)
        
        logger.info(f"✓ Created new user from webhook: {email}")
        
    except Exception as e:
        logger.error(f"Error handling user.created webhook: {str(e)}", exc_info=True)


# ============================================================================
# USER DELETION HANDLER
# ============================================================================

def _handle_user_deleted(data):
    """
    Handle user account deletion from Onehux.
    
    Options:
    1. Delete user completely (GDPR compliance)
    2. Anonymize user (preserve data relationships)
    
    Current implementation: Anonymize (safer for data integrity)
    """
    try:
        user_data = data.get('data', {})
        email = user_data.get('email')
        user_id = user_data.get('user_id')
        
        if not email and not user_id:
            logger.warning("Missing user identifiers in deletion webhook")
            return
        
        # Find user
        user = None
        if user_id:
            try:
                user = User.objects.get(onehux_user_id=user_id)
            except User.DoesNotExist:
                pass
        
        if not user and email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                pass
        
        if not user:
            logger.warning(f"User not found for deletion: email={email}, user_id={user_id}")
            return
        
        # Option 1: Complete deletion (uncomment if preferred)
        # user.delete()
        # logger.info(f"✓ Deleted user account: {email}")
        
        # Option 2: Anonymize user (default - safer for data integrity)
        user.email = f"deleted_{user.id}@onehux.local"
        user.username = f"deleted_{user.id}"
        user.first_name = "Deleted"
        user.last_name = "User"
        user.is_active = False
        user.profile_picture_url = ""
        user.bio = ""
        user.phone_number = ""
        user.role = ""
        user.organization_id = None
        user.organization_name = ""
        user.onehux_user_id = None
        user.save()
        
        logger.info(f"✓ Anonymized user account: {email}")
        
    except Exception as e:
        logger.error(f"Error handling user.deleted webhook: {str(e)}", exc_info=True)





