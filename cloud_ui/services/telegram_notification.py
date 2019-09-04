import json
from collections import defaultdict

import contextlib
import aiocontext
import trio

contextlib.asynccontextmanager = aiocontext.async_contextmanager
import triogram

from cloud_ui.cloudapp import UICloud
from .service import Service


class TelegramService(Service):
    COMMAND_HELP = "/help"
    COMMAND_SUBSCRIBE = "/subscribe"
    COMMAND_UNSUBSCRIBE = "/unsubscribe"
    COMMAND_LIST = "/list"
    COMMAND_REQUEST = "/request"

    help = f"""Welcome to cloudui notify system ...

    {COMMAND_HELP}       - helpful info
    {COMMAND_REQUEST}    - request access of administrator
    {COMMAND_LIST}       - show publics list - subscribe/unsubscribe ...

    """

    """
    gets token from keystore:telegram#telegram_token
    """
    async def get_token(self):
        self.cloud: 'UICloud'
        return await self.cloud.get_service("keystore").request("get", "telegram#telegram_token")

    async def init(self):
        keystore_service: Service = await self.cloud.wait_service("keystore")
        token = None
        while not token:
            await trio.sleep(1)
            token = await self.get_token()

        self.publics = await self.get_param("publics", defaultdict(list))

        # self.publics = defaultdict(list)
        #
        # loaded_publics = await self.get_param()
        # if loaded_publics:
        #     for public_name in loaded_publics:
        #         self.publics[public_name] = loaded_publics[public_name]

        self.bot = triogram.make_bot(token)
        self.approved = await self.get_param("approved", list())
        # self.approved = await keystore_service.request("get", "telegram#approved")
        # if not self.approved:
        #     self.approved = []

        self.pending_requests_access = await self.get_param("pending_requests_access", dict())

        # self.pending_requests_access = await keystore_service.request("get", "telegram#pending_requests_access")
        # if self.pending_requests_access is None:
        #     self.pending_requests_access = dict()

        self.users_info = await self.get_param("users_info", dict())
        # self.users_info = await keystore_service.request("get", "telegram#users_info")
        # if not self.users_info:
        #     self.users_info = dict()

    async def start(self):
        await self.init()

        async def bot_handler(*args):
            await self.bot()

        async def echo_handler(*args):
            await self.echo(self.bot)

        self.cloud.add_background_job(echo_handler)
        self.cloud.add_background_job(bot_handler)
        return await super().start()

    async def get_param(self, param_name, defaultvalue):
        keystore_service = await self.cloud.wait_service("keystore")
        loaded = await keystore_service.request("get", f"telegram#{param_name}")
        if loaded:
            try:
                loaded = json.loads(loaded)
            except Exception as e:
                loaded = None
        if isinstance(defaultvalue, (defaultdict, dict)):
            if loaded:
                try:
                    defaultvalue.update(loaded)
                    return defaultvalue
                except Exception as e:
                    return defaultvalue
            else:
                return defaultvalue
        else:
            return loaded or defaultvalue

    async def save_param(self, param_name, obj):
        print(f"SAVING PARAM {param_name}", obj)
        keystore_service = await self.cloud.wait_service("keystore")
        await keystore_service.request("put", dict(key=f"telegram#{param_name}", value=json.dumps(obj)))

    @classmethod
    def get_name(cls):
        return "telegram_bot"

    @classmethod
    def list(cls):
        return ["subscribe", "publish", "list", "auth", "create", "invite", "list_pending", "approve_pending"]

    async def process_subscribe(self, arguments):
        pass

    async def process_publish(self, arguments):
        channel = arguments['channel']
        payload = arguments['payload']

        for subscriber in self.publics[channel]:
            await self.send_text(subscriber, payload)

    async def process_list(self, arguments):
        result = list()
        for public_name in self.publics:
            result.append(dict(name=public_name, subscribers=[self.users_info.get(chat_id, self.users_info.get(str(chat_id))) for chat_id in self.publics[public_name]]))
        return result

    async def process_auth(self, arguments):
        pass

    async def process_create(self, arguments):
        if arguments not in self.publics:
            self.publics[arguments] = []

            await self.save_param("publics", self.publics)

    async def process_invite(self, arguments):
        pass

    async def process_list_pending(self, arguments):
        return self.pending_requests_access

    async def process_approve_pending(self, arguments):
        if arguments in self.pending_requests_access:
            await self.send_text(chat_id=arguments, text="your request was approved by admin")
            self.approved.append(arguments)
            del self.pending_requests_access[arguments]

            await self.save_param("approved", self.approved)
            await self.save_param("pending_requests_access", self.pending_requests_access)

    async def process(self, name: str, arguments: 'Any'):
        print(f"REQUESTING {name} {arguments}")
        method = getattr(self, f"process_{name}", None)
        print(method)
        if method:
            return await method(arguments)

    async def echo(self, *args):
        """
            Waits for new messages and sends the received text back.
            """

        def new_message(update):
            return "message" in update

        async with self.bot.sub(new_message) as updates:
            async for update in updates:
                await self.process_message(update)

    async def process_message(self, update):

        print(f"new message ? ", update)

        text = update['message']['text']
        chat_id = update['message']['from']['id']
        if update['message']['from']['is_bot'] is False:
            user_info = f"{update['message']['from']['username']}:{update['message']['from']['first_name']} {update['message']['from']['last_name']}"
        else:
            user_info = None
        if text.startswith(self.COMMAND_HELP):
            await self.send_help(chat_id)
        elif text.startswith("help"):
            await self.send_help(chat_id)
        elif text.startswith(self.COMMAND_REQUEST):
            async def request_handler(*args):
                self.users_info[chat_id] = user_info
                await self.process_request_access(chat_id, user_info)
            self.cloud.add_background_job(request_handler)
        elif text.startswith(self.COMMAND_LIST):
            await self.send_list(chat_id)
        elif text.startswith(self.COMMAND_SUBSCRIBE):
            public_name = text[len(self.COMMAND_SUBSCRIBE) + 1:]
            self.publics[public_name].append(chat_id)
            await self.save_param("publics", self.publics)
        elif text.startswith(self.COMMAND_UNSUBSCRIBE):
            public_name = text[len(self.COMMAND_UNSUBSCRIBE) + 1:]
            self.publics[public_name].remove(chat_id)
            await self.save_param("publics", self.publics)

    async def send_text(self, chat_id, text):
        await self.bot.api.send_message(params=dict(chat_id=chat_id, text=text))

    async def send_help(self, chat_id):

        await self.send_text(chat_id, self.help)

    async def process_request_access(self, chat_id, user_info):
        if chat_id in self.approved:
            await self.send_text(chat_id, u"you are already approved...")
            return

        self.pending_requests_access[chat_id] = user_info
        await self.save_param("pending_requests_access", self.pending_requests_access)
        await self.save_param("users_info", self.users_info)
        await self.send_text(chat_id=chat_id, text=u"your request was received ... wait for an admin apply... You will be notified...")

    async def send_list(self, chat_id):
        publics_list = "\n".join([
            f"/subscribe_{public_name}" if chat_id not in self.publics[public_name] else f"/unsubscribe_{public_name}" for public_name in self.publics
        ])
        answer = f"""{self.help}
    
        {publics_list}
        """
        await self.send_text(chat_id=chat_id, text=answer)
