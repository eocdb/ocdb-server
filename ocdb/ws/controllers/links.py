from ocdb.ws.context import WsContext
from ocdb.ws.errors import WsBadRequestError


def get_links(ctx: WsContext) -> dict:
    links = ctx.db_driver.instance().get_links()
    if not links:
        raise WsBadRequestError(f"Could not find links")

    return links.to_dict()


def update_links(ctx: WsContext, content: str) -> dict:
    success = ctx.db_driver.instance().update_links(content)
    if success:
        return get_links(ctx)
    else:
        return {"content": "No links found"}

