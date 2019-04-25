from eocdb.ws.context import WsContext


def get_links(ctx: WsContext):
    fn = ctx.config.get('links')
    with open(fn, 'r') as mdfile:
        s = mdfile.read()
        mdfile.close()
        return s


def update_links(ctx: WsContext, content: str):
    fn = ctx.config.get('links')
    with open(fn, 'w') as mdfile:
        mdfile.write(content)
        return get_links(ctx)

