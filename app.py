import sys
import psycopg2
import os

from PyQt5.QtWidgets import QMainWindow,QApplication, QWidget, QAction, QTableWidget, QTableWidgetItem, QVBoxLayout
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QIcon, QPixmap
from dotenv import load_dotenv

qtCreatorFile = "app.ui"

# Load UI and base class
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

def get_connection():
    """Return a new connection using environment variables."""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def run_sql_file(filename):
    """Execute all SQL commands in a file."""
    conn = get_connection()
    cur = conn.cursor()
    
    with open(filename, 'r', encoding='utf-8') as f:
        sql = f.read()
        cur.execute(sql)  # runs all SQL in one go if separated by semicolons
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"{filename} executed successfully.")

class app(QMainWindow):
    def __init__(self):
        super(app, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Page 1, Connect signals 
        self.loadStateList()
        self.ui.stateList.currentTextChanged.connect(self.stateChanged)
        self.ui.cityList.itemSelectionChanged.connect(self.cityChanged)
        self.ui.zipcodeList.itemSelectionChanged.connect(self.zipcodeChanged)
        self.ui.categoryList.itemSelectionChanged.connect(self.categoryChanged)
        self.ui.bname.textChanged.connect(self.dynamicBusinessSearch)
        self.ui.refreshButton.clicked.connect(self.refresh)

    # Run query and return results
    def executeQuery(self, sql_str):
        try:
            # Connect to PostgreSQL database
           conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"))
        except:
            print('Unable to connect to the databse')

        cur = conn.cursor()
        cur.execute(sql_str)
        result = cur.fetchall()
        conn.close()
        return result
    
    # Update the main business table with query results
    def updateBusinessTable(self, results):
        self.ui.businessTable.clearContents()
        self.ui.businessTable.setRowCount(len(results))
        self.ui.businessTable.setColumnCount(6)
        self.ui.businessTable.setHorizontalHeaderLabels(["Name", "Address", "City", "Rating", "Reviews", "Check-ins"])
        for i, row in enumerate(results):
            for j, val in enumerate(row):
                self.ui.businessTable.setItem(i, j, QTableWidgetItem(str(val)))

    # Fill state dropdown
    def loadStateList(self):
        self.ui.stateList.clear()
        sql_str = "SELECT distinct state FROM business ORDER BY state;"
        try:
            results = self.executeQuery(sql_str)
            for row in results:
                self.ui.stateList.addItem(row[0])
        except:
            print("Query failed")
        self.ui.stateList.setCurrentIndex(-1)
        self.ui.stateList.clearEditText()

    # When state is selected show cities
    def stateChanged(self):
        self.ui.cityList.clear()
        self.ui.zipcodeList.clear()
        self.ui.categoryList.clear()

        state = self.ui.stateList.currentText()
        if self.ui.stateList.currentIndex() >= 0:
            # Get cities for the selected state
            sql_str = "SELECT DISTINCT city FROM business WHERE state = '" + state + "' ORDER BY city;"
            results = self.executeQuery(sql_str)
            for row in results:
                self.ui.cityList.addItem(row[0])

            # Get businesses in the selected state
            sql_str = "SELECT name, address, city, ROUND(reviewrating::numeric, 2), review_count, numcheckins FROM business WHERE state = '" + state + "' ORDER BY name;"
            results = self.executeQuery(sql_str)
            self.updateBusinessTable(results)

    # When city is selected show zipcodes
    def cityChanged(self):
        if (self.ui.stateList.currentIndex() >= 0) and (len(self.ui.cityList.selectedItems()) > 0):
            self.ui.zipcodeList.clear()
            self.ui.categoryList.clear()

            state = self.ui.stateList.currentText()
            city = self.ui.cityList.selectedItems()[0].text()

            # Get zipcodes for selected state and city
            sql_str = "SELECT DISTINCT zipcode FROM Business WHERE state ='" + state + "' AND city ='" + city + "' ORDER BY zipcode;"
            results = self.executeQuery(sql_str) 
            for row in results:
                    self.ui.zipcodeList.addItem(row[0])

            # Get businesses for selected state and city
            sql_str = "SELECT name, address, city, ROUND(reviewrating::numeric, 2), review_count, numCheckins FROM business WHERE state = '" + state + "' AND city = '" + city + "' ORDER BY name;"
            results = self.executeQuery(sql_str)
            self.updateBusinessTable(results)

    # When zipcode is selected show categories and businesses
    def zipcodeChanged(self):
        self.ui.categoryList.clear()
        if not self.ui.zipcodeList.selectedItems():
            return
        zipcode = self.ui.zipcodeList.selectedItems()[0].text()

        # Display zipcode data
        self.displayZipcodeData(zipcode)

        # Load categories for the selected zipcode
        sql_str = "SELECT DISTINCT c.category_name FROM Business b JOIN Categories c on b.business_id = c.business_id WHERE b.zipcode = '" + zipcode + "' ORDER BY c.category_name;"
        results = self.executeQuery(sql_str)
        for row in results:
            self.ui.categoryList.addItem(row[0])

        state =self.ui.stateList.currentText()

        # Get businesses for zipcode
        sql_str = "SELECT name, address, city, ROUND(reviewrating::numeric, 2), review_count, numCheckins FROM business WHERE zipcode = '" + zipcode + "'"

        if state:
            sql_str += f" AND state = '" + state + "'"
        sql_str +=" ORDER BY name;"

        results = self.executeQuery(sql_str)
        self.updateBusinessTable(results)

    # Handler when a category is selected it will filter businesses by category and search input
    def categoryChanged(self):
        if not self.ui.categoryList.selectedItems():
            self.dynamicBusinessSearch()
            return
        category = self.ui.categoryList.selectedItems()[0].text()

        if not self.ui.zipcodeList.selectedItems():
            return
        zipcode = self.ui.zipcodeList.selectedItems()[0].text()
        search_term = self.ui.bname.text()

        sql_str = ("SELECT b.name, b.address, b. city, ROUND(b.reviewrating::numeric, 2), b.review_count, b.numCheckins "
                  "FROM business b JOIN categories c ON b.business_id = c.business_id WHERE b.zipcode = '" + zipcode + "' "
                  "AND c.category_name = '" + category + "' AND b.name ILIKE '%" + search_term + "%' ORDER BY b.name;"
        )
        results = self.executeQuery(sql_str)

        self.ui.businessTable.clearContents()
        self.ui.businessTable.setRowCount(len(results))
        self.ui.businessTable.setColumnCount(6)
        self.ui.businessTable.setHorizontalHeaderLabels(["name", "Address", "City", "Rating", "Reviews", "Check-ins"])

        for i, row in enumerate(results):
            for j, value in enumerate(row):
                self.ui.businessTable.setItem(i, j, QTableWidgetItem(str(value)))


    # Search for businesses based on input
    def dynamicBusinessSearch(self):
        self.ui.businessTable.setRowCount(0)
        if self.ui.zipcodeList.selectedItems():
            zipcode = self.ui.zipcodeList.selectedItems()[0].text()
            search_term = self.ui.bname.text()
            sql_str = "SELECT name, address, city, ROUND(reviewrating::numeric, 2), review_count, numCheckins FROM Business WHERE zipcode = '" + zipcode + "' AND name ILIKE '%" + search_term + "%' ORDER BY name;" 
            results = self.executeQuery(sql_str)

            if results:
                self.ui.businessTable.setColumnCount(6)
                self.ui.businessTable.setHorizontalHeaderLabels(["Name", "Address", "City", "Reviews", "Check-ins"])
                self.ui.businessTable.setRowCount(len(results))

                for i, row in enumerate(results):
                        for j, val in enumerate(row):
                            self.ui.businessTable.setItem(i, j, QTableWidgetItem(str(val)))

    # Helper method to populate QTableWidget from app with data
    def populate_table(self, table_widget, data, headers=None):
        table_widget.setRowCount(len(data))
        table_widget.setColumnCount(len(data[0]) if data else 0)

        if headers:
            table_widget.setHorizontalHeaderLabels(headers)

        for row_index, row in enumerate(data):
            for col_index, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                table_widget.setItem(row_index, col_index, QTableWidgetItem(str(value)))

    # Refresh popular and successful business tables for selected zipcode
    def refresh(self, checked=None):
        selected = self.ui.zipcodeList.selectedItems()
        if not selected:
            return
        zipcode = selected[0].text()
        
        # Query popular businesses in zipcode
        sql_popular = ("SELECT pb.name, b.address, b.city "
        "FROM PopularBusinesses pb JOIN Business b ON pb.business_id = b.business_id WHERE b.zipcode = '" + zipcode + "';"
        )
        
        # Query successful businesses in zipcode
        sql_successful = ("SELECT sb.name, b.address, b.city, ROUND(b.reviewrating::numeric, 2), b.numCheckins "
        "FROM SuccessfulBusinesses sb JOIN Business b ON sb.business_id = b.business_id WHERE b.zipcode = '" + zipcode + "';"
        )       

        popular_rows = self.executeQuery(sql_popular)
        successful_rows = self.executeQuery(sql_successful)

        popular_headers = ["Name", "Address", "City"]
        successful_headers = ["Name", "Address", "City", "Rating", "Check-ins"]

        # Populate popular and successful tables
        self.populate_table(self.ui.popularTable, popular_rows, popular_headers)
        self.populate_table(self.ui.successfulTable, successful_rows, successful_headers)

    # Display zipcode data
    def displayZipcodeData(self, zipcode):
        sql = (
            f"SELECT "
            f"(SELECT COUNT(*) FROM business WHERE zipcode = '{zipcode}') AS total_businesses, "
            f"population, medianIncome "
            f"FROM zipcodeData WHERE zipcode = '{zipcode}' LIMIT 1;"
        )

        results = self.executeQuery(sql)
        if results:
            total_businesses, population, median_income = results[0]

            self.ui.zipcodeInfoTable.setRowCount(1)
            self.ui.zipcodeInfoTable.setColumnCount(3)
            self.ui.zipcodeInfoTable.setHorizontalHeaderLabels(["Total Businesses", "Population", "Median Income"])

            # Populate the zipcode data table with data
            self.ui.zipcodeInfoTable.setItem(0, 0, QTableWidgetItem(str(total_businesses)))
            self.ui.zipcodeInfoTable.setItem(0, 1, QTableWidgetItem("'" + str(population) + "'"))
            self.ui.zipcodeInfoTable.setItem(0, 2, QTableWidgetItem(f"${median_income:,}"))
        else:
            self.ui.zipcodeInfoTable.setRowCount(0)


if __name__ == "__main__":
    load_dotenv()
    run_sql_file("RELATIONS.sql")
    run_sql_file("insert_business.sql")
    run_sql_file("insert_categories.sql")
    run_sql_file("insert_attributes.sql")
    run_sql_file("insert_user.sql")
    run_sql_file("insert_friendship.sql")
    run_sql_file("insert_review.sql")
    run_sql_file("insert_checkins.sql")
    run_sql_file("zipData.sql")
    run_sql_file("UPDATE.sql")
    run_sql_file("POPULATION.sql")
    qapp = QApplication(sys.argv)
    window = app()
    window.show()
    sys.exit(qapp.exec_())