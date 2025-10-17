from fastapi import APIRouter, HTTPException, status
from api.pydantic_models.users_pyda_model import UserSchema

router = APIRouter(
    prefix = "/users",
    tags = ["users"],
    responses = {404: {"description" : "User Not Found"}},
)

@router.post(
    "/", 
    response_model = UserSchema, 
    status_code = status.HTTP_201_CREATED
)
async def create_user(user: UserSchema):
    '''
    Create a new user object in the database
    '''
    