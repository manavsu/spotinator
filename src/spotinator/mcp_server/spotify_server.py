from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("Spotify")

access_token = None

SPOTIFY_TOOL_URL = "http://localhost:8000/spotify/"
SPOTIFY_URL_API = "https://api.spotify.com/v1/"


@mcp.tool()
async def authenticate_user() -> str:
    """Authenticate user by showing the user this login URL and having them navigate to it."""

    LOGIN_URL = SPOTIFY_TOOL_URL + "login_url"
    return requests.get(LOGIN_URL).json()["login_url"]


def queue_track(uri: str) -> str:
    """Queue a song for playback on Spotify.

    Args:
        uri (str): The Spotify URI for the song to queue.

    Raises:
        Exception: If the Spotify API returns an error, this function raises an exception with the error message.

    Returns:
        str: A success message if the track was queued successfully.
    """
    if not access_token:
        raise Exception("Access token is not set. Please authenticate first.")

    response = requests.post(
        SPOTIFY_URL_API + "me/player/queue",
        headers={"Authorization": f"Bearer  {access_token}"},
        params={"uri": uri},
    )
    if response.status_code != 200:
        print(f"Error: {response.text}")
        raise Exception(f"Error: {response.status_code}")
    return "Track queued successfully."


def search_tracks(query: str) -> list[str]:
    """Search for tracks on Spotify with the given query string.

    Args:
        query (str): The search query to use.

    Raises:
        Exception: If the Spotify API returns an error, this function raises an exception with the error message.

    Returns:
        str: A JSON string containing the search results.
    """
    params = {"q": query, "type": "track", "market": "US", "limit": 10}
    response = requests.get(
        SPOTIFY_URL_API + "search",
        headers={"Authorization": f"Bearer {access_token}"},
        params=params,
    ).json()
    if "error" in response:
        print("Error in search_tracks")
        raise Exception(f"Error: {response['error']}")

    result = []
    for item in response["tracks"]["items"]:
        artist = []
        for a in item["artists"]:
            artist.append(a["name"])
        result.append(
            {
                "title": item["name"],
                "artist": str.join(", ", artist),
                "album": item["album"]["name"],
                "uri": item["uri"],
            }
        )
    return result


if __name__ == "__main__":
    mcp.run(port=8001, transport="sse")
