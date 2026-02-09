import discord
from datetime import datetime
from io import BytesIO
from typing import List, Tuple


class TranscriptGenerator:
    """Generate beautiful HTML transcripts for tickets"""
    
    @staticmethod
    async def generate_transcript(
        channel: discord.TextChannel,
        ticket_owner: discord.User,
        panel_name: str,
        server_logo_url: str = None
    ) -> Tuple[bytes, List[discord.User]]:
        """
        Generate HTML transcript of ticket channel
        Returns: (html_bytes, list_of_users_in_transcript)
        """
        
        messages = []
        users_in_transcript = set()
        
        # Fetch all messages
        async for message in channel.history(limit=None, oldest_first=True):
            messages.append(message)
            users_in_transcript.add(message.author)
        
        # Start building HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ticket Transcript: #{channel.name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            background: #36393f;
            color: #dcddde;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: #2f3136;
            border-left: 4px solid #5865f2;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 4px;
        }}
        
        .header-title {{
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 15px;
        }}
        
        .header-info {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            font-size: 14px;
        }}
        
        .header-field {{
            background: #36393f;
            padding: 10px;
            border-radius: 4px;
        }}
        
        .header-label {{
            color: #72767d;
            font-weight: bold;
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        
        .header-value {{
            color: #dcddde;
        }}
        
        .users-section {{
            background: #2f3136;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }}
        
        .users-title {{
            color: #ffffff;
            font-weight: bold;
            margin-bottom: 10px;
            font-size: 14px;
            text-transform: uppercase;
        }}
        
        .user-item {{
            display: flex;
            align-items: center;
            padding: 8px;
            margin-bottom: 8px;
            background: #36393f;
            border-radius: 4px;
        }}
        
        .user-avatar {{
            width: 32px;
            height: 32px;
            border-radius: 50%;
            margin-right: 10px;
        }}
        
        .user-info {{
            display: flex;
            flex-direction: column;
        }}
        
        .user-name {{
            color: #ffffff;
            font-weight: bold;
        }}
        
        .user-tag {{
            color: #72767d;
            font-size: 12px;
        }}
        
        .messages {{
            background: #36393f;
            border-radius: 4px;
            overflow: hidden;
        }}
        
        .message {{
            padding: 15px;
            border-bottom: 1px solid #2f3136;
            display: flex;
            gap: 10px;
        }}
        
        .message:last-child {{
            border-bottom: none;
        }}
        
        .message-author-avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            flex-shrink: 0;
        }}
        
        .message-content {{
            flex: 1;
        }}
        
        .message-header {{
            display: flex;
            align-items: baseline;
            gap: 10px;
            margin-bottom: 5px;
        }}
        
        .message-author {{
            color: #ffffff;
            font-weight: 500;
        }}
        
        .message-timestamp {{
            color: #72767d;
            font-size: 12px;
        }}
        
        .message-text {{
            color: #dcddde;
            word-wrap: break-word;
            white-space: pre-wrap;
        }}
        
        .message-embed {{
            background: #2f3136;
            border-left: 4px solid #5865f2;
            padding: 12px;
            margin-top: 10px;
            border-radius: 4px;
        }}
        
        .embed-title {{
            color: #ffffff;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .embed-description {{
            color: #dcddde;
            font-size: 14px;
        }}
        
        .message-image {{
            max-width: 100%;
            max-height: 300px;
            margin-top: 10px;
            border-radius: 4px;
        }}
        
        .message-attachment {{
            background: #2f3136;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
            display: inline-block;
        }}
        
        .message-attachment a {{
            color: #5865f2;
            text-decoration: none;
        }}
        
        .message-attachment a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-title">📑 Ticket Transcript: #{channel.name}</div>
            <div class="header-info">
                <div class="header-field">
                    <div class="header-label">Ticket Owner</div>
                    <div class="header-value">{ticket_owner.mention} ({ticket_owner.name}#{ticket_owner.discriminator})</div>
                </div>
                <div class="header-field">
                    <div class="header-label">Panel Name</div>
                    <div class="header-value">{panel_name}</div>
                </div>
                <div class="header-field">
                    <div class="header-label">Channel Name</div>
                    <div class="header-value">{channel.name}</div>
                </div>
                <div class="header-field">
                    <div class="header-label">Created At</div>
                    <div class="header-value">{channel.created_at.strftime('%Y-%m-%d %H:%M:%S')}</div>
                </div>
            </div>
        </div>
        
        <div class="users-section">
            <div class="users-title">Users in Transcript ({len(users_in_transcript)})</div>
            {TranscriptGenerator._build_users_html(users_in_transcript)}
        </div>
        
        <div class="messages">
            {await TranscriptGenerator._build_messages_html(messages)}
        </div>
    </div>
</body>
</html>
"""
        
        return html.encode(), list(users_in_transcript)
    
    @staticmethod
    def _build_users_html(users: set) -> str:
        """Build HTML for users list"""
        html = ""
        for user in sorted(users, key=lambda u: u.name):
            html += f"""
            <div class="user-item">
                <img class="user-avatar" src="{user.display_avatar.url}" alt="{user.name}">
                <div class="user-info">
                    <div class="user-name">{user.name}</div>
                    <div class="user-tag">@{user.name}#{user.discriminator}</div>
                </div>
            </div>
            """
        return html
    
    @staticmethod
    async def _build_messages_html(messages: List[discord.Message]) -> str:
        """Build HTML for messages"""
        html = ""
        for message in messages:
            timestamp = message.created_at.strftime("%H:%M:%S")
            
            # Message content
            content = message.content or ""
            
            html += f"""
            <div class="message">
                <img class="message-author-avatar" src="{message.author.display_avatar.url}" alt="{message.author.name}">
                <div class="message-content">
                    <div class="message-header">
                        <span class="message-author">{message.author.name}</span>
                        <span class="message-timestamp">{timestamp}</span>
                    </div>
                    <div class="message-text">{content}</div>
            """
            
            # Embeds
            for embed in message.embeds:
                embed_html = """<div class="message-embed">"""
                if embed.title:
                    embed_html += f"""<div class="embed-title">{embed.title}</div>"""
                if embed.description:
                    embed_html += f"""<div class="embed-description">{embed.description}</div>"""
                embed_html += """</div>"""
                html += embed_html
            
            # Attachments/Images
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith('image'):
                    html += f"""<img class="message-image" src="{attachment.url}" alt="image">"""
                else:
                    html += f"""<div class="message-attachment"><a href="{attachment.url}">📎 {attachment.filename}</a></div>"""
            
            html += """
                </div>
            </div>
            """
        
        return html