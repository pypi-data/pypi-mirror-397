# extergram/core.py

import httpx
import json
import asyncio
import inspect
from .ui import ButtonsDesign
from .api_types import Update, Message, CallbackQuery, BotCommand
from .ext.base import BaseHandler
from . import errors

class Bot:
    """
    The main class for creating a Telegram bot and interacting with the API.
    """
    def __init__(self, token: str):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{self.token}/"
        self.handlers = []
        self._offset = None
        self._client = httpx.AsyncClient()

    async def _make_request(self, method: str, params: dict = None, files: dict = None):
        """Internal method to make requests to the Telegram API."""
        try:
            response = await self._client.post(self.api_url + method, json=params, files=files, timeout=40)
            
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    description = error_data.get('description', 'Unknown API error')
                    error_code = error_data.get('error_code', response.status_code)
                except json.JSONDecodeError:
                    description = "Failed to parse error response"
                    error_code = response.status_code

                # Extended error mapping to prevent crashes
                if response.status_code == 400:
                    raise errors.BadRequestError(description, error_code)
                elif response.status_code == 401:
                    raise errors.UnauthorizedError(description, error_code)
                elif response.status_code == 403:
                    raise errors.ForbiddenError(description, error_code)
                elif response.status_code == 404:
                    raise errors.NotFoundError(description, error_code)
                elif response.status_code == 409:
                    raise errors.ConflictError(description, error_code)
                elif response.status_code == 413:
                    raise errors.EntityTooLargeError(description, error_code)
                elif response.status_code == 502:
                    raise errors.BadGatewayError(description, error_code)
                else:
                    raise errors.APIError(description, error_code)

            data = response.json()
            if not data.get('ok'):
                raise errors.APIError(data.get('description', 'Unknown error'), data.get('error_code', -1))
            
            return data
        except httpx.RequestError as e:
            # Wrap all network-related issues into NetworkError for retry logic
            raise errors.NetworkError(f"Network error: {e}", -1)
        except json.JSONDecodeError:
            raise errors.APIError("Failed to decode JSON response", -1)

    def add_handler(self, handler: BaseHandler):
        """
        Registers a new event handler.
        """
        if not isinstance(handler, BaseHandler):
            raise TypeError("handler must be an instance of BaseHandler")
        self.handlers.append(handler)

    async def _process_update(self, update: Update):
        """Asynchronously processes a single update."""
        event = update.message or update.callback_query or update.edited_message
        if not event:
            return

        tasks = []
        for handler in self.handlers:
            if handler.check_update(update):
                if inspect.iscoroutinefunction(handler.callback):
                    tasks.append(asyncio.create_task(handler.callback(self, event)))
                else:
                    loop = asyncio.get_running_loop()
                    tasks.append(loop.run_in_executor(None, handler.callback, self, event))
        
        if tasks:
            await asyncio.gather(*tasks)

    async def _polling_loop(self, timeout: int = 30):
        """The main asynchronous polling loop with auto-restart logic."""
        while True:
            try:
                updates_data = await self.get_updates(offset=self._offset, timeout=timeout)
                updates = updates_data.get('result', [])
                if updates:
                    for raw_update in updates:
                        self._offset = raw_update['update_id'] + 1
                        update_obj = Update(raw_update)
                        asyncio.create_task(self._process_update(update_obj))
            
            except errors.NetworkError as e:
                print(f"[!] Network Connection Error: {e}. Retrying in 5s...")
                await asyncio.sleep(5)
                continue # Skip to next iteration to retry

            except (errors.UnauthorizedError, errors.NotFoundError) as e:
                print(f"[CRITICAL] Invalid Token or URL: {e}")
                print(">>> Please check your BOT_TOKEN. Retrying in 10s...")
                await asyncio.sleep(10)

            except errors.ConflictError:
                print("[!] Conflict: Another bot instance is running. Waiting 10s...")
                await asyncio.sleep(10)

            except errors.BadGatewayError:
                print("[!] Telegram servers are down (502 Bad Gateway). Waiting 5s...")
                await asyncio.sleep(5)

            except errors.APIError as e:
                print(f"[!] API Error: {e}. Attempting to continue in 5s...")
                await asyncio.sleep(5)

            except Exception as e:
                print(f"[!!!] Unexpected System Error: {e}")
                await asyncio.sleep(10)

    async def polling(self, timeout: int = 30):
        """Starts the bot in long-polling mode. This is now a coroutine."""
        print("Bot started polling...")
        try:
            # This will now run inside the existing event loop when awaited.
            await self._polling_loop(timeout)
        except (KeyboardInterrupt, asyncio.CancelledError):
            print("Bot stopped.")
        finally:
            # It's a good practice to close the client session on exit.
            await self._client.aclose()


    # --- API Methods ---
    async def get_updates(self, offset: int = None, timeout: int = 30):
        params = {'timeout': timeout, 'offset': offset}
        return await self._make_request('getUpdates', params)

    async def send_message(self, chat_id: int, text: str, parse_mode: str = None, reply_markup=None):
        params = {'chat_id': chat_id, 'text': text}
        if parse_mode:
            params['parse_mode'] = parse_mode
        if isinstance(reply_markup, ButtonsDesign):
            params['reply_markup'] = reply_markup.to_dict()
        elif reply_markup:
            params['reply_markup'] = reply_markup
        return await self._make_request('sendMessage', params)

    async def edit_message_text(self, chat_id: int, message_id: int, text: str, parse_mode: str = None, reply_markup=None):
        params = {'chat_id': chat_id, 'message_id': message_id, 'text': text}
        if parse_mode:
            params['parse_mode'] = parse_mode
        if isinstance(reply_markup, ButtonsDesign):
            params['reply_markup'] = reply_markup.to_dict()
        elif reply_markup:
            params['reply_markup'] = reply_markup
        return await self._make_request('editMessageText', params)
    
    async def answer_callback_query(self, callback_query_id: str, text: str = None, show_alert: bool = False):
        params = {'callback_query_id': callback_query_id}
        if text:
            params['text'] = text
        params['show_alert'] = show_alert
        return await self._make_request('answerCallbackQuery', params)
        
    async def delete_message(self, chat_id: int, message_id: int):
        params = {'chat_id': chat_id, 'message_id': message_id}
        return await self._make_request('deleteMessage', params)

    async def send_photo(self, chat_id: int, photo: str, caption: str = None, parse_mode: str = None, reply_markup=None):
        params = {'chat_id': chat_id}
        files = None
        if caption:
            params['caption'] = caption
        if parse_mode:
            params['parse_mode'] = parse_mode
        if isinstance(reply_markup, ButtonsDesign):
            params['reply_markup'] = reply_markup.to_dict()
        elif reply_markup:
            params['reply_markup'] = reply_markup

        if photo.startswith('http'):
            params['photo'] = photo
        else:
            files = {'photo': open(photo, 'rb')}
            
        return await self._make_request('sendPhoto', params, files=files)

    async def send_document(self, chat_id: int, document: str, caption: str = None, parse_mode: str = None, reply_markup=None):
        params = {'chat_id': chat_id}
        files = None
        if caption:
            params['caption'] = caption
        if parse_mode:
            params['parse_mode'] = parse_mode
        if isinstance(reply_markup, ButtonsDesign):
            params['reply_markup'] = reply_markup.to_dict()
        elif reply_markup:
            params['reply_markup'] = reply_markup
            
        if document.startswith('http'):
            params['document'] = document
        else:
            files = {'document': open(document, 'rb')}

        return await self._make_request('sendDocument', params, files=files)

    async def edit_message_reply_markup(self, chat_id: int, message_id: int, reply_markup=None):
        params = {'chat_id': chat_id, 'message_id': message_id}
        if isinstance(reply_markup, ButtonsDesign):
            params['reply_markup'] = reply_markup.to_dict()
        elif reply_markup:
            params['reply_markup'] = reply_markup
        return await self._make_request('editMessageReplyMarkup', params)
        
    async def set_my_commands(self, commands: list[BotCommand]):
        params = {'commands': [cmd.to_dict() for cmd in commands]}
        return await self._make_request('setMyCommands', params)