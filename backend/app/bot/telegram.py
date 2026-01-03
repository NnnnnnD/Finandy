from telegram import Update
from telegram.ext import ContextTypes
from app.core.database import SessionLocal
from app.models.users import User
from app.models.accounts import Account
from app.models.user_channels import UserChannel
from app.bot.handlers import handle_message


async def on_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user_id = str(update.effective_user.id)
    name = update.effective_user.first_name or "User"

    db = SessionLocal()
    try:
        ch = (
            db.query(UserChannel)
            .filter(
                UserChannel.channel_type == "telegram",
                UserChannel.channel_user_id == telegram_user_id,
            )
            .first()
        )

        if not ch:
            user = User(name=name)
            db.add(user)
            db.flush()

            db.add(UserChannel(
                user_id=user.id,
                channel_type="telegram",
                channel_user_id=telegram_user_id,
                is_primary=True,
            ))
        else:
            user = db.query(User).filter(User.id == ch.user_id).first()

        primary = (
            db.query(Account)
            .filter(Account.user_id == user.id, Account.is_primary == True)
            .first()
        )

        if not primary:
            db.add(Account(
                user_id=user.id,
                name="BCA",
                type="Balance",
                is_primary=True,
            ))

        db.commit()

        await update.message.reply_text(
            "👋 Finandy siap! Akun utama **BCA** aktif 🚀"
        )
    finally:
        db.close()


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return  # 🔥 FIX

    text = update.message.text
    telegram_user_id = str(update.effective_user.id)

    db = SessionLocal()
    try:
        user = (
            db.query(User)
            .join(UserChannel)
            .filter(
                UserChannel.channel_type == "telegram",
                UserChannel.channel_user_id == telegram_user_id,
            )
            .first()
        )
        if not user:
            await update.message.reply_text("Ketik /start dulu ya.")
            return

        accounts = db.query(Account).filter(Account.user_id == user.id).all()

        res = handle_message(
            db=db,
            telegram_user_id=telegram_user_id,
            user_id=user.id,
            text=text,
            user_accounts=accounts,
        )

        if res and "reply" in res:
            await update.message.reply_text(res["reply"])
    finally:
        db.close()
