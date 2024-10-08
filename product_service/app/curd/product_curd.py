from typing import Annotated, List
from fastapi import Depends, HTTPException, File, UploadFile
from sqlmodel import select
from app.main import DB_SESSION # type: ignore
from app.curd.category_curd import search_category_func # type: ignore
from app.models.product_model import Product, ProductItem, ProductFormModel, Stock, ProductSize, ProductImage # type: ignore
from app.utils.admin_auth import admin_verification # type: ignore
from app.s3config.aws_s3 import upload_files_in_s3 # type: ignore
from sqlalchemy import or_


def create_product_func(
    session: DB_SESSION,
    # admin_verification: Annotated[dict, Depends(admin_required)],
    product_details: ProductFormModel,
):
    if not admin_verification:
        raise HTTPException(
            status_code=403, detail="You are not authorized to create a product!"
        )
    if not product_details:
        raise HTTPException(
            status_code=400, detail="Product details not found!"
        )
    print(f"Product Details: f{product_details}")
    product_item_tables: List[ProductItem] = []
    try:
        for product_item in product_details.product_items:
            product_size_tables: List[ProductSize] = [] 
            for product_size in product_item.sizes:
                stock_table = Stock(stock=product_size.stock)
                print(f"Stock Level: {stock_table.stock_level}")
                product_size_schema = ProductSize(
                    size_id=product_size.size, price=product_size.price, stock=stock_table
                )
                product_size_tables.append(product_size_schema)

            product_item_table = ProductItem(
                color=product_item.color,  
                sizes=product_size_tables
            )
            product_item_tables.append(product_item_table)

        print("All ProductItems created: ", product_item_tables)

        product_table = Product(
            product_name=product_details.product_name,
            product_description=product_details.product_description,
            product_type=product_details.product_type,
            duration=product_details.duration,
            gender_id=product_details.gender_id,
            category_id=product_details.category_id,
            product_items=product_item_tables
        )
        session.add(product_table)
        session.commit()
        session.refresh(product_table)
        return product_table

    except Exception as x:
        print("Error while creating Product:", x)
        raise HTTPException(
            status_code=500, detail="An error occurred while creating the product."
        )


def add_images_in_product(
    product_item_id: int,
    session: DB_SESSION,
    images: List[UploadFile] = File(...)
):

    if not admin_verification:
        raise HTTPException(
            status_code=403, detail="You are not authorized to create a product!"
        )
    product_item = session.exec(select(ProductItem)
    .where(ProductItem.item_id == product_item_id)
    ).one_or_none()
    if not product_item:
        raise HTTPException(
            status_code=404, detail=f"Product item not found from id: {product_item_id}")
    image_urls = upload_files_in_s3(images, product_item.product_id)

    product_images_table = [ProductImage(product_image_url=url) 
    for url in image_urls]
    print(f"All Product Images : {product_images_table}")
    product_item.product_images = product_images_table
    session.add(product_item)
    session.commit()
    session.refresh(product_item)
    return f"Images has been successfully added."


def get_product_func(product_id: int, session: DB_SESSION):
    product = session.exec(select(Product)
    .where(Product.product_id == product_id)
    ).one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def get_all_products_func(session: DB_SESSION):
    products = session.exec(select(Product)).all()
    return products


def get_limited_products_func(limit: int, session: DB_SESSION):
    products = session.exec(select(Product).limit(limit)).all()
    return products


def search_products_func(input: str, session: DB_SESSION):

    categories = search_category_func(input, session)
    category_ids = [category.category_id for category in categories]
    if category_ids:
        category_conditions = [Product.category_id ==
                               category_id for category_id in category_ids]

        products_by_category = session.exec(
            select(Product).where(or_(*category_conditions))).all()
    else:
        products_by_category = []

    products_by_input = session.exec(select(Product).where(
        (input in Product.product_name) or (
            input in Product.product_description)
    )).all()

    all_products_set = set(products_by_input).union(products_by_category)
    all_products = list(all_products_set)
    return all_products


def update_product_func(
    product_id: int,
    updated_product: Product, #Product object in the database that want to update,, updated_product object contains the new data    
    session: DB_SESSION,
):
    if not admin_verification:
        HTTPException(status_code=400,
                      detail="You are not authorized to update a product!")
    product = session.exec(select(Product)
    .where(Product.product_id == product_id)).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in updated_product.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def delete_product_func(
    product_id: int,
    session: DB_SESSION,
):

    if not admin_verification:
        HTTPException(status_code=400,
                      detail="You are not authorized to create a product!")
    product = session.exec(select(Product)
    .where(Product.product_id == product_id)
    ).one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(product)
    session.commit()
    return product_id
