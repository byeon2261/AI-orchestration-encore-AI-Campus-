import asyncio
import time
from time import perf_counter


async def wait_task(name: str, seconds: float) -> str:
    """논블로킹 대기를 확인하기 위한 코루틴."""
    print(f"{name} 시작")

    # 현재 코루틴은 잠시 멈추고 이벤트 루프는 다른 코루틴을 실행할 수 있다.
    await asyncio.sleep(seconds)

    print(f"{name} 완료")
    return name

async def show_coroutine() -> None:
    """코루틴 객체와 await의 역할을 확인한다."""

    # async 함수는 호출만 하면 실행 결과가 아니라 코루틴 객체를 반환한다.
    coroutine = wait_task("코루틴 확인", 0.5)
    print(f"호출 직후 자료형: {type(coroutine).__name__}")

    # await를 만나면 코루틴을 실행하고, 결과가 나올때까지 현재 코루틴을 잠시 멈춘다.
    result = await coroutine

    print(f"await 결과: {result}")

async def main() -> None:
    print("1. 코루틴과 await")
    await show_coroutine()

if __name__ == "__main__":
    # 최상위 코루틴인 main()을 이벤트 루프에서 실행한다.
    asyncio.run(main())