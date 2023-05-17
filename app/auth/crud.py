from app.utils import hasher
from app.utils.generate_random_code import generate_random_code
from . import schemas
from app.prisma import prisma


async def get_user(user_id: str):
    return await prisma.user.find_first(where={
        'id': user_id
    },
    include={
        'verification': True
    })


async def get_user_by_email(email: str):
    return await prisma.user.find_first(where={
        'email': email
    },
    include={
        'verification': True
    })


async def get_user_by_email_password(email: str, password: str):
    user = await prisma.user.find_first(where={
        'email': email,
    },
    include={
        'verification': True
    })

    if user is None or not hasher.verify_password(password, user.password):
        return None
    
    return user



async def create_user(user: schemas.UserSignup) -> dict | None:
    user_exists = await get_user_by_email(user.email) is not None
    if user_exists:
        return None

    created_user = await prisma.user.create(data={
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'password': hasher.get_password_hash(user.password)
    })

    verification = await prisma.verification.create(data={
        'code': generate_random_code(6),
        'user_id': created_user.id,
    })

    return {
        'id': created_user.id,
        'email': created_user.email,
        'first_name': created_user.first_name,
        'last_name': created_user.last_name,
        'verified': verification.verified,
        'verification_code': verification.code
    }


async def verify_user(user_id: str, code: str):
    verification = await prisma.verification.find_first(where={
        'user_id': user_id,
    })
    
    if verification is None:
        return 'no account'

    if verification.code != code:
        return 'wrong code'

    return await prisma.verification.update(data={
        'verified': True,
    },
    where={
        'id': verification.id,
    },
    include={
        'user': True
    })


async def authenticate_user(user: schemas.UserLogin):
    db_user = await get_user_by_email(user.email)
    if db_user is None or not hasher.verify_password(user.password, db_user.password):
        return False
    return True


async def update_user(user: schemas.UserUpdate):
    updated_user = await prisma.user.update(data={
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    },
    where={
        'email': user.email
    },
    include={
        'verification': True
    })

    return updated_user


async def update_user_password(user: schemas.UserUpdatePassword):
    _user = await get_user_by_email_password(user.email, user.previous_password)
    if _user is None:
        return None
    updated_user = await prisma.user.update(data={
        'email': _user.email,
        'password': hasher.get_password_hash(user.new_password)
    },
    where={
        'email': user.email
    },
    include={
        'verification': True
    })

    return updated_user


async def remove_user(user: schemas.UserRemove):
    delete_user = await get_user_by_email_password(user.email, user.password)
    if delete_user is None:
        return False

    deleted_user = await prisma.user.delete(where={
        'id': delete_user.id
    })

    return deleted_user is not None
