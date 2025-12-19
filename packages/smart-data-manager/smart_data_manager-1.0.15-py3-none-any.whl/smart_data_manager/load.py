import pandas as pd
import sys
import logging
from sqlalchemy.exc import SQLAlchemyError
from .db import get_engine

# ----------------------------
# Logging Setup
# ----------------------------
logger = logging.getLogger("load")
logger.setLevel(logging.DEBUG)

# Console handler - Redirects to Azure Log Stream
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)

# NOTE: Removed fh = logging.FileHandler("load.log") to fix OSError: [Errno 30]
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)

logger.addHandler(ch)

# ----------------------------
# Load Function
# ----------------------------

def load_table(df: pd.DataFrame, table_name: str, if_exists="replace"):
    """
    Loads a DataFrame into SQL Server.

    Args:
        df (pd.DataFrame): Data to load
        table_name (str): Destination table
        if_exists (str): "replace", "append", or "fail"
    """
    engine = get_engine()

    try:
        if df is None or df.empty:
            logger.warning(f"Skipping load for '{table_name}': DataFrame is empty.")
            return

        logger.info(f"Loading '{table_name}' ({len(df)} rows) using mode: {if_exists}...")
        
        # to_sql handles the bulk insertion
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists=if_exists,
            index=False,
            chunksize=1000 # Better memory management for larger loads
        )
        logger.info(f"Successfully loaded table: {table_name}")

    except SQLAlchemyError as e:
        logger.error(f"❌ Failed loading table '{table_name}': {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error loading '{table_name}': {e}")


# ----------------------------
# Full Load Pipeline (Star Schema)
# ----------------------------

def load_transformed_schema(
    dim_customers,
    dim_products,
    dim_date,
    fact_orders,
    fact_order_items,
    mode="replace"
):
    """
    Loads all transformed tables into SQL Server in correct FK order.
    Dimensions must be loaded before Facts to maintain referential integrity.
    """

    logger.info("=== Starting Load Phase ===")

    # Load Dimensions first
    # 
    load_table(dim_customers, "DimCustomers", if_exists=mode)
    load_table(dim_products, "DimProducts", if_exists=mode)
    load_table(dim_date, "DimDate", if_exists=mode)

    # Load Facts afterwards
    load_table(fact_orders, "FactOrders", if_exists=mode)
    load_table(fact_order_items, "FactOrderItems", if_exists=mode)

    logger.info("=== Load Phase Complete ===")


# ----------------------------
# Optional: run standalone
# ----------------------------
if __name__ == "__main__":
    logger.info("load.py should be called from the ETL pipeline, not directly.")