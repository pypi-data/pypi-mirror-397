"""
AssetPipe License Management

This module handles license key validation for Pro features.
Free tier: Single file conversion, basic validation
Pro tier: Batch processing, watch folders, plugins, all formats
"""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class LicenseTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class License:
    """License information"""
    tier: LicenseTier
    email: str
    key: str
    expires_at: Optional[int] = None  # Unix timestamp
    features: Optional[Dict[str, bool]] = None
    
    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        return not self.is_expired
    
    def has_feature(self, feature: str) -> bool:
        """Check if license includes a feature"""
        if self.tier == LicenseTier.ENTERPRISE:
            return True
        if self.features:
            return self.features.get(feature, False)
        # Default features by tier
        pro_features = {
            "batch_processing",
            "watch_folders", 
            "plugins",
            "fbx_format",
            "priority_support",
            "auto_reports",
        }
        if self.tier == LicenseTier.PRO:
            return feature in pro_features
        return False


# Feature flags for Pro-only commands
PRO_FEATURES = {
    "batch": "batch_processing",
    "watch": "watch_folders",
    "plugins": "plugins",
}


def get_license_path() -> Path:
    """Get path to license file"""
    return Path.home() / ".assetpipe" / "license.json"


def get_current_license() -> License:
    """Get current license or return free tier"""
    license_path = get_license_path()
    
    # Check environment variable first
    env_key = os.environ.get("ASSETPIPE_LICENSE_KEY")
    if env_key:
        license_data = validate_license_key(env_key)
        if license_data:
            return license_data
    
    # Check license file
    if license_path.exists():
        try:
            with open(license_path) as f:
                data = json.load(f)
            license_obj = License(
                tier=LicenseTier(data.get("tier", "free")),
                email=data.get("email", ""),
                key=data.get("key", ""),
                expires_at=data.get("expires_at"),
                features=data.get("features"),
            )
            if license_obj.is_valid:
                return license_obj
        except (json.JSONDecodeError, KeyError, ValueError):
            pass
    
    # Return free tier
    return License(
        tier=LicenseTier.FREE,
        email="",
        key="",
    )


def validate_license_key(key: str) -> Optional[License]:
    """
    Validate a license key.
    
    In production, this would call your license server.
    For now, we use a simple format: TIER-EMAIL_HASH-SIGNATURE
    """
    if not key or len(key) < 10:
        return None
    
    parts = key.split("-")
    if len(parts) < 3:
        return None
    
    tier_code = parts[0].upper()
    
    # Map tier codes
    tier_map = {
        "PRO": LicenseTier.PRO,
        "ENT": LicenseTier.ENTERPRISE,
    }
    
    tier = tier_map.get(tier_code)
    if not tier:
        return None
    
    # In production: verify signature with your server
    # For now, accept any properly formatted key
    return License(
        tier=tier,
        email="licensed@user.com",
        key=key,
        expires_at=None,  # No expiry for now
    )


def activate_license(key: str) -> tuple[bool, str]:
    """
    Activate a license key and save it.
    
    Returns (success, message)
    """
    license_data = validate_license_key(key)
    
    if not license_data:
        return False, "Invalid license key format"
    
    if license_data.is_expired:
        return False, "License key has expired"
    
    # Save license
    license_path = get_license_path()
    license_path.parent.mkdir(exist_ok=True)
    
    with open(license_path, "w") as f:
        json.dump({
            "tier": license_data.tier.value,
            "email": license_data.email,
            "key": license_data.key,
            "expires_at": license_data.expires_at,
            "features": license_data.features,
            "activated_at": int(time.time()),
        }, f, indent=2)
    
    return True, f"License activated: {license_data.tier.value.upper()} tier"


def deactivate_license() -> tuple[bool, str]:
    """Remove current license"""
    license_path = get_license_path()
    
    if license_path.exists():
        license_path.unlink()
        return True, "License deactivated"
    
    return False, "No license found"


def require_pro(feature_name: str = "this feature"):
    """
    Decorator to require Pro license for a function.
    
    Usage:
        @require_pro("batch processing")
        def batch_command():
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            license_data = get_current_license()
            
            if license_data.tier == LicenseTier.FREE:
                from rich.console import Console
                from rich.panel import Panel
                
                console = Console()
                console.print(Panel.fit(
                    f"[yellow]⚡ {feature_name.title()} requires a Pro license[/yellow]\n\n"
                    f"Upgrade to unlock:\n"
                    f"  • Batch processing\n"
                    f"  • Watch folder automation\n"
                    f"  • Custom plugins\n"
                    f"  • Priority support\n\n"
                    f"[dim]Run: assetpipe license activate <KEY>[/dim]\n"
                    f"[dim]Or visit: https://assetpipe.dev/pricing[/dim]",
                    title="🔒 Pro Feature",
                    border_style="yellow",
                ))
                raise SystemExit(0)
            
            return func(*args, **kwargs)
        
        # Preserve function metadata
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    
    return decorator


def check_feature(feature: str) -> bool:
    """Check if current license has a feature"""
    license_data = get_current_license()
    return license_data.has_feature(feature)


def get_license_info() -> Dict[str, Any]:
    """Get current license info for display"""
    license_data = get_current_license()
    
    return {
        "tier": license_data.tier.value,
        "email": license_data.email or "N/A",
        "valid": license_data.is_valid,
        "expires": license_data.expires_at,
        "features": {
            "batch_processing": license_data.has_feature("batch_processing"),
            "watch_folders": license_data.has_feature("watch_folders"),
            "plugins": license_data.has_feature("plugins"),
            "fbx_format": license_data.has_feature("fbx_format"),
        },
    }
