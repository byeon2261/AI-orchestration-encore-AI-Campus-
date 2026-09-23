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

async def blocking_wait(name: str, seconds: float) -> None:

    print(f"{name} 시작")

    time.sleep(seconds)

    print(f"{name} 완료")

async def compare_blocking_waits() -> None:
    """ㅇ"""
    started_at = perf_counter()
    
    await asyncio.gather(
        blocking_wait("블로킹 작업 A", 0.5),
        blocking_wait("블로킹 작업 B", 0.5),
    )
    print(f"블로킹 대기 두 개: {perf_counter() - started_at:.2f}초")

    started_at = perf_counter()

    await asyncio.gather(
        blocking_wait("블로킹 작업 A", 0.5),
        blocking_wait("블로킹 작업 B", 0.5),
    )

    print(f"블로킹 대기 두 개: {perf_counter() - started_at:.2f}초")

async def run_sequentially() -> None:
    """두 작업을 순서대로 실행한다."""

    started_at = perf_counter()

    await wait_task("첫 번째 순차 작업", 0.5)
    await wait_task("두 번째 순차 작업", 0.5)

    print(f"순차 실행 {perf_counter() - started_at:.2f}초")

async def run_concurrently() -> None:
    """두 작업을 함께 실행한다."""

    started_at = perf_counter()

    await asyncio.gather(
        wait_task("첫 번째 순차 작업", 0.5),
        wait_task("두 번째 순차 작업", 0.5)
    )

    print(f"함께 실행 {perf_counter() - started_at:.2f}초")

async def main() -> None:
    # print("1. 코루틴과 await")
    # await show_coroutine()

    # await compare_blocking_waits()

    print("\n3. 순차 실행과 동시 실행")
    await run_sequentially()
    
    print("=" * 30)
    await run_concurrently()

if __name__ == "__main__":
    # 최상위 코루틴인 main()을 이벤트 루프에서 실행한다.
    asyncio.run(main())