import google.generativeai as genai
from backend.config import settings
from sqlalchemy.orm import Session
import backend.models as models

# Configure Gemini with our API key if present
if settings.GEMINI_API_KEY:
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
    except Exception:
        pass


def build_context(db: Session, user=None):
    """
    Builds structured product and order context for AI queries
    """
    products = db.query(models.Product).all()

    product_lines = []
    for p in products:
        product_lines.append(
            f"[ID:{p.id}] {p.name} ({p.brand}) | Category: {p.category} | "
            f"Price: ₹{p.price} | Stock: {p.stock} | Rating: {p.rating}★ | "
            f"Desc: {p.description}"
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
                items_str = ", ".join([f"{item.product.name} (x{item.quantity})" for item in o.order_items if item.product])
                order_lines.append(
                    f"- Order #{o.id} | Status: {o.status.upper()} | Payment: {o.payment_status} | "
                    f"Total: ₹{o.total_amount} | Items: [{items_str}] | Date: {o.created_at.strftime('%Y-%m-%d')}"
                )
            order_text = f"User's recent orders:\n" + "\n".join(order_lines)
        else:
            order_text = "User has no order history yet."

    return products, product_text, order_text


def fallback_bot_response(message: str, products, user, order_text: str) -> str:
    """
    Smart fallback AI assistant engine when external LLM API is unconfigured/unavailable
    """
    msg_lower = message.lower()

    # Order tracking query
    if "order" in msg_lower or "track" in msg_lower or "status" in msg_lower:
        if not user:
            return "Please log in to your Nexora account to view and track your order history!"
        if "no order" in order_text.lower():
            return "You haven't placed any orders yet. Explore our top tech catalog to place your first order!"
        return f"Here is your recent order details:\n\n{order_text}\n\nYou can also view full progress on your Orders page!"

    # Comparison query
    if "compare" in msg_lower or "vs" in msg_lower:
        matched = [p for p in products if p.name.lower() in msg_lower or p.brand.lower() in msg_lower or p.category.lower() in msg_lower]
        if len(matched) >= 2:
            p1, p2 = matched[0], matched[1]
            return (
                f"### Comparison: {p1.name} vs {p2.name}\n\n"
                f"- **Price**: ₹{p1.price:,} vs ₹{p2.price:,}\n"
                f"- **Rating**: {p1.rating}★ vs {p2.rating}★\n"
                f"- **Stock**: {p1.stock} units vs {p2.stock} units\n"
                f"- **Highlights**: {p1.description[:80]}... vs {p2.description[:80]}...\n\n"
                f"Both are excellent choices in our catalog!"
            )

    # Search / Recommendation filter queries
    matches = []
    for p in products:
        if (p.name.lower() in msg_lower or 
            p.category.lower() in msg_lower or 
            p.brand.lower() in msg_lower or
            any(word in p.description.lower() for word in msg_lower.split() if len(word) > 3)):
            matches.append(p)

    if matches:
        top_items = matches[:3]
        lines = [f"I found {len(matches)} matching product(s) for you:"]
        for item in top_items:
            lines.append(f"• **{item.name}** ({item.brand}) - ₹{item.price:,} | Rating: {item.rating}★\n  _{item.description[:90]}_...")
        lines.append("\nClick on any product card or visit the catalog to add them directly to your cart!")
        return "\n\n".join(lines)

    # Default friendly greeting
    return (
        f"Welcome to Nexora AI Assistant! ⚡\n\n"
        f"I can help you with:\n"
        f"1. Finding top tech products (Laptops, Phones, Audio, Accessories)\n"
        f"2. Comparing specs and prices\n"
        f"3. Tracking your active orders\n"
        f"4. Answering questions about inventory and checkout\n\n"
        f"How can I assist your shopping experience today?"
    )


def get_ai_response(message: str, db: Session, user=None) -> str:
    """
    Generates intelligent response using Gemini API with context, falling back to local engine if needed
    """
    products, product_text, order_text = build_context(db, user)

    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
        return fallback_bot_response(message, products, user, order_text)

    system_prompt = f"""You are the Nexora AI Assistant for Nexora, a futuristic electronics e-commerce store.

Your role:
- Provide friendly, crisp, expert recommendations for laptops, smartphones, headphones, displays, smartwatches, and accessories.
- Compare products side-by-side when asked.
- Help users locate items, check prices in ₹ (INR), and check stock.
- Track user orders accurately using their order history context.
- Keep responses engaging, modern, formatted in Markdown.

Available Products:
{product_text}

User Order Information:
{order_text}

Rules:
- Recommend only from the catalog above.
- Always quote exact INR prices with ₹.
- If order status is queried, refer to user's order list accurately.
"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content(f"{system_prompt}\n\nUser Question: {message}")
        return response.text
    except Exception as e:
        return fallback_bot_response(message, products, user, order_text)