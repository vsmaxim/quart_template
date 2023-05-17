from returns.pointfree import bind_future_result, bind_result, map_
from returns.pipeline import flow
from returns.curry import curry
from returns.result import Result
from returns.future import FutureResult
from returns.functions import tap

from yet_another_flask_template.types import QuartResponse
from yet_another_flask_template.context import app_context, Context
from yet_another_flask_template.errors import HttpException

from ..auth import secure_password, check_password, make_token, set_auth_cookie
from ..queries import create_user, get_user_by_name
from ..schemas import UserSignUpRequest, UserModel, User, UserLoginRequest, UserSignInResponse


@app_context
def sign_up(ctx: Context) -> QuartResponse:
    @curry
    def _prepare_create(user: UserSignUpRequest) -> UserModel:
        return UserModel(
            username=user.username,
            secure_password=secure_password(ctx, user.password),
            email=user.email,
        )

    return flow(
        ctx.request.get_json_typed(UserSignUpRequest),
        map_(_prepare_create),
        bind_future_result(create_user(ctx)),
    )


@app_context
def sign_in(ctx: Context) -> QuartResponse:
    def _get_user_if_valid_pass(req: UserLoginRequest) -> FutureResult[User, HttpException]:
        @curry
        def check_pass(pwd: str, user: User) -> Result[User, HttpException]:
            return check_password(ctx, pwd, user.secure_password).map(lambda _: user)

        return flow(
            get_user_by_name(ctx, req.username),
            bind_result(check_pass(req.password)),
        )

    def set_token(user: User):
        flow(
            user,
            make_token(ctx),
            set_auth_cookie(ctx)
        )

    def make_response(user: User) -> UserSignInResponse:
        return UserSignInResponse(
            user_id=user.id,
            username=user.username,
        )

    return flow(
        ctx.request.get_json_typed(UserLoginRequest),
        bind_future_result(_get_user_if_valid_pass),
        map_(tap(set_token)),
        map_(make_response),
    )

