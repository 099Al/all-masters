import json
import logging
from src.ai.gpt_message import ai_validate_message
from src.config_paramaters import SCHEDULE_UPDATE_STATUSES, SCHEDULE_VALIDATE_MESSAGES

from src.database.requests_db import ReqData

from src.scheduled.tkq import broker

logger = logging.getLogger(__name__)

class ValidateMessages(ReqData):
    """
    Проверка сообщений
    """


    def __init__(self):
        super().__init__()
        #self.session = DataBase().get_session()


    async def call_validate_messages(self):
        req = ReqData()
        messages = await req.get_messages_for_validate()

        d_valid_result = {}
        d_ban_result = {}
        for id, user_id, message in messages:
            res_valid = ai_validate_message(message)

            d_res = json.loads(res_valid)
            d_valid_result[id] = (d_res['valid'], d_res.get('reason', None))

            if d_res['valid'] == False:
                d_ban_result[id] = d_res['reason']

        await req.set_validation_results(d_valid_result)
        await req.set_ban_reason(d_ban_result)



validate = ValidateMessages()

@broker.task(
    task_name="validate_messages",
    schedule=[SCHEDULE_VALIDATE_MESSAGES],
)
async def validate_messages() -> None:
    await validate.call_validate_messages()





if __name__ == '__main__':
    import asyncio
    req = ValidateMessages()
    res = asyncio.run(req.call_validate_messages())

    print(f" result: {res}")




