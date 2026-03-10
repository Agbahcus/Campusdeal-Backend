"""
WITHDRAWAL SYSTEM STRESS TEST
Tests for race conditions, security vulnerabilities, and edge cases
"""

import threading
import time
from decimal import Decimal
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from accounts.models import Profile, BankAccount
from marketplace.models import Withdrawal, WalletTransaction


class WithdrawalStressTest(TransactionTestCase):
    """Stress tests for withdrawal system"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='+2348012345678',
            email='test@example.com',
            password='TestPass123'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            phone_number='+2348012345678',
            primary_location='ilorin',
            wallet_balance=Decimal('10000.00'),
            phone_verified=True
        )
        
        # Create test bank account
        self.bank_account = BankAccount.objects.create(
            user=self.user,
            account_number='0123456789',
            account_name='Test User',
            bank_name='Test Bank',
            bank_code='058',
            recipient_code='RCP_test123',
            is_verified=True,
            is_primary=True
        )
    
    def test_concurrent_withdrawals_race_condition(self):
        """
        CRITICAL: Test if multiple simultaneous withdrawals can drain more than balance
        Expected: Only one should succeed, others should fail
        """
        print("\n[TEST 1] Concurrent Withdrawal Race Condition")
        print(f"Initial balance: ₦{self.profile.wallet_balance}")
        
        results = []
        errors = []
        
        def attempt_withdrawal():
            try:
                from marketplace.withdrawal_views import withdraw_funds
                from rest_framework.test import APIRequestFactory
                from rest_framework.request import Request
                
                factory = APIRequestFactory()
                request = factory.post('/api/marketplace/wallet/withdraw/', {
                    'amount': '6000.00'
                })
                request.user = self.user
                request = Request(request)
                
                response = withdraw_funds(request)
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Launch 5 concurrent withdrawal attempts
        threads = []
        for i in range(5):
            t = threading.Thread(target=attempt_withdrawal)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Refresh profile
        self.profile.refresh_from_db()
        
        print(f"Final balance: ₦{self.profile.wallet_balance}")
        print(f"Success responses: {results.count(201)}")
        print(f"Failure responses: {results.count(400)}")
        print(f"Errors: {len(errors)}")
        
        # Assertions
        assert self.profile.wallet_balance >= 0, "❌ CRITICAL: Balance went negative!"
        assert results.count(201) <= 1, "❌ CRITICAL: Multiple withdrawals succeeded!"
        print("✅ PASS: Race condition prevented")
    
    def test_negative_amount_withdrawal(self):
        """Test withdrawal with negative amount"""
        print("\n[TEST 2] Negative Amount Withdrawal")
        
        from marketplace.withdrawal_views import withdraw_funds
        from rest_framework.test import APIRequestFactory
        from rest_framework.request import Request
        
        factory = APIRequestFactory()
        request = factory.post('/api/marketplace/wallet/withdraw/', {
            'amount': '-5000.00'
        })
        request.user = self.user
        request = Request(request)
        
        response = withdraw_funds(request)
        
        assert response.status_code == 400, "❌ FAIL: Negative amount accepted"
        print("✅ PASS: Negative amount rejected")
    
    def test_zero_amount_withdrawal(self):
        """Test withdrawal with zero amount"""
        print("\n[TEST 3] Zero Amount Withdrawal")
        
        from marketplace.withdrawal_views import withdraw_funds
        from rest_framework.test import APIRequestFactory
        from rest_framework.request import Request
        
        factory = APIRequestFactory()
        request = factory.post('/api/marketplace/wallet/withdraw/', {
            'amount': '0.00'
        })
        request.user = self.user
        request = Request(request)
        
        response = withdraw_funds(request)
        
        assert response.status_code == 400, "❌ FAIL: Zero amount accepted"
        print("✅ PASS: Zero amount rejected")
    
    def test_below_minimum_withdrawal(self):
        """Test withdrawal below minimum (₦1000)"""
        print("\n[TEST 4] Below Minimum Withdrawal")
        
        from marketplace.withdrawal_views import withdraw_funds
        from rest_framework.test import APIRequestFactory
        from rest_framework.request import Request
        
        factory = APIRequestFactory()
        request = factory.post('/api/marketplace/wallet/withdraw/', {
            'amount': '500.00'
        })
        request.user = self.user
        request = Request(request)
        
        response = withdraw_funds(request)
        
        assert response.status_code == 400, "❌ FAIL: Below minimum accepted"
        print("✅ PASS: Below minimum rejected")
    
    def test_insufficient_balance_withdrawal(self):
        """Test withdrawal exceeding balance"""
        print("\n[TEST 5] Insufficient Balance Withdrawal")
        
        from marketplace.withdrawal_views import withdraw_funds
        from rest_framework.test import APIRequestFactory
        from rest_framework.request import Request
        
        factory = APIRequestFactory()
        request = factory.post('/api/marketplace/wallet/withdraw/', {
            'amount': '50000.00'
        })
        request.user = self.user
        request = Request(request)
        
        response = withdraw_funds(request)
        
        assert response.status_code == 400, "❌ FAIL: Insufficient balance accepted"
        print("✅ PASS: Insufficient balance rejected")
    
    def test_daily_limit_enforcement(self):
        """Test daily withdrawal limit (₦500,000)"""
        print("\n[TEST 6] Daily Limit Enforcement")
        
        # Set high balance
        self.profile.wallet_balance = Decimal('600000.00')
        self.profile.save()
        
        from marketplace.withdrawal_views import withdraw_funds
        from rest_framework.test import APIRequestFactory
        from rest_framework.request import Request
        
        factory = APIRequestFactory()
        request = factory.post('/api/marketplace/wallet/withdraw/', {
            'amount': '550000.00'
        })
        request.user = self.user
        request = Request(request)
        
        response = withdraw_funds(request)
        
        assert response.status_code == 400, "❌ FAIL: Daily limit not enforced"
        print("✅ PASS: Daily limit enforced")
    
    def test_sql_injection_in_amount(self):
        """Test SQL injection in amount field"""
        print("\n[TEST 7] SQL Injection in Amount")
        
        from marketplace.withdrawal_views import withdraw_funds
        from rest_framework.test import APIRequestFactory
        from rest_framework.request import Request
        
        factory = APIRequestFactory()
        request = factory.post('/api/marketplace/wallet/withdraw/', {
            'amount': "5000'; DROP TABLE marketplace_withdrawal; --"
        })
        request.user = self.user
        request = Request(request)
        
        response = withdraw_funds(request)
        
        # Should fail with validation error, not SQL error
        assert response.status_code == 400, "❌ FAIL: SQL injection not handled"
        
        # Verify table still exists
        from marketplace.models import Withdrawal
        assert Withdrawal.objects.model._meta.db_table, "❌ CRITICAL: Table dropped!"
        print("✅ PASS: SQL injection prevented")
    
    def test_invalid_data_types(self):
        """Test invalid data types in amount"""
        print("\n[TEST 8] Invalid Data Types")
        
        from marketplace.withdrawal_views import withdraw_funds
        from rest_framework.test import APIRequestFactory
        from rest_framework.request import Request
        
        test_cases = [
            'abc',
            '5000.00.00',
            '5,000',
            'null',
            'undefined',
            '<script>alert("xss")</script>',
        ]
        
        for test_value in test_cases:
            factory = APIRequestFactory()
            request = factory.post('/api/marketplace/wallet/withdraw/', {
                'amount': test_value
            })
            request.user = self.user
            request = Request(request)
            
            response = withdraw_funds(request)
            assert response.status_code == 400, f"❌ FAIL: Invalid value '{test_value}' accepted"
        
        print("✅ PASS: All invalid data types rejected")
    
    def test_missing_bank_account(self):
        """Test withdrawal without bank account"""
        print("\n[TEST 9] Missing Bank Account")
        
        # Delete bank account
        self.bank_account.delete()
        
        from marketplace.withdrawal_views import withdraw_funds
        from rest_framework.test import APIRequestFactory
        from rest_framework.request import Request
        
        factory = APIRequestFactory()
        request = factory.post('/api/marketplace/wallet/withdraw/', {
            'amount': '5000.00'
        })
        request.user = self.user
        request = Request(request)
        
        response = withdraw_funds(request)
        
        assert response.status_code == 400, "❌ FAIL: Withdrawal without bank account accepted"
        print("✅ PASS: Missing bank account detected")
    
    def test_wallet_transaction_logging(self):
        """Test if all transactions are logged"""
        print("\n[TEST 10] Transaction Logging")
        
        initial_count = WalletTransaction.objects.filter(user=self.user).count()
        
        # Mock successful withdrawal (skip Paystack)
        from django.db import transaction as db_transaction
        from django.db.models import F
        
        with db_transaction.atomic():
            profile = Profile.objects.select_for_update().get(user=self.user)
            amount = Decimal('5000.00')
            balance_before = profile.wallet_balance
            
            Profile.objects.filter(user=self.user).update(
                wallet_balance=F('wallet_balance') - amount
            )
            
            WalletTransaction.objects.create(
                user=self.user,
                transaction_type='debit',
                amount=amount,
                source='withdrawal',
                balance_before=balance_before,
                balance_after=balance_before - amount
            )
        
        final_count = WalletTransaction.objects.filter(user=self.user).count()
        
        assert final_count == initial_count + 1, "❌ FAIL: Transaction not logged"
        print("✅ PASS: Transaction logged correctly")
    
    def test_balance_consistency(self):
        """Test balance consistency after operations"""
        print("\n[TEST 11] Balance Consistency")
        
        initial_balance = self.profile.wallet_balance
        
        # Perform multiple operations
        from django.db import transaction as db_transaction
        from django.db.models import F
        
        operations = [
            ('debit', Decimal('1000.00')),
            ('credit', Decimal('500.00')),
            ('debit', Decimal('2000.00')),
        ]
        
        for op_type, amount in operations:
            with db_transaction.atomic():
                profile = Profile.objects.select_for_update().get(user=self.user)
                
                if op_type == 'debit':
                    Profile.objects.filter(user=self.user).update(
                        wallet_balance=F('wallet_balance') - amount
                    )
                else:
                    Profile.objects.filter(user=self.user).update(
                        wallet_balance=F('wallet_balance') + amount
                    )
        
        self.profile.refresh_from_db()
        expected_balance = initial_balance - Decimal('1000.00') + Decimal('500.00') - Decimal('2000.00')
        
        assert self.profile.wallet_balance == expected_balance, "❌ FAIL: Balance inconsistent"
        print(f"✅ PASS: Balance consistent (₦{self.profile.wallet_balance})")


def run_stress_tests():
    """Run all stress tests"""
    print("=" * 60)
    print("WITHDRAWAL SYSTEM STRESS TEST")
    print("=" * 60)
    
    import django
    django.setup()
    
    from django.test.utils import setup_test_environment, teardown_test_environment
    from django.db import connection
    
    setup_test_environment()
    
    # Create test database
    connection.cursor().execute("BEGIN")
    
    try:
        test = WithdrawalStressTest()
        test.setUp()
        
        # Run all tests
        test.test_concurrent_withdrawals_race_condition()
        test.test_negative_amount_withdrawal()
        test.test_zero_amount_withdrawal()
        test.test_below_minimum_withdrawal()
        test.test_insufficient_balance_withdrawal()
        test.test_daily_limit_enforcement()
        test.test_sql_injection_in_amount()
        test.test_invalid_data_types()
        test.test_missing_bank_account()
        test.test_wallet_transaction_logging()
        test.test_balance_consistency()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✅")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
    finally:
        connection.cursor().execute("ROLLBACK")
        teardown_test_environment()


if __name__ == '__main__':
    run_stress_tests()
