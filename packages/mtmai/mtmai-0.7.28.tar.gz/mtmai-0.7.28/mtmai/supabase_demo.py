import asyncio
from supabase import create_async_client
from realtime.types import RealtimePostgresChangesListenEvent
import os


async def realtime_demo():
    SUPABASE_URL = "https://ziohtkhskbozoajxusdl.supabase.co"
    SUPABASE_ANON_KEY: str = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")  # type: ignore
    supabase = await create_async_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    # 提示根据当前配置,需要登录才能获取到订阅数据.
    # login_response = await supabase.auth.sign_in_with_password(
    #     {"email": "admin@example.com", "password": "feihuo321"}
    # )
    # if not login_response.user:
    #     print("登录失败")
    #     return
    # print(login_response.user.id)
    ch = supabase.channel("realtime:public:services")

    def handle(payload):
        print("Realtime payload:", payload)

    ch = ch.on_postgres_changes(
        RealtimePostgresChangesListenEvent.All,
        schema="public",
        table="services",
        # optional: filter by id or other
        # filter="id=eq.{some-id}",
        callback=handle,
    )

    # 调用 subscribe。如果是协程/awaitable，则 await 它
    sub = ch.subscribe()

    # 若 subscribe() 返回协程，则 await
    if asyncio.iscoroutine(sub):
        await sub

    print("Subscribed. Waiting for events... (Ctrl+C to exit)")

    try:
        # 使用 asyncio.sleep 保持事件循环活跃
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Unsubscribing...")
        await ch.unsubscribe()  # 如果需要 await
        # await supabase.close()  # 关闭客户端（如果有此方法）


if __name__ == "__main__":
    asyncio.run(realtime_demo())
