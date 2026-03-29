from mcp.server.fastmcp import FastMCP
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("discord-mcp", stateless_http=True, host="0.0.0.0")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HEADERS = {
    "Authorization": f"Bot {DISCORD_TOKEN}",
    "Content-Type": "application/json"
}

@mcp.tool()
async def send_message(channel_id: str, message: str) -> str:
    """Send a message to a Discord channel."""
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"https://discord.com/api/v10/channels/{channel_id}/messages",
            headers=HEADERS,
            json={"content": message}
        )
        if r.status_code == 200:
            return "Message sent successfully!"
        return f"Failed: {r.text}"

@mcp.tool()
async def get_messages(channel_id: str) -> str:
    """Get last 5 messages from a Discord channel."""
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"https://discord.com/api/v10/channels/{channel_id}/messages",
            headers=HEADERS,
            params={"limit": 5}
        )
        data = r.json()
        results = []
        for msg in data:
            results.append(f"{msg['author']['username']}: {msg['content']}")
        return "\n".join(results) if results else "No messages found."

@mcp.tool()
async def get_server_info(guild_id: str) -> str:
    """Get information about a Discord server."""
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"https://discord.com/api/v10/guilds/{guild_id}",
            headers=HEADERS
        )
        data = r.json()
        return f"Server: {data.get('name')}\nMembers: {data.get('approximate_member_count')}\nDescription: {data.get('description')}"

app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, forwarded_allow_ips="*", proxy_headers=True)