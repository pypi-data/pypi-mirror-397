"""
MU-TH-UR 6000 Terminal Interface.

Full-screen Textual TUI application with Aliens aesthetic.
"""

import asyncio
import uuid
from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Footer, Header, Input, Static

from nostromo_core import ChatEngine
from nostromo_core.adapters.memory import FileMemoryStore
from nostromo_core.theme import (
    BOOT_SEQUENCE,
    DISPLAY_NAME,
    HEADER_COMPACT,
    PRIMARY,
    SHUTDOWN_SEQUENCE,
    SYSTEM_NAME,
)
from nostromo_core.theme.errors import NostromoError, format_error, get_error_for_exception

from nostromo_cli.config import ConfigManager, DATA_DIR


class MotherHeader(Static):
    """ASCII art header for MU-TH-UR 6000."""

    def compose(self) -> ComposeResult:
        yield Static(HEADER_COMPACT, id="header-art")


class MessageDisplay(Static):
    """A single message in the chat."""

    def __init__(
        self,
        content: str,
        is_mother: bool = False,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.content = content
        self.is_mother = is_mother

    def compose(self) -> ComposeResult:
        prefix = f"◀ {DISPLAY_NAME}" if self.is_mother else "▶ CREW"
        yield Static(f"[bold]{prefix}[/]", classes="message-prefix")
        yield Static(self.content, classes="message-content")


class TypingIndicator(Static):
    """Animated typing indicator."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._frames = ["█", "█", " "]
        self._frame_index = 0

    def on_mount(self) -> None:
        self.set_interval(0.5, self._animate)

    def _animate(self) -> None:
        self._frame_index = (self._frame_index + 1) % len(self._frames)
        cursor = self._frames[self._frame_index]
        self.update(f"◀ {DISPLAY_NAME}: {cursor}")


class ChatView(VerticalScroll):
    """Scrollable container for chat messages."""

    def add_message(self, content: str, is_mother: bool = False) -> MessageDisplay:
        """Add a message to the chat view."""
        message = MessageDisplay(content, is_mother=is_mother)
        message.add_class("mother-message" if is_mother else "crew-message")
        self.mount(message)
        self.scroll_end(animate=False)
        return message

    def add_typing_indicator(self) -> TypingIndicator:
        """Add typing indicator while MOTHER is responding."""
        indicator = TypingIndicator(id="typing-indicator")
        self.mount(indicator)
        self.scroll_end(animate=False)
        return indicator

    def remove_typing_indicator(self) -> None:
        """Remove the typing indicator."""
        try:
            indicator = self.query_one("#typing-indicator")
            indicator.remove()
        except Exception:
            pass


class ResponseDisplay(Static):
    """Widget for streaming MOTHER response with typing effect."""

    def __init__(self, typing_speed: int = 50, uppercase: bool = False, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._content = ""
        self._display_content = ""
        self._typing_speed = typing_speed
        self._uppercase = uppercase
        self._typing_complete = False

    async def stream_content(self, content_iterator) -> str:
        """Stream content from an async iterator with typing effect."""
        self._content = ""
        self._display_content = ""
        self._typing_complete = False

        async for chunk in content_iterator:
            self._content += chunk
            # Apply uppercase if configured
            display_chunk = chunk.upper() if self._uppercase else chunk
            self._display_content += display_chunk

            # Update display with cursor
            self.update(f"◀ {DISPLAY_NAME}: {self._display_content}█")

            # Small delay for typing effect
            if self._typing_speed > 0:
                delay = 1.0 / self._typing_speed
                await asyncio.sleep(delay * len(chunk))

        # Final update without cursor
        self._typing_complete = True
        self.update(f"◀ {DISPLAY_NAME}: {self._display_content}")

        return self._content

    def set_content(self, content: str) -> None:
        """Set content directly without streaming."""
        self._content = content
        self._display_content = content.upper() if self._uppercase else content
        self._typing_complete = True
        self.update(f"◀ {DISPLAY_NAME}: {self._display_content}")


class NostromoApp(App):
    """
    MU-TH-UR 6000 Terminal Interface.

    Full-screen chat application with Aliens aesthetic.
    """

    TITLE = SYSTEM_NAME
    CSS_PATH = "styles/mother.tcss"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Exit", show=True),
        Binding("ctrl+l", "clear", "Clear", show=True),
        Binding("ctrl+n", "new_session", "New Session", show=True),
        Binding("escape", "focus_input", "Focus Input", show=False),
    ]

    def __init__(
        self,
        config: ConfigManager | None = None,
        session_id: str | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._config = config
        self._session_id = session_id or f"session-{uuid.uuid4().hex[:8]}"
        self._engine: ChatEngine | None = None
        self._user_config = None
        self._is_processing = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            MotherHeader(),
            ChatView(id="chat-view"),
            Horizontal(
                Static("▶ ", id="prompt-prefix"),
                Input(placeholder="ENTER QUERY...", id="user-input"),
                id="input-container",
            ),
            id="main-container",
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Initialize the application on mount."""
        await self._initialize_engine()
        await self._show_boot_sequence()
        self.query_one("#user-input", Input).focus()

    async def _initialize_engine(self) -> None:
        """Initialize the chat engine with configured provider."""
        from nostromo_cli.config import get_config_manager
        from nostromo_cli.secrets import get_secrets_manager

        config = self._config or get_config_manager()
        secrets = get_secrets_manager()

        # Get provider configuration
        provider_config = config.get_provider_config()
        self._user_config = config.get_user_config()

        # Get API key
        api_key = secrets.get_key(provider_config.provider)  # type: ignore
        if not api_key:
            self._show_error(
                format_error(NostromoError.KEY_MISSING, provider=provider_config.provider.upper())
            )
            return

        # Create LLM provider
        if provider_config.provider == "anthropic":
            from nostromo_core.adapters.anthropic import AnthropicProvider

            llm = AnthropicProvider(
                api_key=api_key,
                model=provider_config.model,
                max_tokens=provider_config.max_tokens,
                temperature=provider_config.temperature,
            )
        elif provider_config.provider == "openai":
            from nostromo_core.adapters.openai import OpenAIProvider

            llm = OpenAIProvider(
                api_key=api_key,
                model=provider_config.model,
                max_tokens=provider_config.max_tokens,
                temperature=provider_config.temperature,
            )
        else:
            self._show_error(
                format_error(NostromoError.INVALID_PROVIDER, provider=provider_config.provider)
            )
            return

        # Create memory store
        memory = FileMemoryStore(DATA_DIR / "sessions")

        # Create engine
        self._engine = ChatEngine(
            llm=llm,
            memory=memory,
            system_prompt=provider_config.system_prompt,
        )

    async def _show_boot_sequence(self) -> None:
        """Display the boot sequence animation."""
        chat_view = self.query_one("#chat-view", ChatView)

        for line in BOOT_SEQUENCE:
            if line:
                chat_view.add_message(line, is_mother=True)
            await asyncio.sleep(0.3)

    def _show_error(self, message: str) -> None:
        """Display an error message."""
        chat_view = self.query_one("#chat-view", ChatView)
        chat_view.add_message(f"*** ERROR: {message} ***", is_mother=True)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input submission."""
        user_input = event.value.strip()

        if not user_input:
            return

        if self._is_processing:
            return

        # Clear input
        event.input.value = ""

        # Handle special commands
        if user_input.lower() in ("exit", "quit", "bye"):
            await self._show_shutdown_sequence()
            self.exit()
            return

        if user_input.lower() == "clear":
            await self.action_clear()
            return

        # Add user message to chat
        chat_view = self.query_one("#chat-view", ChatView)
        chat_view.add_message(user_input, is_mother=False)

        # Process with engine
        if self._engine:
            self._is_processing = True
            self._send_message(user_input)

    @work(thread=True)
    async def _send_message(self, user_input: str) -> None:
        """Send message to MOTHER and stream response."""
        chat_view = self.query_one("#chat-view", ChatView)

        # Create response display
        typing_speed = self._user_config.typing_speed if self._user_config else 50
        uppercase = self._user_config.uppercase_responses if self._user_config else False

        response_display = ResponseDisplay(
            typing_speed=typing_speed,
            uppercase=uppercase,
        )
        response_display.add_class("mother-message")

        self.call_from_thread(chat_view.mount, response_display)
        self.call_from_thread(chat_view.scroll_end, animate=False)

        try:
            # Stream response
            full_response = ""

            async def stream_wrapper():
                nonlocal full_response
                async for token in self._engine.chat_stream(self._session_id, user_input):
                    full_response += token
                    yield token

            await response_display.stream_content(stream_wrapper())

        except Exception as e:
            error_type, kwargs = get_error_for_exception(e)
            error_msg = format_error(error_type, **kwargs)
            self.call_from_thread(response_display.set_content, f"*** {error_msg} ***")

        finally:
            self._is_processing = False
            self.call_from_thread(self.query_one("#user-input", Input).focus)

    async def _show_shutdown_sequence(self) -> None:
        """Display shutdown sequence."""
        chat_view = self.query_one("#chat-view", ChatView)

        for line in SHUTDOWN_SEQUENCE:
            if line:
                chat_view.add_message(line, is_mother=True)
            await asyncio.sleep(0.3)

    async def action_quit(self) -> None:
        """Handle quit action."""
        await self._show_shutdown_sequence()
        self.exit()

    async def action_clear(self) -> None:
        """Clear the chat view."""
        chat_view = self.query_one("#chat-view", ChatView)
        chat_view.remove_children()

        if self._engine:
            await self._engine.clear_session(self._session_id)

        chat_view.add_message("DISPLAY CLEARED.", is_mother=True)

    async def action_new_session(self) -> None:
        """Start a new session."""
        self._session_id = f"session-{uuid.uuid4().hex[:8]}"

        chat_view = self.query_one("#chat-view", ChatView)
        chat_view.remove_children()

        chat_view.add_message(f"NEW SESSION INITIALIZED: {self._session_id}", is_mother=True)

    def action_focus_input(self) -> None:
        """Focus the input field."""
        self.query_one("#user-input", Input).focus()
