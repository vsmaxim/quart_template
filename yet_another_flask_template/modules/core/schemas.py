from typing import Sequence
import msgspec


class User(msgspec.Struct):
    id: int
    username: str
    secure_password: str
    email: str


class Category(msgspec.Struct):
    id: int
    image: str
    name: str
    description: str
    parent_id: int | None = None


class NewCategoryRequest(msgspec.Struct):
    image: str
    name: str
    description: str
    parent_id: int | None = None


class Entry(msgspec.Struct):
    id: int
    title: str
    description: str
    keywords: str
    links: str
    category_id: int
    is_deleted: bool


class NewEntryRequest(msgspec.Struct):
    title: str
    description: str
    links: str
    keywords: str



class CreateItemResponse(msgspec.Struct):
    id: int


class UpdateItemResponse(msgspec.Struct):
    id: int


class UpdateCategoryRequest(msgspec.Struct):
    image: str
    name: str
    description: str
    parent_id: int | None


class UserSignUpRequest(msgspec.Struct):
    username: str
    password: str
    email: str


class UserSignUpResponse(msgspec.Struct):
    id: int
    username: str
    email: str


class UserLoginRequest(msgspec.Struct):
    username: str
    password: str


class UserModel(msgspec.Struct):
    username: str
    secure_password: str
    email: str


class UserSignInResponse(msgspec.Struct):
    user_id: int
    username: str


class ListResponse(msgspec.Struct):
    results: Sequence[msgspec.Struct]

