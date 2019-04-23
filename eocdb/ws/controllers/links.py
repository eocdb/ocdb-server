from eocdb.ws.context import WsContext


def get_links(ctx: WsContext):
    with open('res/links.md', 'r') as mdfile:
        s = mdfile.read()
        mdfile.close()
        return s


def update_links(ctx: WsContext, content: str):
    with open('res/links.md', 'w') as mdfile:
        mdfile.write(content)
        return get_links(ctx)

