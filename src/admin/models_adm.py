from aiogram.dispatcher.filters.state import State, StatesGroup


class Farmstead(StatesGroup):

    name = State()
    address = State()
    photo = State()
    destination = State()
    rooms_number = State()
    services = State()
    price = State()
    is_water_near = State()
    unique_services = State()
    contact_phone = State()
    contact_email = State()
    gps_number = State()
    website_link = State()


class AdmPassword(StatesGroup):

    admin_password = State()
    new_admin_password = State()
    new_admin_password_repead = State()
    holder_login = State()
    holder_login_set = State()