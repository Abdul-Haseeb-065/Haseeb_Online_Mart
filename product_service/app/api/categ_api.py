from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Depends
from app.models.categ_auth_model import Category, Gender, Size # type: ignore
from app.models.product_model import Product, ProductItem# type: ignore
from app.curd.category_curd import create_category_func, add_gender_func, create_size_func, get_categories_func, search_products_by_gender_func, get_genders_func, search_products_by_category_func, search_specific_size_products_func # type: ignore

categ_router = APIRouter()

@categ_router.post("/create_category/", response_model=Category)
def create_category(category: Annotated[Category, Depends(create_category_func)]):
    if not category:
        raise HTTPException(
            status_code=500, detail="Some things went wrong, while creating product.")
    return category


@categ_router.get("/get_categories/", response_model=List[Category])
def get_categories(categories: Annotated[List[Category], Depends(get_categories_func)]):
    if not categories:
        raise HTTPException(
            status_code=500, detail="Some things went wrong, while creating product.")
    return categories


@categ_router.get("/get_products_by_category/", response_model=List[Product])
def search_products_by_category(products: Annotated[List[Product], Depends(search_products_by_category_func)]):
    if not products:
        raise HTTPException(
            status_code=500, detail="Some things went wrong, while creating product.")
    return products


@categ_router.post("/create_gender/", response_model=Gender)
def add_gender(gender: Annotated[Gender, Depends(add_gender_func)]):
    if not gender:
        raise HTTPException(
            status_code=500, detail="Some things went wrong, while creating product.")
    return gender


@categ_router.get("/get_genders/", response_model=List[Gender])
def get_genders(gender: Annotated[List[Gender], Depends(get_genders_func)]):
    if not gender:
        raise HTTPException(
            status_code=500, detail="Some things went wrong, while creating product.")
    return gender


@categ_router.get("/get_products_by_gender/", response_model=Product)
def search_products_by_gender(products: Annotated[List[Product], Depends(search_products_by_gender_func)]):
    if not products:
        raise HTTPException(
            status_code=500, detail="Some things went wrong, while creating product.")
    return products


@categ_router.post("/create_size/", response_model=Size)
def create_size(size: Annotated[Size, Depends(create_size_func)]):
    if not size:
        raise HTTPException(
            status_code=500, detail="Some things went wrong, while creating product.")
    return size


@categ_router.get("/get_specific_size_products/", response_model=List[ProductItem])
def search_specific_size_products(product_items: Annotated[List[ProductItem], Depends(search_specific_size_products_func)]):
    if not product_items:
        raise HTTPException(
            status_code=500, detail="Some things went wrong, while creating product.")
    return product_items
