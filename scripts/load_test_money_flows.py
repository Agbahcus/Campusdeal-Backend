import argparse
import concurrent.futures
import json
import os
import random
import sys
import time
from dataclasses import dataclass

import requests


@dataclass
class ActionResult:
    name: str
    status_code: int
    ok: bool
    body: object
    error: str = ''


def build_session(token: str | None):
    session = requests.Session()
    session.headers.update({
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    })
    if token:
        session.headers['Authorization'] = f'Bearer {token}'
    return session


def request_json(session, base_url, method, path, payload):
    response = session.request(
        method=method,
        url=f"{base_url.rstrip('/')}{path}",
        data=json.dumps(payload),
        timeout=30,
    )
    try:
        body = response.json()
    except Exception:
        body = response.text
    return response.status_code, body


def run_action(base_url, token, action_name, path, payload):
    try:
        session = build_session(token)
        status_code, body = request_json(session, base_url, 'POST', path, payload)
        ok = status_code < 500
        return ActionResult(action_name, status_code, ok, body)
    except Exception as exc:
        return ActionResult(action_name, 0, False, None, str(exc))


def generate_request_id(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"


def parse_args():
    parser = argparse.ArgumentParser(description='Load test CampusDeal money flows safely.')
    parser.add_argument('--base-url', default=os.environ.get('API_BASE_URL', '').strip(), help='API base URL, e.g. https://campusdeal-backend.onrender.com/api')
    parser.add_argument('--token', default=os.environ.get('API_TOKEN', '').strip(), help='Bearer access token')
    parser.add_argument('--concurrency', type=int, default=4, help='Number of concurrent workers')
    parser.add_argument('--repeat', type=int, default=3, help='How many times to repeat each action')
    parser.add_argument('--order-id', default='', help='Order ID for checkout/refund actions')
    parser.add_argument('--withdraw-amount', default='1000.00', help='Withdrawal amount')
    parser.add_argument('--bank-account-id', default='', help='Bank account ID for withdrawals')
    parser.add_argument('--deposit-amount', default='1000.00', help='Wallet deposit amount')
    parser.add_argument('--reference', default='', help='Payment/deposit reference for verification endpoints')
    parser.add_argument('--delivery-address', default='CampusDeal test address', help='Checkout delivery address')
    parser.add_argument('--delivery-phone', default='08000000000', help='Checkout delivery phone')
    parser.add_argument('--refund-reason', default='other', help='Refund reason')
    parser.add_argument('--refund-explanation', default='This is a safe load-test refund request payload for validation.', help='Refund explanation')
    parser.add_argument('--include-verify', action='store_true', help='Also hit verify endpoints when a reference is supplied')
    return parser.parse_args()


def build_actions(args):
    actions = []

    if args.order_id:
        actions.append((
            'checkout',
            f'/marketplace/orders/{args.order_id}/checkout/',
            lambda: {
                'payment_method': 'paystack',
                'delivery_address': args.delivery_address,
                'delivery_phone': args.delivery_phone,
                'request_id': generate_request_id('checkout'),
            },
        ))
        actions.append((
            'refund-request',
            f'/marketplace/orders/{args.order_id}/request-refund/',
            lambda: {
                'reason': args.refund_reason,
                'detailed_explanation': args.refund_explanation,
                'request_id': generate_request_id('refund'),
            },
        ))

    actions.append((
        'wallet-add-funds',
        '/marketplace/wallet/add-funds/',
        lambda: {
            'amount': args.deposit_amount,
            'request_id': generate_request_id('wallet'),
        },
    ))

    actions.append((
        'wallet-withdraw',
        '/marketplace/wallet/withdraw/',
        lambda: {
            'amount': args.withdraw_amount,
            'bank_account_id': args.bank_account_id or None,
            'request_id': generate_request_id('withdraw'),
        },
    ))

    if args.include_verify and args.reference:
        actions.append((
            'verify-wallet-deposit',
            '/marketplace/wallet/verify-deposit/',
            lambda: {'reference': args.reference},
        ))
        actions.append((
            'verify-payment',
            '/marketplace/payments/verify/',
            lambda: {'reference': args.reference},
        ))

    return actions


def main():
    args = parse_args()

    if not args.base_url:
        print('ERROR: --base-url or API_BASE_URL is required', file=sys.stderr)
        return 2

    actions = build_actions(args)

    if not actions:
        print('No actions configured. Provide --order-id for checkout/refund load tests.', file=sys.stderr)
        return 1

    jobs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as executor:
        for action_name, path, payload_factory in actions:
            payload = payload_factory()
            for _ in range(max(1, args.repeat)):
                jobs.append(executor.submit(
                    run_action,
                    args.base_url,
                    args.token,
                    action_name,
                    path,
                    payload,
                ))

        results = [job.result() for job in concurrent.futures.as_completed(jobs)]

    failures = 0
    for result in results:
        status_text = f"{result.status_code}" if result.status_code else 'ERR'
        print(f"[{status_text}] {result.name} {json.dumps(result.body, default=str) if result.body is not None else result.error}")
        if not result.ok:
            failures += 1

    print(f"\nCompleted {len(results)} requests with {failures} failures.")
    return 0 if failures == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
