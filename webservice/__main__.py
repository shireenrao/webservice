import os
import aiohttp

from aiohttp import web

from gidgethub import routing, sansio
from gidgethub import aiohttp as gh_aiohttp


routes = web.RouteTableDef()

router = routing.Router()


@router.register("issues", action="opened")
async def issue_opened_event(event, gh, *args, **kwargs):
    """ Whenever an issue is opened, greet the author and say thanks."""
    url = event.data["issue"]["comments_url"]
    author = event.data["issue"]["user"]["login"]

    message = f"Thanks for the report @{author}! I will look into it ASAP! (I'm a bot)."
    await gh.post(url, data={"body": message})


@router.register("pull_request", action="closed")
async def pull_request_closed_event(event, gh, *args, **kwargs):
    """ Whenever a pull request is closed, say thank you for the pull request """
    url = event.data["pull_request"]["comments_url"]
    author = event.data["pull_request"]["user"]["login"]

    message = f"Thanks for the contribution @{author}! 🥂"
    await gh.post(url, data={"body": message})


@router.register("pull_request", action="opened")
async def pull_request_opened_event(event, gh, *args, **kwargs):
    """ Whenever a pull request is closed, say thank you for the pull request """
    url = event.data["pull_request"]["issue_url"]
    accept = "application/vnd.github.symmetra-preview+json"

    message = {
        "labels": [
            "pending review"
        ]
    }
    await gh.patch(url, data=message, accept=accept)


@router.register("issue_comment", action="created")
async def issue_comment_created_event(event, gh, *args, **kwargs):
    """ Whenever a issue comment is created react to the user """
    # url = event.data["issue"]["comment"]["url"] + "/reactions"
    # url = event.data["comment"]["url"] + "/reactions"
    # url = event.data["comment"]["html_url"] + "/reactions"
    url = event.data["comment"]["url"] + "/reactions"
    author = event.data["comment"]["user"]["login"]
    # print(f"URL:=====>{url}")
    accept = "application/vnd.github.squirrel-girl-preview"
    message = {
        "content": "heart"
    }
    if author != "shireenrao":
        await gh.post(url, data=message, accept=accept)



@routes.post("/")
async def main(request):
    # read the GitHub webhook payload
    body = await request.read()

    # our authentication token and secret
    secret = os.environ.get("GH_SECRET")
    oauth_token = os.environ.get("GH_AUTH")

    # a representation of GitHub webhook event
    event = sansio.Event.from_http(request.headers, body, secret=secret)

    # instead of mariatta, use your own username
    async with aiohttp.ClientSession() as session:
        gh = gh_aiohttp.GitHubAPI(session, "shireenrao",
                                  oauth_token=oauth_token)

        # call the appropriate callback for the event
        await router.dispatch(event, gh)

    # return a "Success"
    return web.Response(status=200)


if __name__ == "__main__":
    app = web.Application()
    app.add_routes(routes)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)

    web.run_app(app, port=port)