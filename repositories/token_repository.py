from datetime import datetime
from models.refresh_token import RefreshToken
from core.security import hash_data, verify_hash

def save_refresh_token(db, user_id, jti, token, expires_at):
    """Save refresh token with hashed JWT and JTI for tracking"""
    token_hash = hash_data(token)  # Hash the JWT before storage
    
    token_obj = RefreshToken(
        user_id=user_id,
        jti=jti,  # Store JTI for uniqueness
        token_hash=token_hash,  # Store hashed token for verification
        expires_at=expires_at
    )
    db.add(token_obj)
    db.commit()
    db.refresh(token_obj)
    return token_obj

def revoke_token(db, jti: str):
    """Revoke token by JTI instead of raw token"""
    token = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
    if token:
        token.revoked_at = datetime.utcnow()
        db.commit()
        return True
    return False

def get_refresh_token(db, token: str):
    """Get refresh token by JTI and verify hash"""
    payload = None
    try:
        from core.security import decode_token
        payload = decode_token(token)
    except Exception:
        return None
    
    if not payload:
        return None
    
    jti = payload.get("jti")
    if not jti:
        return None
    
    # Query by JTI to get the stored token
    token_obj = db.query(RefreshToken).filter(
        RefreshToken.jti == jti,
        RefreshToken.revoked_at == None,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()
    
    if not token_obj:
        return None
    
    # Verify the provided token matches the stored hash
    if not verify_hash(token, token_obj.token_hash):
        return None
    
    return token_obj
