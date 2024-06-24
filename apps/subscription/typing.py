from dataclasses import dataclass
from typing import Literal

DATETIME_ISOFORMAT = str


# Объект платежа
@dataclass(frozen=True)
class AmountData:
    value: str
    currency: str = "RUB"


@dataclass(frozen=True)
class ConfirmationRequestData:
    type: Literal["qr"] | Literal["redirect"]
    return_url: None = None  # куда пользователь вернётся после оплаты
    locale: str = "ru_RU"


@dataclass(frozen=True)
class ConfirmationResponseData:
    type: Literal["qr"] | Literal["redirect"]
    confirmation_url: str  # ссылка для подтверждения платежа
    locale: str = "ru_RU"


# для сериализации и таймхинтинга во вьюхе
@dataclass(frozen=True)
class CreatePaymentResponseData:
    id: str
    status: Literal["pending"] | Literal["waiting_for_capture"] | Literal["succeeded"]
    amount: AmountData
    created_at: DATETIME_ISOFORMAT
    confirmation: ConfirmationResponseData
    paid: bool
    test: bool
    metadata: dict[Literal["user_profile_id"], int]


# создание платежа


@dataclass(frozen=True)
class ItemData:
    description: str
    amount: AmountData
    vat_code: int = 1
    quantity: str = "1"


@dataclass(frozen=True)
class ReceiptData:
    customer: dict[Literal["email"], str]
    items: list[ItemData]


@dataclass(frozen=True)
class CreatePaymentData:
    amount: AmountData
    confirmation: ConfirmationRequestData
    metadata: dict[Literal["user_profile_id"], int]
    receipt: ReceiptData
    save_payment_method: bool = False  # возможность провести платёж ещё раз без подтверждения
    capture: bool = True  # авто-проведение поступившего платежа


@dataclass(frozen=True)
class CreateRecurrentPaymentData:
    amount: AmountData
    metadata: dict[Literal["user_profile_id"], int]
    payment_method_id: str
    save_payment_method: bool = True  # возможность провести платёж ещё раз без подтверждения
    capture: bool = True


@dataclass(frozen=True)
class CreatePaymentViewRequestData:
    subscription_id: int
    confirmation: ConfirmationRequestData
    user_profile_id: int


@dataclass
class CreatePaymentViewResponseData:
    subscription_id: int
    confirmation: ConfirmationResponseData
    user_profile_id: int


# вебхуки
@dataclass(frozen=True)
class WebHookRequest:
    event: str
    object: dict
    type: str = "notification"


@dataclass
class SubIdSerializer:
    subscription_id: int
    redirect_url: str | None = None
