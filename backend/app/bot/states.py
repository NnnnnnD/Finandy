from enum import Enum

class BotState(str, Enum):
    IDLE = "idle"
    AWAIT_CONFIRM = "await_confirm"
    AWAIT_PAYMENT_SOURCE = "await_payment_source"
    CORRECT_SELECT_TX = "correct_select_tx"
    CORRECT_APPLY_EDIT = "correct_apply_edit"
    CORRECT_CONFIRM_UPDATE = "correct_confirm_update"

