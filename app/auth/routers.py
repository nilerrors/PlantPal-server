from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from app.utils.send_email import send_email_async
from . import crud, schemas


router = APIRouter(prefix='/auth')


@router.post('/login')
async def login(user: schemas.UserLogin, Authorize: AuthJWT = Depends()):
    auth_user = await crud.authenticate_user(user)
    if not auth_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Email does not correspond with the password')
    
    db_user = await crud.get_user_by_email(user.email)
    if not db_user or db_user.verification is None or not db_user.verification.verified:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Account is not verified')

    access_token = Authorize.create_access_token(subject=user.email, expires_time=user.expires_time)
    return {'access_token': access_token}


@router.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(background_tasks: BackgroundTasks, user: schemas.UserSignup):
    created_user = await crud.create_user(user)
    if created_user is None:
        raise HTTPException(status.HTTP_409_CONFLICT, f"User with email-address '{user.email}' already exists.")

    background_tasks.add_task(send_email_async,
        'Account Verification',
        user.email,
        {
            'title': 'Verify Account',
            'name': user.first_name,
            'verification_id': created_user['verification_id']
        },
        'verify.html'
    )

    return {'message': f'Verification email sent to {user.email}'}


@router.post('/user/verify/{verification_id}')
async def verify_user(verification_id: str, Authorize: AuthJWT = Depends()):
    verification_added = await crud.verify_user(verification_id)
    if verification_added is None or verification_added.user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No account found with verification id '{verification_id}'")
    
    access_token = Authorize.create_access_token(subject=verification_added.user.email, expires_time=3600)
    return {'access_token': access_token}


@router.post("/user/resend_verification")
async def resend_verification(background_tasks: BackgroundTasks, user: schemas.UserResendVerification):
    db_user = await crud.get_user_by_email(user.email)
    if db_user is None or db_user.verification is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"User with email-address '{user.email}' does not exist")
    
    if db_user.verification is not None and db_user.verification.verified:
        raise HTTPException(status.HTTP_208_ALREADY_REPORTED, f"Account is already verified")
    
    background_tasks.add_task(send_email_async,
        'Account Verification',
        user.email,
        {
            'title': 'Verify Account',
            'name': db_user.first_name,
            'verification_id': db_user.verification.id or ""
        },
        'verify.html'
    )
   
    return {
        'message': f'Verification email sent to {user.email}'
    }


@router.get('/user/current')
async def current_user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    user = Authorize.get_jwt_subject()
    return {'current_user': user}


@router.get('/user', response_model=schemas.UserResponse)
async def user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    user = await crud.get_user_by_email(Authorize.get_jwt_subject())

    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'User does not exist')

    return {
        **user.dict(),
        "verified": True if user.verification is not None and user.verification.verified else False
    }


@router.put('/user', response_model=schemas.UpdatedUserResponse)
async def update_user(user: schemas.UserUpdate, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    user_email = Authorize.get_jwt_subject()
    if user.email != user_email:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Unauthorized to update account')
    updated = await crud.update_user(user)
    if updated is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'User with given email not found')
    
    return {
        "user": updated,
        "access_token": Authorize.create_access_token(subject=updated.email, expires_time=3600)
    }


@router.put('/user/password', response_model=schemas.UpdatedUserResponse)
async def update_user_password(user: schemas.UserUpdatePassword, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    user_email = Authorize.get_jwt_subject()
    if user.email != user_email:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Unauthorized to update account')
    updated = await crud.update_user_password(user)
    if updated is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'User with given email not found')
    
    return {
        "user": updated,
        "access_token": Authorize.create_access_token(subject=updated.email, expires_time=3600)
    }


@router.delete('/user')
async def delete_user(user: schemas.UserRemove, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    user_email = Authorize.get_jwt_subject()
    if user.email != user_email:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Unauthorized to delete account')
    deleted = await crud.remove_user(user)
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Email and password do not correspond')

    return {'message': 'Account deleted'}
