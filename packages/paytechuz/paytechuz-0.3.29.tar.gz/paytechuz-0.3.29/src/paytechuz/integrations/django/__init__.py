"""
Django integration for PayTechUZ.
"""

# Check if Django dependencies are available
try:
    from paytechuz.core.dependencies import check_dependencies
    check_dependencies('django', raise_error=False)
except ImportError:
    pass  # dependencies module not available yet during build

# Register the app configuration
default_app_config = 'paytechuz.integrations.django.apps.PaytechuzConfig'

# This is used to prevent Django from creating new migrations
# when the model changes. Instead, users should use the provided
# migration or create their own if needed.
PAYTECHUZ_PREVENT_MIGRATIONS = True

