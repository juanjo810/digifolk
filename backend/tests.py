from app.api.routes.piece_route import piece_excel_to_sqlalchemy, excel_controller
from app.api.routes.col_route import col_excel_to_sqlalchemy

import sys

if __name__ == "__main__":
    if sys.argv[1] == 'excel_to_piece':
        piece_excel_to_sqlalchemy(user_id=1)
    elif sys.argv[1] == 'excel_to_col':
        col_excel_to_sqlalchemy()
    elif sys.argv[1] == 'excel_controller':
        excel_controller(user_id=1)
