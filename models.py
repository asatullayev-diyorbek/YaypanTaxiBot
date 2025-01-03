# models.py
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

# Yo'nalish nomini belgilash
directions = {
    "fargona_yaypan": "Farg'ona → Yaypan",
    "yaypan_fargona": "Yaypan → Farg'ona",
    "yaypan_yakatut": "Yaypan → Yakatut",
    "yakatut_yaypan": "Yakatut → Yaypan"
}

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    chat_id = Column(Integer, unique=True, nullable=False)
    phone_number = Column(String)

    # Orders bilan bog'lanish (1:Many munosabati)
    orders = relationship('Order', back_populates='user')

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    direction = Column(String(100))         # Yo'nalish: Farg'ona-Yaypan, Yaypan-Farg'ona, Yaypan-Yakatut, Yakatut-Yaypan
    leave_time = Column(String(20)) # Ketish vaqti: 4:00 - 5:00; ... ; 21:00 - 22:00; different
    person_count = Column(String(10))          # Nechi kishi: 1, 2, 3, 4, Pochta
    location = Column(String(100))          # Lokatsiya (ixtiyoriy)
    gender = Column(String(30))  # Jinsi
    comment = Column(String(300))
    extra_column = Column(Integer)      # Qo'shimcha ma'lumot (ixtiyoriy)

    user = relationship('User', back_populates='orders')  # back_populates bu yerda 'user' ustunini ifodalaydi

    def time_info(self):
        if self.leave_time.isdigit():
            return f"{self.leave_time}:00 - {int(self.leave_time) + 1}:00"
        return "Aniq emas"

    def mail_info(self):
        if self.person_count.isdigit():
            return f"{self.person_count}"
        return "Pochta 📬"

    def male_info(self):
        if self.gender == "male":
            return "Faqat erkak 👨"
        elif self.gender == "female":
            return "Faqat ayol 👩"
        return "Erkak va Ayol 👨‍🦱👩‍🦰"

    def info(self):
        info = [f"ID-{self.id} Buyurtma ma'lumotlari\n"]  # ID ni qo'shish

        # Har bir maydonni tekshirish va qiymat mavjud bo'lsa, qo'shish
        if self.direction:
            info.append(f"🧭 *Yo'nalish*: _{directions[self.direction]}_")
        if self.leave_time:
            info.append(f"⌛ *Ketish vaqti*: _{self.time_info()}_")
        if self.person_count:
            info.append(f"🔢 *Yo'lovchilar soni*: _{self.mail_info()}_")
        if self.location:
            info.append(f"📍 *Lokatsiya*: {self.location}")
        if self.gender:
            info.append(f"🚻 *Jinsi*: _{self.male_info()}_")
        if self.comment:
            info.append(f"💬 *Izoh*: `{self.comment}`")

        return "\n".join(info)

    def info_for_group(self, user: User = None):
        info = [f"ID-{self.id} Buyurtma 🗓 \n"]  # ID ni qo'shish

        # Agar user ma'lumotlari mavjud bo'lsa, ularni qo'shish
        if user:
            info.append("<b>Yo'lovchi ma'lumotlari:</b>")
            info.append(f"👤 <b>Ismi:</b> <a href='tg://user?id={user.chat_id}'>#{user.full_name}</a>")
            info.append(f"📞 <b>Telefon:</b> {user.phone_number}")

        info.append("\n<b>Buyurtma ma'lumotlari</b>")
        # Har bir maydonni tekshirish va qiymat mavjud bo'lsa, qo'shish
        if self.direction:
            info.append(f"🚗 <b>Yo'nalish</b>: <i>{directions[self.direction]}</i>")
        if self.leave_time:
            info.append(f"🕒 <b>Ketish vaqti:</b> <i>{self.time_info()}</i>")
        if self.person_count:
            info.append(f"🔢 <b>Yo'lovchilar soni:</b> <i>{self.mail_info()}</i>")
        if self.location:
            info.append(f"📍 <b>Lokatsiya:</b> <i>{self.location}</i>")
        if self.gender:
            info.append(f"🚻 <b>Jinsi:</b> <i>{self.male_info()}</i>")
        if self.comment:
            info.append(f"💬 <b>Izoh:</b> <code>{self.comment}</code>")

        return "\n".join(info)

    def __repr__(self):
        return f"<Order(user_id={self.user_id}, direction='{self.direction}', person_count={self.person_count}, location='{self.location}', gender='{self.gender}', extra_column='{self.extra_column}')>"

class GroupChatId(Base):
    __tablename__ = 'group_chat_ids'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True, nullable=False)
    group_name = Column(String(255), nullable=False)

    def delete(self):
        session.delete(self)
        session.commit()

    def __repr__(self):
        return f"<GroupChatId(chat_id={self.chat_id}, group_name='{self.group_name}')>"

load_dotenv()
# Database ulanishi
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Jadval yaratish
Base.metadata.create_all(engine)
