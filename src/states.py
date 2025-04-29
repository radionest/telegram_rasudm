from aiogram.fsm.state import State, StatesGroup


class RegisterUser(StatesGroup):
    """States for user registration"""
    need_registration = State()
    get_agreement = State()
    wait_agreement = State()
    waiting_phone = State()
    waiting_phone_changed_user = State()
    

class EditActivePhones(StatesGroup):
    waiting_table = State()
    
class TargetGroupSelection(StatesGroup):
    target_selected = State()