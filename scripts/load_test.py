import argparse
import asyncio
import os
import statistics
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from urllib.parse import urljoin

import httpx


DEFAULT_ENDPOINTS = ["GET:/washioo-api/health"]
DEFAULT_SCENARIOS = [
    "10-users:10:5",
    "100-users-spike:100:1",
    "100-users-sustained:100:5",
]
PRESET_ENDPOINTS = {
    "tri-role-read": [
        "GET:/washioo-api/users/me",
        "GET:/washioo-api/services/addresses",
        "GET:/washioo-api/services/my-bookings",
        "GET:/washioo-api/customer/vehicles",
        "GET:/washioo-api/customer/notifications",
        "GET:/washioo-api/services/cleaner/profile",
        "GET:/washioo-api/services/cleaner/assignments",
        "GET:/washioo-api/cleaner/notifications",
        "GET:/washioo-api/services/admin/all-bookings",
        "GET:/washioo-api/users/",
    ],
}


@dataclass(frozen=True)
class Endpoint:
    method: str
    path: str


@dataclass(frozen=True)
class Scenario:
    name: str
    users: int
    requests_per_user: int


@dataclass
class RequestResult:
    scenario: str
    endpoint: str
    status: int | None
    elapsed_ms: float
    error: str | None = None


def parse_endpoint(value: str) -> Endpoint:
    if ":" not in value:
        raise argparse.ArgumentTypeError(
            "Endpoint must look like GET:/washioo-api/health"
        )
    method, path = value.split(":", 1)
    method = method.strip().upper()
    path = path.strip()
    if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
        raise argparse.ArgumentTypeError(f"Unsupported HTTP method: {method}")
    if not path.startswith("/"):
        raise argparse.ArgumentTypeError("Endpoint path must start with /")
    return Endpoint(method=method, path=path)


def parse_scenario(value: str) -> Scenario:
    parts = value.split(":")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(
            "Scenario must look like name:users:requests_per_user"
        )
    name, users, requests_per_user = parts
    try:
        users_int = int(users)
        requests_int = int(requests_per_user)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Users and requests must be numbers") from exc
    if users_int < 1 or requests_int < 1:
        raise argparse.ArgumentTypeError("Users and requests must be at least 1")
    return Scenario(name=name, users=users_int, requests_per_user=requests_int)


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = round((len(sorted_values) - 1) * pct)
    return sorted_values[index]


def build_url(base_url: str, path: str) -> str:
    return urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))


async def hit_endpoint(
    client: httpx.AsyncClient,
    scenario_name: str,
    endpoint: Endpoint,
    url: str,
    start_gate: asyncio.Event,
) -> RequestResult:
    await start_gate.wait()
    started = time.perf_counter()
    try:
        response = await client.request(endpoint.method, url)
        elapsed_ms = (time.perf_counter() - started) * 1000
        return RequestResult(
            scenario=scenario_name,
            endpoint=f"{endpoint.method} {endpoint.path}",
            status=response.status_code,
            elapsed_ms=elapsed_ms,
        )
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000
        return RequestResult(
            scenario=scenario_name,
            endpoint=f"{endpoint.method} {endpoint.path}",
            status=None,
            elapsed_ms=elapsed_ms,
            error=type(exc).__name__,
        )


async def run_scenario(
    base_url: str,
    scenario: Scenario,
    endpoints: list[Endpoint],
    headers: dict[str, str],
    timeout_seconds: float,
) -> tuple[float, list[RequestResult]]:
    start_gate = asyncio.Event()
    limits = httpx.Limits(
        max_connections=max(scenario.users, 20),
        max_keepalive_connections=max(scenario.users, 20),
    )
    timeout = httpx.Timeout(timeout_seconds)

    async with httpx.AsyncClient(headers=headers, limits=limits, timeout=timeout) as client:
        tasks = []
        for user_index in range(scenario.users):
            for request_index in range(scenario.requests_per_user):
                endpoint = endpoints[(user_index + request_index) % len(endpoints)]
                url = build_url(base_url, endpoint.path)
                tasks.append(
                    hit_endpoint(client, scenario.name, endpoint, url, start_gate)
                )

        started = time.perf_counter()
        start_gate.set()
        results = await asyncio.gather(*tasks)
        total_seconds = time.perf_counter() - started

    return total_seconds, results


