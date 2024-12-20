from fastapi import Depends
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from ..config import SECRET, ALGORITHM
# from jose import jwt
from typing import Annotated
from fastapi import HTTPException
from ..db.db import get_async_session, AsyncSession
from ..models.user import User
from ..schemas.token import TokenData
from sqlalchemy.exc import NoResultFound

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/auth/login')

def create_access_token(username: str, 
                        user_id: int, 
                        first_name: str, 
                        last_name: str, 
                        role: str,
                        verify: str,
                        active: str,
                        ava_img: str, 
                        secret: str, 
                        expires_delta: timedelta):
    
    encode = {'sub': username, 
              'id': user_id, 
              'first_name':first_name, 
              'last_name': last_name, 
              'role': role, 
              'verify': verify,
              'active': active,
              'ava_img':ava_img}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, secret, algorithm=ALGORITHM)

def decode_token(token: Annotated[str, Depends(oauth2_bearer)], secret: str, algorithm: str) -> TokenData:
    payload = jwt.decode(token, secret, algorithms=[algorithm])
    username: str = payload.get('sub')
    user_id: int = payload.get('id')
    return TokenData(sub=username, id=user_id)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], session: AsyncSession = Depends(get_async_session)):
    try:
        token_decode: TokenData = decode_token(token, SECRET, ALGORITHM)
        if token_decode.sub is None or token_decode.id is None:
            raise HTTPException(status_code=401, detail='Unauthorized')
        stmt = select(User).where(and_(User.id == token_decode.id, User.username == token_decode.sub, User.is_active == True)).limit(1)
        res = await session.execute(stmt)
        user = res.scalar_one().to_read_model()
        return user
    except:
        raise HTTPException(status_code=401, detail='Unauthorized')
    
async def get_verified_user(token: Annotated[str, Depends(oauth2_bearer)], session: AsyncSession = Depends(get_async_session)):
    try:
        token_decode: TokenData = decode_token(token, SECRET, ALGORITHM)
        if token_decode.sub is None or token_decode.id is None:
            raise HTTPException(status_code=401, detail='Unauthorized')
        stmt = select(User).where(and_(User.id == token_decode.id, User.username == token_decode.sub, User.is_verified == True, User.is_active == True)).limit(1)
        res = await session.execute(stmt)
        user = res.scalar_one().to_read_model()
        return user
    except NoResultFound:
        raise HTTPException(status_code=403, detail='Forbidden')
    except:
        raise HTTPException(status_code=401, detail='Unauthorized')
    

async def get_verify_admin(token: Annotated[str, Depends(oauth2_bearer)], session: AsyncSession = Depends(get_async_session)):
    try:
        token_decode: TokenData = decode_token(token, SECRET, ALGORITHM)
        if token_decode.sub is None or token_decode.id is None:
            raise HTTPException(status_code=401, detail='Unauthorized')
        stmt = select(User).where(and_(User.id == token_decode.id, User.is_active == True, User.role == 'admin')).limit(1)
        res = await session.execute(stmt)
        user = res.scalar_one().to_read_model()
        return user
    except:
        raise HTTPException(status_code=401, detail='Unauthorized')    
