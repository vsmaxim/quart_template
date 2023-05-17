from returns.pointfree import bind_future_result, map_
from returns.pipeline import flow

from yet_another_flask_template.types import QuartResponse

from ..auth import AuthorizedContext, authorized_context
from ..queries import create_entry_returning_id, get_entries
from ..schemas import CreateItemResponse, ListResponse, NewEntryRequest


@authorized_context
def create_entry(ctx: AuthorizedContext, category_id: int) -> QuartResponse:
    return flow(
        ctx.request.get_json_typed(NewEntryRequest),
        bind_future_result(create_entry_returning_id(ctx, category_id)),
        map_(CreateItemResponse),
    )


@authorized_context
def list_category_entries(ctx: AuthorizedContext, category_id: int) -> QuartResponse:
    return flow(
        category_id,
        get_entries(ctx),
        map_(ListResponse),
    )

