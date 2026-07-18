"JWT Authrization Moudle"
import os
from datetime import datetime,timedelta
from jose import JWTError,jwt
from passlib.context import CryptContext
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from dotenv import load_dotenv
from fastapi import Depends,HTTPException

load_dotenv()
SECRET_KEY=os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY未在.env中进行配置")
ALGORITHM='HS256'
ACCESS_TOKEN_EXPIRE_MINUTES=60


pwd_context=CryptContext(schemes=['bcrypt'],deprecated='auto')
security=HTTPBearer()

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain,hashed):
    return pwd_context.verify(plain,hashed)

def create_access_token(emp_id):
    expire=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload={
        'sub':str(emp_id),
        'exp':expire,
        'iat':datetime.utcnow(),
    }

    return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)

def verify_token(token):

    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        emp_id=payload.get('sub')
        if emp_id is None:
            return None
        return int(emp_id)

    except JWTError:
        return None

async def get_current_emp(credentials:HTTPAuthorizationCredentials=Depends(security)):

    emp_id=verify_token(credentials.credentials)
    if emp_id is None:
        raise HTTPException(status_code=401,detail='无效或者过期的token')
    return emp_id