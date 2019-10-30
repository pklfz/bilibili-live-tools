import asyncio
import bilibiliCilent


class Rafflehandler:
    instance = None

    def __new__(cls, *args, **kw):
        if not cls.instance:
            cls.instance = super(Rafflehandler, cls).__new__(cls, *args, **kw)
            cls.instance.list_activity = []
            cls.instance.list_TV = []
            cls.instance.list_TV_waiting = asyncio.Queue()  # { 'id': int, 'type': str, 'time_wait': float, 'roomid': int }
            cls.instance.list_TV_processed = []
        return cls.instance

    async def run(self):
        producer =  self.produce()
        consumers = [ self.consume() for i in range(100) ]  # 同步等待礼物冷却 
        consumers.append(producer)

        done, pending = await asyncio.wait(
            consumers, 
            return_when=asyncio.FIRST_EXCEPTION
        )
        for task in done:
            if task.exception():
                raise task.exception()

    async def consume(self):
        gift_data = await self.list_TV_waiting.get()
        if gift_data['time_wait'] > 0:
            await asyncio.sleep(gift_data['time_wait'])
        await bilibiliCilent.handle_1_TV_raffle(
            gift_data['type'], 
            5, 
            gift_data['roomid'], 
            gift_data['id'], 
        )


    async def produce(self):
        while True:
            len_list_activity = len(self.list_activity)
            len_list_TV = len(self.list_TV)
            set_TV = set(self.list_TV)
            tasklist = []
            for i in set_TV:
                task = asyncio.ensure_future(bilibiliCilent.handle_1_room_TV(i))
                tasklist.append(task)
            if tasklist:
                await asyncio.wait(tasklist, return_when=asyncio.ALL_COMPLETED)
            else:
                pass

            del self.list_activity[:len_list_activity]
            del self.list_TV[:len_list_TV]
            if len_list_activity == 0 and len_list_TV == 0:
                await asyncio.sleep(1.1)
            else:
                await asyncio.sleep(1.0)

    def append2list_TV(self, real_roomid):
        self.list_TV.append(real_roomid)
        return

    def append2list_activity(self, text1):
        self.list_activity.append(text1)
        return