def summarize(total_seconds: float, results: list[RequestResult]) -> str:
    latencies = [result.elapsed_ms for result in results]
    failures = [result for result in results if result.error or not is_success(result.status)]
    status_counts = Counter(str(result.status) if result.status else result.error for result in results)
    endpoint_latencies: dict[str, list[float]] = defaultdict(list)
    for result in results:
        endpoint_latencies[result.endpoint].append(result.elapsed_ms)

    total = len(results)
    success = total - len(failures)
    rate = total / total_seconds if total_seconds > 0 else 0
    failure_rate = (len(failures) / total) * 100 if total else 0

    lines = [
        f"Requests: {total} total, {success} successful, {len(failures)} failed ({failure_rate:.2f}%)",
        f"Throughput: {rate:.2f} requests/sec over {total_seconds:.2f}s",
        (
            "Latency: "
            f"avg {statistics.fmean(latencies):.2f}ms, "
            f"p50 {percentile(latencies, 0.50):.2f}ms, "
            f"p90 {percentile(latencies, 0.90):.2f}ms, "
            f"p95 {percentile(latencies, 0.95):.2f}ms, "
            f"p99 {percentile(latencies, 0.99):.2f}ms, "
            f"max {max(latencies):.2f}ms"
        ),
        "Statuses: " + ", ".join(f"{key}={value}" for key, value in sorted(status_counts.items())),
    ]

    slowest = sorted(
        endpoint_latencies.items(),
        key=lambda item: percentile(item[1], 0.95),
        reverse=True,
    )
    if len(slowest) > 1:
        lines.append("Slowest endpoints by p95:")
        for endpoint, values in slowest:
            lines.append(
                f"  {endpoint}: {len(values)} requests, "
                f"p95 {percentile(values, 0.95):.2f}ms"
            )

    return "\n".join(lines)


def is_success(status: int | None) -> bool:
    return status is not None and 200 <= status < 400


def make_headers() -> dict[str, str]:
    headers = {"User-Agent": "washioo-load-test/1.0"}
    token = os.getenv("LOAD_TEST_BEARER_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def resolve_endpoints(args: argparse.Namespace) -> list[Endpoint]:
    endpoints = []
    for preset in args.preset or []:
        endpoints.extend(parse_endpoint(value) for value in PRESET_ENDPOINTS[preset])
    if args.endpoint:
        endpoints.extend(args.endpoint)
    if not endpoints:
        endpoints = [parse_endpoint(value) for value in DEFAULT_ENDPOINTS]
    return endpoints


async def main_async(args: argparse.Namespace) -> int:
    endpoints = resolve_endpoints(args)
    scenarios = args.scenario or [parse_scenario(value) for value in DEFAULT_SCENARIOS]
    headers = make_headers()
    exit_code = 0

    print(f"Base URL: {args.base_url}")
    print("Endpoints: " + ", ".join(f"{endpoint.method} {endpoint.path}" for endpoint in endpoints))
    print()

    for scenario in scenarios:
        print(
            f"=== {scenario.name}: {scenario.users} concurrent users, "
            f"{scenario.requests_per_user} request(s) each ==="
        )
        total_seconds, results = await run_scenario(
            args.base_url,
            scenario,
            endpoints,
            headers,
            args.timeout,
        )
        print(summarize(total_seconds, results))
        print()

        if any(result.error or not is_success(result.status) for result in results):
            exit_code = 1
        if args.max_p95_ms is not None:
            p95 = percentile([result.elapsed_ms for result in results], 0.95)
            if p95 > args.max_p95_ms:
                exit_code = 1

    return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a small async load test against the deployed Washioo API."
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("LOAD_TEST_BASE_URL"),
        help="Render base URL, for example https://your-service.onrender.com",
    )
    parser.add_argument(
        "--endpoint",
        action="append",
        type=parse_endpoint,
        help="Endpoint to hit. Repeatable. Example: --endpoint GET:/washioo-api/services/",
    )
    parser.add_argument(
        "--preset",
        action="append",
        choices=sorted(PRESET_ENDPOINTS),
        help="Endpoint preset to include. Repeatable.",
    )
    parser.add_argument(
        "--scenario",
        action="append",
        type=parse_scenario,
        help="Scenario as name:users:requests_per_user. Repeatable.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Per-request timeout in seconds.",
    )
    parser.add_argument(
        "--max-p95-ms",
        type=float,
        default=None,
        help="Return a failing exit code when scenario p95 latency is above this value.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if not args.base_url:
        parser.error("--base-url or LOAD_TEST_BASE_URL is required")
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
