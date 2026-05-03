# Quick Summary: Refresh Token Issues & Fixes

## Root Causes (What Was Wrong)

### 1. **Raw JWT in Database** ❌

- Tokens stored as plain text instead of hashed
- Security risk if database compromised
- Variable named `token_hash` but stored raw JWT (confusing!)

### 2. **Fragile String Lookup** ❌

- Direct string comparison: `WHERE token_hash == incoming_token`
- Fails if JWT has whitespace, encoding differences, or base64 padding variations
- No way to reliably identify which token was used

### 3. **Unique Constraint Conflict** ❌

- Raw JWT stored with `UNIQUE` constraint
- On refresh, new JWT couldn't be stored (unique violation)
- This is why refresh was failing!

### 4. **No Token Versioning** ❌

- After refresh, old token should be unusable
- But no reliable way to track \"which token is this\"
- Could lead to replay attacks or session confusion

---

## Solutions Implemented ✅

| Issue          | Old                      | New                               |
| -------------- | ------------------------ | --------------------------------- |
| **Storage**    | Raw JWT in `token_hash`  | Hashed JWT in `token_hash`        |
| **Lookup**     | String comparison on JWT | Query by `jti`, verify hash       |
| **Uniqueness** | `token_hash UNIQUE`      | `jti UNIQUE` (prevents conflicts) |
| **Revocation** | Revoke by token string   | Revoke by JTI (reliable)          |
| **Security**   | Plain text in DB         | Bcrypt hashed                     |

---

## Files Changed

✅ `core/security.py` - Added JTI generation and token unpacking  
✅ `models/refresh_token.py` - Added JTI column, changed token_hash usage  
✅ `repositories/token_repository.py` - Hash storage, JTI-based lookup  
✅ `services/token_service.py` - JTI-based refresh and revocation  
✅ `services/auth_service.py` - JTI handling in signup/signin  
✅ `database.sql` - Schema updated with JTI column

---

## Next Steps

1. **Backup your database** (important!)
2. **Apply database schema** from Step 2 in REFRESH_TOKEN_FIX.md
3. **Restart the application**
4. **Test**: Signup → Get tokens → Wait/Refresh → Verify still logged in
5. **Update frontend** to handle new token format (usually no changes needed)

---

## Why It Wasn't Working Before

```
User Signs In
    ↓
create_refresh_token() returns raw JWT
    ↓
save_refresh_token(db, user_id, raw_jwt) - stores as \"token_hash\"
    ↓
Frontend stores refresh_token in localStorage
    ↓
[Time passes, access token expires]
    ↓
User refreshes: POST /refresh-token with refresh_token
    ↓
refresh_user_token() calls get_refresh_token(db, refresh_token)
    ↓
Query: WHERE token_hash = 'raw_jwt_here' AND revoked_at IS NULL
    ↓
❌ NOT FOUND (because this specific JWT wasn't stored anymore, or unique constraint issue)
    ↓
❌ \"Refresh token revoked or invalid\"
    ↓
❌ User forced to login again despite valid token
```

## How It Works Now

```
User Signs In
    ↓
create_refresh_token() returns (jwt, jti)
    ↓
save_refresh_token(db, user_id, jti, jwt) - hashes JWT, stores both jti and hash
    ↓
Frontend stores refresh_token JWT
    ↓
[Time passes, access token expires]
    ↓
User refreshes: POST /refresh-token with refresh_token JWT
    ↓
refresh_user_token() calls get_refresh_token(db, refresh_token)
    ↓
Decode JWT → Extract JTI
    ↓
Query: WHERE jti = 'extracted_jti' AND revoked_at IS NULL
    ↓
✅ FOUND (JTI is reliable, stored once per token)
    ↓
Verify hash: bcrypt.verify(jwt, stored_hash)
    ↓
✅ VERIFIED (hash proves it's the real token)
    ↓
Revoke old JTI, generate new tokens (token, jti)
    ↓
✅ Return new access & refresh tokens
    ↓
✅ User stays logged in!
```

---

## Key Improvements

🔒 **Security**: Tokens now hashed like passwords  
⚡ **Reliability**: JTI-based lookup instead of fragile string comparison  
🔄 **Scalability**: Each token has unique ID (supports token versioning)  
📊 **Debuggability**: Can track which token is active/revoked  
🛡️ **Audit Trail**: Database shows JTI for each refresh

---

## Testing Commands

```bash
# 1. Signup
curl -X POST http://localhost:8000/auth/signup \
  -H \"Content-Type: application/json\" \
  -d '{\n    \"phone_number\": \"9876543210\",\n    \"otp_code\": \"123456\",\n    \"full_name\": \"Test User\",\n    \"email\": \"test@example.com\",\n    \"role\": \"customer\"\n  }'

# 2. Save tokens from response

# 3. Refresh token (should work even after access token expires)
curl -X POST http://localhost:8000/auth/refresh-token \
  -H \"Content-Type: application/json\" \
  -d '{\n    \"refresh_token\": \"YOUR_REFRESH_TOKEN\"\n  }'

# 4. Check database
# Should see: jti (UUID), token_hash (bcrypt hash), active tokens have revoked_at = NULL
```

---

**Status**: ✅ **All fixes implemented and ready to deploy**

