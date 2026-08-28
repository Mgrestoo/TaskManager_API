# """
# Proves whether your endpoints run concurrently or serially.

# Usage:
#     1. Run your FastAPI app locally (uvicorn main:app)
#     2. Pick an endpoint that hits the DB (e.g. GET /tasks)
#     3. python3 concurrency_test.py
# """
# import asyncio
# import time
# import httpx 

# URL = "http://localhost:8000/register"   # <-- change to a real DB-hitting route
# NUM_REQUESTS = 20
# HEADERS = {
#     "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyZXN0bzNvQGdtYWlsLmNvbSIsImV4cCI6MTc4Nzc3NzI4OH0.wGW_rGY81eCyK3llbvsCGHRGsTbg0Nk62651hU1ihSM"
#     }  # add {"Authorization": "Bearer <token>"} if the route needs auth


# async def fire_one(client: httpx.AsyncClient, i: int) -> float:
#     start = time.perf_counter()
#     resp = await client.get(URL, headers=HEADERS)
#     elapsed = time.perf_counter() - start
#     print(f"Request {i:2d}: status={resp.status_code} took {elapsed:.3f}s")
#     return elapsed


# async def main():
#     async with httpx.AsyncClient(timeout=30) as client:
#         overall_start = time.perf_counter()
#         results = await asyncio.gather(
#             *(fire_one(client, i) for i in range(NUM_REQUESTS))
#         )
#         overall_elapsed = time.perf_counter() - overall_start

#     avg_individual = sum(results) / len(results)
#     print(f"\n{NUM_REQUESTS} requests")
#     print(f"Total wall time: {overall_elapsed:.3f}s")
#     print(f"Avg per-request time: {avg_individual:.3f}s")
#     print(f"Sum of individual times (if serial): {sum(results):.3f}s")

#     if overall_elapsed < sum(results) * 0.5:
#         print("\n✅ Concurrent: total time is far less than the sum of individual times.")
#     else:
#         print("\n⚠️  Looks serial: total time ≈ sum of individual times. Something is blocking.")


# if __name__ == "__main__":
#     asyncio.run(main())