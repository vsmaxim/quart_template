from returns.pointfree import bind_future_result, map_
from returns.pipeline import flow

from yet_another_flask_template.types import QuartResponse

from ..auth import AuthorizedContext, authorized_context
from ..queries import get_categories, update_category_by_id, create_category_returning_id
from ..schemas import CreateItemResponse, ListResponse, NewCategoryRequest, UpdateItemResponse, UpdateCategoryRequest


@authorized_context
def list_categories(ctx: AuthorizedContext) -> QuartResponse:
    return flow(
        get_categories(ctx),
        map_(ListResponse),
    )


@authorized_context
def create_category(ctx: AuthorizedContext) -> QuartResponse:
    return flow(
        ctx.request.get_json_typed(NewCategoryRequest),
        bind_future_result(create_category_returning_id(ctx)), # type: ignore
        map_(CreateItemResponse),
    )


@authorized_context
def update_category(ctx: AuthorizedContext, category_id: int) -> QuartResponse:
    return flow(
        ctx.request.get_json_typed(UpdateCategoryRequest),
        bind_future_result(update_category_by_id(ctx, category_id)),
        map_(UpdateItemResponse),
    )

