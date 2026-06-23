import os
import typing as t
import uuid

from attr import dataclass
from dodopayments import AsyncDodoPayments
from dotenv import load_dotenv
from yookassa import Configuration, Payment
from yookassa.domain.models.payment_data.payment_data import \
    ResponsePaymentData
from yookassa.domain.response import PaymentResponse as YookassaPaymentResponse

load_dotenv()

Configuration.account_id = os.getenv("YOOKASSA_SHOP_ID")
Configuration.secret_key = os.getenv("YOOKASSA_TOKEN")


client = AsyncDodoPayments(
    bearer_token=os.getenv("DODO_PAYMENTS_API_KEY"),
    environment="test_mode",
)


@dataclass
class PaymentResponse:
    is_paid: bool
    cancellation_details: t.Optional[str]
    method: t.Optional[ResponsePaymentData]


class YookassaPayment:
    def __init__(
        self,
        *,
        tariff: str,
        amount: int,
        email: str,
        save_payment_method: bool = False,
        payment_method_id: t.Optional[str] = None,
        create_pay: bool = False
    ):
        self.tariff: str = tariff
        self.amount: int = amount
        self.payment_data = self._create_payment_data(email, save_payment_method, payment_method_id) if create_pay else None
        self.payment_url = self._create_payment_url(email=email, save_payment_method=save_payment_method)

    @property
    def id(self) -> str:
        return self.payment_data.id

    @property
    def get_confirmation_token(self):
        return self.payment_data.confirmation.confirmation_token

    @staticmethod
    def get_payment_response(pay_id: str) -> PaymentResponse:
        payment_instance = Payment.find_one(pay_id)
        return PaymentResponse(
            payment_instance.paid,
            payment_instance.cancellation_details,
            payment_instance.payment_method,
        )

    def _create_payment_data(
        self,
        email: str,
        save_payment_method: bool = False,
        payment_method_id: t.Optional[str] = None,
    ) -> YookassaPaymentResponse:
        if payment_method_id:
            return Payment.create(
                {
                    "amount": {"value": self.amount, "currency": "RUB"},
                    "capture": True,
                    "receipt": {
                        "customer": {
                            "email": f"{email}"
                        },
                        "items": [
                            {
                                "description": f"Тариф {self.tariff}",
                                "quantity": 1,
                                "amount": {
                                    "value": f"{self.amount}",
                                    "currency": "RUB"
                                },
                                "vat_code": 1
                            },
                        ]
                    },
                    "payment_method_id": payment_method_id,
                    "description": f"Fibonacci: тариф {self.tariff} презентаций",
                }
            )

        return Payment.create(
            {
                "amount": {"value": self.amount, "currency": "RUB"},
                "confirmation": {
                    "type": "embedded",
                },
                "receipt": {
                    "customer": {
                        "email": f"{email}"
                    },
                    "items": [
                        {
                            "description": f"Тариф {self.tariff}",
                            "quantity": 1,
                            "amount": {
                                "value": f"{self.amount}",
                                "currency": "RUB"
                            },
                            "vat_code": 1
                        },
                    ]
                },
                "capture": True,
                "description": f"Fibonacci: тариф {self.tariff}",
                "save_payment_method": save_payment_method,
            },
            str(uuid.uuid4()),
        )

    def _create_payment_url(
        self,
        email: str,
        save_payment_method: bool = False
    ) -> str:
        payment_data = Payment.create(
            {
                "amount": {
                    "value": self.amount,
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": "https://t.me/Fibonacci_presentation_bot"
                },
                "capture": True,
                "receipt": {
                    "customer": {
                        "email": f"{email}"
                    },
                    "items": [
                        {
                            "description": f"Тариф {self.tariff}",
                            "quantity": 1,
                            "amount": {
                                "value": f"{self.amount}",
                                "currency": "RUB"
                            },
                            "vat_code": 1
                        },
                    ]
                },
                "description": f"Fibonacci: тариф {self.tariff} - {self.amount}",
                "save_payment_method": save_payment_method
            },
            str(uuid.uuid4())
        )
        return payment_data.confirmation.confirmation_url


class DodoPayments:
    def __init__(
        self,
        *,
        amount: int,
        payment_method_id: str,
        id: str = "dodopayments"
    ):
        self.amount: int = amount
        self.payment_method_id = payment_method_id
        self.id = id

    async def create_payment(self):
        responce = await client.subscriptions.charge(
            subscription_id=self.payment_method_id,
            product_price=round(self.amount/82) * 100,
        )
        self.id = responce.payment_id
        return self.id
