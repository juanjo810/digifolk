from fastapi import APIRouter, Request, Depends
from fastapi_sqlalchemy import db
from app.models.items import ListItem
from app.api.schemas.items_schema import ListItemSc


router = APIRouter()

## CREATE COLLECTION
@router.post("/createItem")
def create_item(item: ListItemSc):
   
    ## IMPORTANT! A way to detect same collection???? #############
    n=db.session.query(ListItem).filter(ListItem.id==item.id).filter(ListItem.type_item==item.type_item).count()
    
    if n >0: 
        return [{"msg": "Field already created"}]
    else: 
        db_item=ListItem(id=item.id,name=item.name,type_item=item.type_item)
        db.session.add(db_item)
        db.session.commit()
        db_item=db.session.query(ListItem).filter(ListItem.id==item.id).filter(ListItem.type_item==item.type_item).first()
        return db_item
    

#EDIT COLLECTION
@router.post("/editItem")
def edit_item(item: ListItemSc):
    
    ## We need the id to know identify the piece
    if (item.id!=""):
        old_item=db.session.query(ListItem).filter(ListItem.id==item.id).first()
    if old_item:
        # Update the data using Pydantic
        update_data = item.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(old_item, key, value)

        # Commit the changes
        db.session.commit()
        #db.session.refresh(old_item)
        return old_item

    return [{"msg": "Item not found"}]

## REMOVE COLLECTION
@router.delete("/removeItem")
def delete_item(id: int, type_item: int):
    if id != "":
        n=db.session.query(ListItem).filter(ListItem.id==id).filter(ListItem.type_item==type_item).delete()
        #return n
         ## Retrieve items with id and remove them
        #n.delete()
        db.session.commit()
        return [{"msg": "Rm done"}]
    else:
        return [{"msg": "Collection not found"}]


# GET COLLECTIONS
@router.get("/getItemById")
def get_col(id: int = None):

    if id is not None:
        item=db.session.query(ListItem).filter(ListItem.id==id).all()
    else:
        return [{"msg": "Provide Title, Creator or id"}]
    if len(item)==0:
        return [{"msg": "No collection with such data"}]
    return item


#GET LIST OF COLLECTIONS
@router.get("/getListForType")
def get_list_for_type(type_item : int):
    ##Retrieve also songbooks
    n=db.session.query(ListItem).filter(ListItem.type_item==type_item).all()
    return n


#GET PIECES FROM COLLECTION
@router.get("/getListItems")
def get_items():
    list_i=db.session.query(ListItem).all()
    return list_i
    
    