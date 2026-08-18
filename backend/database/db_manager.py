import mysql.connector

from mysql.connector import Error

from backend.config import settings
from backend.exceptions import DatabaseException
from backend.utils.logger import get_logger


logger = get_logger(__name__)


class DatabaseConnection:
    
    _instance = None

    def __new__(cls):

        if cls._instance is None:

            cls._instance = super(
                DatabaseConnection,
                cls
            ).__new__(cls)

            cls._instance.oltp_connection = None
            cls._instance.olap_connection = None

        return cls._instance

    def _create_connection(
        self,
        database_name
    ):

        try:

            logger.info(
                "Connecting to database: %s",
                database_name
            )

            connection = mysql.connector.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database=database_name
            )

            if connection.is_connected():

                logger.info(
                    "Successfully connected to %s.",
                    database_name
                )

                return connection

            raise DatabaseException(
                f"Could not connect to {database_name}."
            )

        except Error as e:

            logger.exception(
                "Database connection failed: %s",
                database_name
            )

            raise DatabaseException(
                f"Database connection failed: {e}"
            )

    def connect(self, database="oltp"):

        database = database.lower()

        # =====================================================
        # OLTP
        # =====================================================

        if database == "oltp":

            if self.oltp_connection is None:

                self.oltp_connection = (
                    self._create_connection(
                        settings.DB_OLTP
                    )
                )

            else:

                try:

                    if not self.oltp_connection.is_connected():

                        self.oltp_connection = (
                            self._create_connection(
                                settings.DB_OLTP
                            )
                        )

                except Exception:

                    logger.warning(
                        "OLTP connection is in an invalid state. "
                        "Creating a new connection."
                    )

                    try:

                        self.oltp_connection.close()

                    except Exception:

                        pass

                    self.oltp_connection = (
                        self._create_connection(
                            settings.DB_OLTP
                        )
                    )

            return self.oltp_connection


        if database == "olap":

            if self.olap_connection is None:

                self.olap_connection = (
                    self._create_connection(
                        settings.DB_OLAP
                    )
                )

            else:

                try:

                    if not self.olap_connection.is_connected():

                        self.olap_connection = (
                            self._create_connection(
                                settings.DB_OLAP
                            )
                        )

                except Exception:

                    logger.warning(
                        "OLAP connection is in an invalid state. "
                        "Creating a new connection."
                    )

                    try:

                        self.olap_connection.close()

                    except Exception:

                        pass

                    self.olap_connection = (
                        self._create_connection(
                            settings.DB_OLAP
                        )
                    )

            return self.olap_connection


        raise DatabaseException(
            "Database must be either 'oltp' or 'olap'."
        )


    def get_cursor(
        self,
        database="oltp"
    ):

        try:

            connection = self.connect(
                database
            )

            # IMPORTANT:
            # buffered=True prevents
            # "Unread result found" errors
            # when the Singleton connection is reused.

            return connection.cursor(
                dictionary=True,
                buffered=True
            )

        except Exception as e:

            logger.exception(
                "Failed to create database cursor."
            )

            raise DatabaseException(
                f"Failed to create cursor: {e}"
            )


    def commit(
        self,
        database="oltp"
    ):

        try:

            connection = self.connect(
                database
            )

            connection.commit()

            logger.info(
                "Transaction committed on %s.",
                database
            )

        except Exception as e:

            logger.exception(
                "Commit failed on %s.",
                database
            )

            raise DatabaseException(
                f"Commit failed: {e}"
            )


    def rollback(
        self,
        database="oltp"
    ):

        try:

            connection = self.connect(
                database
            )

            connection.rollback()

            logger.info(
                "Transaction rolled back on %s.",
                database
            )

        except Exception as e:

            logger.exception(
                "Rollback failed on %s.",
                database
            )


    def close(self):

        if self.oltp_connection:

            try:

                if self.oltp_connection.is_connected():

                    self.oltp_connection.close()

                    logger.info(
                        "OLTP connection closed."
                    )

            except Exception:

                logger.exception(
                    "Error while closing OLTP connection."
                )

        if self.olap_connection:

            try:

                if self.olap_connection.is_connected():

                    self.olap_connection.close()

                    logger.info(
                        "OLAP connection closed."
                    )

            except Exception:

                logger.exception(
                    "Error while closing OLAP connection."
                )


        self.oltp_connection = None
        self.olap_connection = None





