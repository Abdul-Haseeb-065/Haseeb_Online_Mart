from fastapi import HTTPException
from sqlmodel import select
from app.models.cart_models import Cart, CartItem, CartModel, CartUpdateModel # type: ignore
from app.main import DB_SESSION # type: ignore


def add_cart_item_func(cart_details: CartModel, session: DB_SESSION):
    cart_by_user = session.exec(select(Cart).where(
        Cart.user_id == cart_details.user_id)).one_or_none()

    if cart_by_user:
        cart_item = session.exec(
            select(CartItem)
            .where(
                CartItem.cart_id == cart_by_user.cart_id,
                CartItem.product_size_id == cart_details.product_size_id
            )
        ).one_or_none()

        if cart_item:
            cart_item.quantity += cart_details.quantity
        else:
            cart_item = CartItem(
                cart_id=cart_by_user.cart_id,
                product_item_id=cart_details.product_item_id,
                product_size_id=cart_details.product_size_id,
                quantity=cart_details.quantity
            )
            session.add(cart_item)
    else:
        cart_item = CartItem(
            product_item_id=cart_details.product_item_id,
            product_size_id=cart_details.product_size_id,
            quantity=cart_details.quantity
        )
        cart_table = Cart(
            user_id=cart_details.user_id,
            cart_items=[cart_item]
        )
        session.add(cart_table)
    session.commit()
    return "Item has been added successfully in Cart." if cart_by_user else "Cart has been created successfully."


# update specific item quantity in cart:
def update_cart_item_func(cart_details: CartUpdateModel, session: DB_SESSION):
    cart_item = session.get(CartItem, cart_details.cart_item_id)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart Item not found.")
    if cart_details.quantity <= 0:
        raise HTTPException(status_code=400, detail="Please add quantity ")
    session.add(cart_item)
    session.commit()
    session.refresh(cart_item)
    return cart_item


# delete specific item from cart:
def delete_cart_item_func(cart_item_id: int, session: DB_SESSION):
    cart_item = session.get(CartItem, cart_item_id)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart Item not found.")
    session.delete(cart_item)
    session.commit()
    session.refresh(cart_item)
    return "Cart Item has been successfully deleted."


# get item details from cart:
def get_cart_details_func(user_id: int, session: DB_SESSION):
    cart_by_user = session.exec(select(Cart).where(
        Cart.user_id == user_id)).one_or_none()
    if not cart_by_user or not (len(cart_by_user.cart_items) > 0):
        raise HTTPException(
            status_code=404, detail="You have an empty cart.")
    cart_items = [cart_item.model_dump(exclude_unset=True)
                  for cart_item in cart_by_user.cart_items]
    return {
        "cart_details": cart_by_user.model_dump(),
        "cart_items_details": cart_items
    }
