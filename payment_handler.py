from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def send_payment_button(update, context):
    """Отправка кнопки с ссылкой на оплату."""
    payment_url = "https://example.com/pay"  # Временный валидный URL, заменить на реальную ссылку позже
    if not payment_url.startswith(('http://', 'https://')):
        payment_url = "https://example.com/pay"  # Fallback на валидный URL
    keyboard = [
        [InlineKeyboardButton("Перейти к оплате", url=payment_url)],
        [InlineKeyboardButton("Домой", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Спасибо! Регистрация завершена. Ожидайте подтверждения.', reply_markup=reply_markup)