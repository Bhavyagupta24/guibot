import discord
from datetime import datetime
from io import BytesIO
from typing import List, Tuple
import re
import html as html_module


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
        Generate HTML transcript of ticket channel with enhanced visuals and message details
        Returns: (html_bytes, list_of_users_in_transcript)
        """
        
        messages = []
        users_in_transcript = set()
        
        # Fetch all messages
        async for message in channel.history(limit=None, oldest_first=True):
            messages.append(message)
            users_in_transcript.add(message.author)
        
        # Calculate statistics
        message_count = len(messages)
        user_messages = {}
        for msg in messages:
            user_messages[msg.author] = user_messages.get(msg.author, 0) + 1
        
        # Start building HTML with enhanced styles
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ticket Transcript: #{channel.name}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/atom-one-dark.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
            color: #dcddde;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", sans-serif;
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2f3136 0%, #36393f 100%);
            border-left: 6px solid #7B5BE8;
            padding: 25px;
            margin-bottom: 25px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }}
        
        .header-title {{
            font-size: 28px;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 20px;
        }}
        
        .header-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            font-size: 14px;
        }}
        
        .header-field {{
            background: rgba(0, 0, 0, 0.2);
            padding: 12px 15px;
            border-radius: 6px;
            border-left: 3px solid #7B5BE8;
        }}
        
        .header-label {{
            color: #b5bac1;
            font-weight: 700;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }}
        
        .header-value {{
            color: #ffffff;
            font-weight: 500;
        }}
        
        .stats-dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }}
        
        .stat-box {{
            background: linear-gradient(135deg, #2f3136 0%, #36393f 100%);
            padding: 18px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid rgba(88, 101, 242, 0.2);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }}
        
        .stat-number {{
            font-size: 28px;
            font-weight: 800;
            color: #7B5BE8;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #b5bac1;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .users-section {{
            background: linear-gradient(135deg, #2f3136 0%, #36393f 100%);
            padding: 20px;
            margin-bottom: 25px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }}
        
        .users-title {{
            color: #ffffff;
            font-weight: 700;
            margin-bottom: 15px;
            font-size: 16px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .users-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 12px;
        }}
        
        .user-item {{
            display: flex;
            align-items: center;
            padding: 12px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 6px;
            border: 1px solid rgba(88, 101, 242, 0.1);
            transition: all 0.3s ease;
        }}
        
        .user-item:hover {{
            background: rgba(88, 101, 242, 0.1);
            border-color: rgba(88, 101, 242, 0.3);
        }}
        
        .user-avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-right: 12px;
            border: 2px solid #7B5BE8;
        }}
        
        .user-info {{
            display: flex;
            flex-direction: column;
            flex: 1;
        }}
        
        .user-name {{
            color: #ffffff;
            font-weight: 600;
            font-size: 14px;
        }}
        
        .user-tag {{
            color: #72767d;
            font-size: 12px;
        }}
        
        .messages {{
            background: #2a2a3e;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }}
        
        .message {{
            padding: 15px;
            border-bottom: 1px solid rgba(88, 101, 242, 0.1);
            display: flex;
            gap: 12px;
            transition: all 0.2s ease;
        }}
        
        .message:hover {{
            background: rgba(88, 101, 242, 0.05);
        }}
        
        .message:last-child {{
            border-bottom: none;
        }}
        
        .message-author-avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            flex-shrink: 0;
            border: 2px solid #7B5BE8;
        }}
        
        .message-content {{
            flex: 1;
            min-width: 0;
        }}
        
        .message-header {{
            display: flex;
            align-items: baseline;
            gap: 10px;
            margin-bottom: 8px;
            flex-wrap: wrap;
        }}
        
        .message-author {{
            color: #ffffff;
            font-weight: 600;
            font-size: 15px;
        }}
        
        .message-timestamp {{
            color: #72767d;
            font-size: 12px;
            margin-left: auto;
        }}
        
        .message-text {{
            color: #dcddde;
            word-wrap: break-word;
            white-space: pre-wrap;
            font-size: 14px;
            line-height: 1.5;
            margin-bottom: 10px;
        }}
        
        .message-mention {{
            background: rgba(88, 101, 242, 0.3);
            color: #7289da;
            padding: 2px 6px;
            border-radius: 3px;
            font-weight: 600;
            white-space: nowrap;
            display: inline-block;
        }}
        
        .message-code {{
            background: #1e1e2e;
            border-left: 3px solid #7B5BE8;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            margin: 10px 0;
        }}
        
        .message-code code {{
            font-family: "Courier New", monospace;
            font-size: 13px;
            color: #dcddde;
        }}
        
        .message-attachments {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-top: 10px;
        }}
        
        .message-image {{
            max-width: 100%;
            max-height: 400px;
            border-radius: 6px;
            border: 2px solid rgba(88, 101, 242, 0.2);
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .message-image:hover {{
            border-color: #7B5BE8;
            box-shadow: 0 0 15px rgba(123, 91, 232, 0.3);
        }}
        
        .message-attachment {{
            background: rgba(123, 91, 232, 0.1);
            padding: 12px 15px;
            border-radius: 6px;
            border-left: 3px solid #7B5BE8;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            max-width: 100%;
        }}
        
        .message-attachment a {{
            color: #7B5BE8;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.2s ease;
            word-break: break-word;
        }}
        
        .message-attachment a:hover {{
            color: #7289da;
            text-decoration: underline;
        }}
        
        .message-embed {{
            background: rgba(123, 91, 232, 0.1);
            border-left: 4px solid #7B5BE8;
            padding: 15px;
            margin-top: 10px;
            border-radius: 6px;
            display: grid;
            gap: 10px;
        }}
        
        .embed-title {{
            color: #ffffff;
            font-weight: 700;
            font-size: 15px;
        }}
        
        .embed-description {{
            color: #dcddde;
            font-size: 14px;
            line-height: 1.5;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        
        .embed-field {{
            display: grid;
            gap: 5px;
        }}
        
        .embed-field-name {{
            color: #b5bac1;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .embed-field-value {{
            color: #dcddde;
            font-size: 14px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        
        .embed-thumbnail {{
            max-width: 100%;
            max-height: 200px;
            border-radius: 4px;
            margin-top: 5px;
        }}
        
        .embed-image {{
            max-width: 100%;
            max-height: 400px;
            border-radius: 4px;
            margin-top: 10px;
        }}
        
        .message-buttons {{
            display: flex;
            gap: 10px;
            margin-top: 10px;
            flex-wrap: wrap;
        }}
        
        .button {{
            background: #7B5BE8;
            color: #ffffff;
            padding: 10px 16px;
            border-radius: 4px;
            border: none;
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        
        .button:hover {{
            background: #9370DB;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(123, 91, 232, 0.4);
        }}
        
        .button.secondary {{
            background: #4f545c;
        }}
        
        .button.secondary:hover {{
            background: #5d6066;
        }}
        
        .button.danger {{
            background: #ed4245;
        }}
        
        .button.danger:hover {{
            background: #f04747;
        }}
        
        .button.success {{
            background: #57f287;
            color: #000000;
        }}
        
        .button.success:hover {{
            background: #70f88f;
        }}
        
        .message-reactions {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }}
        
        .reaction {{
            background: rgba(123, 91, 232, 0.2);
            border: 1px solid rgba(123, 91, 232, 0.3);
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 4px;
            color: #dcddde;
        }}
        
        .reaction-count {{
            color: #72767d;
            font-size: 12px;
            font-weight: 600;
        }}

        .hljs {{
            background: transparent !important;
            color: #dcddde;
        }}

        .hljs-attr, .hljs-attribute {{
            color: #7B5BE8;
        }}

        .hljs-string {{
            color: #57f287;
        }}

        .hljs-number {{
            color: #faa61a;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-title">Ticket Transcript: #{channel.name}</div>
            <div class="header-info">
                <div class="header-field">
                    <div class="header-label">Ticket Owner</div>
                    <div class="header-value"><span class="message-mention">@{ticket_owner.name}</span></div>
                </div>
                <div class="header-field">
                    <div class="header-label">Panel Name</div>
                    <div class="header-value">{panel_name}</div>
                </div>
                <div class="header-field">
                    <div class="header-label">Channel ID</div>
                    <div class="header-value">{channel.id}</div>
                </div>
                <div class="header-field">
                    <div class="header-label">Created At</div>
                    <div class="header-value">{channel.created_at.strftime('%B %d, %Y • %H:%M:%S')}</div>
                </div>
            </div>
        </div>

        <div class="stats-dashboard">
            <div class="stat-box">
                <div class="stat-number">{message_count}</div>
                <div class="stat-label">Messages</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{len(users_in_transcript)}</div>
                <div class="stat-label">Users</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{max(user_messages.values()) if user_messages else 0}</div>
                <div class="stat-label">Most Active</div>
            </div>
        </div>
        
        <div class="users-section">
            <div class="users-title">Users in Transcript ({len(users_in_transcript)})</div>
            <div class="users-grid">
                {TranscriptGenerator._build_users_html(users_in_transcript)}
            </div>
        </div>
        
        <div class="messages">
            {await TranscriptGenerator._build_messages_html(messages)}
        </div>
    </div>
    <script>
        document.querySelectorAll('code').forEach(block => {{
            hljs.highlightElement(block);
        }});
    </script>
</body>
</html>
"""
        
        return html.encode(), list(users_in_transcript)
    
    @staticmethod
    def _build_users_html(users: set) -> str:
        """Build HTML for users list with enhanced styling"""
        html = ""
        for user in sorted(users, key=lambda u: u.name):
            html += f"""
            <div class="user-item">
                <img class="user-avatar" src="{user.display_avatar.url}" alt="{html_module.escape(user.name)}">
                <div class="user-info">
                    <div class="user-name">{html_module.escape(user.name)}</div>
                    <div class="user-tag">@{html_module.escape(user.name)}</div>
                </div>
            </div>
            """
        return html
    
    @staticmethod
    def _parse_mentions(text: str) -> str:
        """Convert Discord mention format to styled mentions"""
        text = html_module.escape(text)
        # User mentions <@ID>
        text = re.sub(r'&lt;@!?(\d+)&gt;', r'<span class="message-mention">@User</span>', text)
        # Role mentions <@&ID>
        text = re.sub(r'&lt;@&amp;(\d+)&gt;', r'<span class="message-mention">@Role</span>', text)
        # Channel mentions <#ID>
        text = re.sub(r'&lt;#(\d+)&gt;', r'<span class="message-mention">#channel</span>', text)
        return text
    
    @staticmethod
    def _parse_code_blocks(text: str) -> str:
        """Parse and highlight code blocks"""
        # Handle triple backtick code blocks
        def replace_code_block(match):
            language = match.group(1) or "plaintext"
            code = html_module.escape(match.group(2)).strip()
            return f'<div class="message-code"><code class="language-{language}">{code}</code></div>'
        
        text = re.sub(r'```(\w+)?\n(.*?)```', replace_code_block, text, flags=re.DOTALL)
        
        # Handle inline code with single backticks
        text = re.sub(
            r'`([^`]+)`',
            lambda m: f'<code style="background: #1e1e2e; padding: 2px 4px; border-radius: 3px; color: #57f287; font-family: monospace;">{html_module.escape(m.group(1))}</code>',
            text
        )
        
        return text
    
    @staticmethod
    async def _build_messages_html(messages: List[discord.Message]) -> str:
        """Build HTML for all messages with enhanced content display"""
        html = ""
        for message in messages:
            timestamp = message.created_at.strftime("%H:%M:%S")
            
            # Skip empty system messages
            content = message.content or ""
            
            # Parse content: mentions and code blocks
            content = TranscriptGenerator._parse_mentions(content)
            content = TranscriptGenerator._parse_code_blocks(content)
            
            # Skip bot messages that only have embeds/attachments and no text
            if not content.strip() and not message.embeds and not message.attachments and not message.components:
                continue
            
            html += f"""
            <div class="message">
                <img class="message-author-avatar" src="{message.author.display_avatar.url}" alt="{html_module.escape(message.author.name)}">
                <div class="message-content">
                    <div class="message-header">
                        <span class="message-author">{html_module.escape(message.author.name)}</span>
                        <span class="message-timestamp">{timestamp}</span>
                    </div>
                    {f'<div class="message-text">{content}</div>' if content.strip() else ''}
            """
            
            # Render embeds
            for embed in message.embeds:
                html += TranscriptGenerator._build_embed_html(embed)
            
            # Render buttons/components
            if message.components:
                html += TranscriptGenerator._build_buttons_html(message.components)
            
            # Render attachments and images
            if message.attachments:
                html += '<div class="message-attachments">'
                for attachment in message.attachments:
                    if attachment.content_type and attachment.content_type.startswith('image'):
                        html += f'<img class="message-image" src="{attachment.url}" alt="attachment">'
                    else:
                        # Calculate file size
                        size_mb = attachment.size / (1024 * 1024)
                        if size_mb >= 1:
                            size_str = f"{size_mb:.2f} MB"
                        else:
                            size_str = f"{attachment.size / 1024:.2f} KB"
                        html += f'<div class="message-attachment"><span>📎</span><a href="{attachment.url}">{html_module.escape(attachment.filename)}</a> <span style="color: #72767d;">({size_str})</span></div>'
                html += '</div>'
            
            # Render reactions
            if message.reactions:
                html += '<div class="message-reactions">'
                for reaction in message.reactions:
                    emoji_str = str(reaction.emoji)
                    html += f'<div class="reaction"><span>{emoji_str}</span><span class="reaction-count">{reaction.count}</span></div>'
                html += '</div>'
            
            html += """
                </div>
            </div>
            """
        
        return html
    
    @staticmethod
    def _build_embed_html(embed: discord.Embed) -> str:
        """Build HTML for a rich embed with all fields"""
        html = '<div class="message-embed">'
        
        # Title
        if embed.title:
            html += f'<div class="embed-title">{html_module.escape(embed.title)}</div>'
        
        # Description
        if embed.description:
            desc = html_module.escape(embed.description)
            desc = TranscriptGenerator._parse_mentions(desc)
            desc = desc.replace('&lt;', '<').replace('&gt;', '>')  # Fix double-escaping from mentions
            html += f'<div class="embed-description">{desc}</div>'
        
        # Fields
        if embed.fields:
            for field in embed.fields:
                field_value = html_module.escape(field.value)
                field_value = TranscriptGenerator._parse_mentions(field_value)
                field_value = field_value.replace('&lt;', '<').replace('&gt;', '>')
                html += f'''
                <div class="embed-field">
                    <div class="embed-field-name">{html_module.escape(field.name)}</div>
                    <div class="embed-field-value">{field_value}</div>
                </div>
                '''
        
        # Thumbnail
        if embed.thumbnail:
            html += f'<img class="embed-thumbnail" src="{embed.thumbnail.url}" alt="embed thumbnail">'
        
        # Image
        if embed.image:
            html += f'<img class="embed-image" src="{embed.image.url}" alt="embed image">'
        
        html += '</div>'
        return html
    
    @staticmethod
    def _build_buttons_html(components: list) -> str:
        """Build HTML for button components"""
        html = '<div class="message-buttons">'
        
        for component in components:
            if hasattr(component, 'children'):
                for button in component.children:
                    if hasattr(button, 'label'):
                        style_class = ""
                        if hasattr(button, 'style'):
                            if button.style == discord.ButtonStyle.primary or button.style.name == "blurple":
                                style_class = ""
                            elif button.style.name == "gray":
                                style_class = "secondary"
                            elif button.style.name == "red":
                                style_class = "danger"
                            elif button.style.name == "green":
                                style_class = "success"
                        
                        emoji_part = ""
                        if hasattr(button, 'emoji') and button.emoji:
                            emoji_part = f'{button.emoji} '
                        
                        label = html_module.escape(button.label) if button.label else "Button"
                        html += f'<div class="button {style_class}">{emoji_part}{label}</div>'
        
        html += '</div>'
        return html