from datetime import datetime
from models.refresh_token import RefreshToken

def save_refresh_token(db, user_id, token_hash, expires_at):
    token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token

def revoke_token(db, token_hash):
    token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if token:
        token.revoked_at = datetime.utcnow()
        db.commit()

def get_refresh_token(db, token_hash):
    return db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.revoked_at == None,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()
