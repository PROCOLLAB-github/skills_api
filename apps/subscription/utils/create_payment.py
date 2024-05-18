from dataclasses import asdict

import requests
from yookassa import Payment
from subscription.mapping import CreatePaymentData, CreatePaymentResponseData, CreateRecurrentPaymentData


def create_payment(payload: CreatePaymentData | CreateRecurrentPaymentData) -> CreatePaymentResponseData:
    try:
        response_data = Payment.create(asdict(payload))
        return CreatePaymentResponseData(
            id=response_data["id"],
            status=response_data["status"],
            amount=response_data["amount"],
            created_at=response_data["created_at"],
            confirmation=response_data["confirmation"],
            paid=response_data["paid"],
            test=response_data["test"],
            metadata=response_data["metadata"],
        )
    except requests.exceptions.HTTPError:
        pass
