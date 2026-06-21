import google.generativeai as genai
from backend.config import settings
from sqlalchemy.orm import Session
import backend.models as models

# Configure Gemini with our API key
genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash-lite")


def build_context(db: Session, user=None) -> str:
    """
    Builds a text summary of products and user's orders
    This gets injected into the AI's system prompt so it
    knows what products exist and can answer order questions
    """
    products = db.query(models.Product).all()

    product_lines = []
    for p in products:
        product_lines.append(
            f"- {p.name} ({p.brand}) | Category: {p.category} | "
            f"Price: ₹{p.price} | Stock: {p.stock} | Rating: {p.rating}"
        )
    product_text = "\n".join(product_lines)

    order_text = "User is not logged in."
    if user:
        orders = db.query(models.Order).filter(
            models.Order.user_id == user.id
        ).order_by(models.Order.created_at.desc()).limit(5).all()

        if orders:
            order_lines = []
            for o in orders:
                order_lines.append(
                    f"- Order #{o.id} | Status: {o.status} | "
                    f"Total: ₹{o.total_amount} | Date: {o.created_at.strftime('%Y-%m-%d')}"
                )
            order_text = f"User's recent orders:\n" + "\n".join(order_lines)
        else:
            order_text = "User has no orders yet."

    return product_text, order_text


def get_ai_response(message: str, db: Session, user=None) -> str:
    """
    Sends user message to Gemini along with product catalog
    and order history as context, returns AI's reply
    """
    product_text, order_text = build_context(db, user)

    system_prompt = f"""You are a helpful shopping assistant for Nexora, an electronics e-commerce store.

Your job:
- Help users find products that match what they're looking for
- Answer questions about product specs, prices, and availability
- Help users check their order status
- Compare products when asked
- Be friendly, concise, and helpful

Available products:
{product_text}

{order_text}

Rules:
- Only recommend products from the list above
- Always mention exact prices in ₹ (INR)
- If asked about something not in the catalog, politely say it's not available
- Keep responses short and conversational, like a helpful store assistant
- If user asks about their orders, use the order information provided
"""

    try:
        chat = model.start_chat(history=[])
        response = chat.send_message(f"{system_prompt}\n\nUser question: {message}")
        return response.text
    except Exception as e:
        return f"Sorry, I'm having trouble responding right now. Please try again. (Error: {str(e)})"