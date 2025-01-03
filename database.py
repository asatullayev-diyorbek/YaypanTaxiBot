# database.py
from models import session, User, Order, GroupChatId

def check_user(chat_id):
    """Foydalanuvchini tekshiradi"""
    user = session.query(User).filter(User.chat_id == chat_id).first()
    return user is not None

def add_user(chat_id):
    """Yangi foydalanuvchini qo'shadi"""
    new_user = User(chat_id=chat_id)
    session.add(new_user)
    session.commit()

def get_user(chat_id):
    return session.query(User).filter(User.chat_id == chat_id).first()

def save_phone_number(chat_id: int, full_name: str, phone_number: str):
    # Agar telefon raqam boshida "+" belgisi bo'lmasa, qo'shing
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number

    new_user = User(chat_id=chat_id, full_name=full_name, phone_number=phone_number)
    session.add(new_user)

    session.commit()
    return new_user


# Order
def new_order(user: User):
    """Yangi buyurtma qo'shadi"""
    order = Order(user_id=user.id, extra_column=1)
    session.add(order)
    session.commit()
    return order


def get_order(user):
    """Foydalanuvchi buyurtmasini olish"""
    order = session.query(Order).filter(Order.user_id == user.id).order_by(Order.id.desc()).first()
    if order:
        return order
    return None

def update_order(order: Order, **kwargs):
    """Buyurtmani o'zgartirish"""
    for key, value in kwargs.items():
        setattr(order, key, value)
    session.commit()
    return order


def delete_order(order: Order):
    """Buyurtmani bekor qilish"""
    order.extra_column = 0
    session.commit()

def get_group():
    """Guruhlar olish"""
    groups = session.query(GroupChatId).first()
    return groups

def add_group(chat_id: int, group_name: str):
    """Yangi guruh qo'shadi"""
    new_group = GroupChatId(chat_id=chat_id, group_name=group_name)
    session.add(new_group)
    session.commit()
    return new_group
