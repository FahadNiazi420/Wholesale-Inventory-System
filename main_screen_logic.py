import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QMessageBox,
    QMainWindow,
    QStackedWidget,
    QComboBox,
    QLineEdit,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QHeaderView,
    QTableWidgetItem,
    QWidget,
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QPushButton, QMessageBox, QMainWindow
import os
import sys
import os

from BL import productManager, shopkeeperManager


from ui_main import Ui_MainWindow  # Adjust based on your generated class name

class MasterScreen(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        
        import traceback

        try:
            self.setupUi(self)  # Call setupUi to initialize the UI

            from modules.ui_functions import UIFunctions
            print("here")
            self.ui = self
            self.ui.productsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.ui.shopkeeperTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.ui.orderDetailTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.ui.orderTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.ui.paymentsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.ui.returnsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.ui.salesmanTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.set_buttons_cursor()

            self.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))
            UIFunctions.uiDefinitions(self)

            self.btnProjects.setStyleSheet(UIFunctions.selectMenu(self.btnProjects.styleSheet()))

            self.stacked_widget = self.findChild(QStackedWidget, "stackedWidget")  # Match the object name in Qt Designer
            self.init_pages()

            self.menu_buttons = [self.btnProjects,  self.btnCriteria,self.btnTestList,self.btnReport,self.btnProjects,self.btnSensorList,self.btnPlanning,self.btnReportCampaign,self.btnDashboard]

            # Assign menu button clicks
            self.btnProjects.clicked.connect(self.show_config_system)
            self.btnCriteria.clicked.connect(self.show_menu_compiler)
            self.btnTestList.clicked.connect(self.show_game_update_menu)
            self.btnReport.clicked.connect(self.show_multi_tool_menu)
            self.btnSensorList.clicked.connect(self.show_pairip_pass_menu)
            self.btnPlanning.clicked.connect(self.show_offset_leech_menu)
            self.btnReportCampaign.clicked.connect(self.show_report_campaign_menu)
            self.btnDashboard.clicked.connect(self.show_dashboard_menu)

            # --------------------- SHOPKEEPER PAGE BUTTONS ---------------------
            self.ui.btnAddShopkeeper.clicked.connect(self.onAddShopkeeperClick)
            self.fillShopkeeperTable()

            # --------------------- PRODUCT PAGE BUTTON ---------------------
            self.ui.btnAddProduct.clicked.connect(self.onAddProductClick)
            self.fillProductsTable()

        except Exception as e:
            error_message = f"Error loading UI: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            print(error_message)  # Print to console for debugging
            self.show_message_box("Critical Error", error_message)

# ------------------------------------------------------ SHOPKEEPER FUNCTION ------------------------------------------------------
    def onAddShopkeeperClick(self):
        """Handles the add/edit shopkeeper button click event."""
        try:
            name = self.ui.txtShopkeeperName.text().strip()
            contact = self.ui.txtShopkeeperContact.text().strip()

            if not name or not contact:
                QMessageBox.warning(None, "Input Error", "Please fill all fields correctly before proceeding.")
                return

            if self.ui.btnAddShopkeeper.text() == "Edit Shopkeeper":
                success, message = shopkeeperManager.updateShopkeeper(self.editingShopkeeperID, name, contact)
            else:
                success, message = shopkeeperManager.addShopkeeper(name, contact)

            if success:
                QMessageBox.information(None, "Success", message)
                self.resetShopkeeperForm()
                self.fillShopkeeperTable()  # Refresh table after update
            else:
                QMessageBox.warning(None, "Error", message)

            # Reset button text
            self.ui.btnAddShopkeeper.setText("Add Shopkeeper")
            self.editingShopkeeperID = None  # Clear tracking variable

        except Exception as e:
            QMessageBox.critical(None, "Critical Error", f"An unexpected error occurred: {str(e)}")
    def fillShopkeeperTable(self):
        """Fetches shopkeeper data and fills the shopkeeperTable widget with Edit, Delete, and View buttons."""
        shopkeepers, error = shopkeeperManager.getShopkeepers()

        if error:
            QMessageBox.critical(None, "Error", error)
            return

        # Clear existing data
        self.ui.shopkeeperTable.setRowCount(0)

        # Adjust column count to include the ID column (hidden)
        self.ui.shopkeeperTable.setColumnCount(10)  # Ensure correct number of columns
        self.ui.shopkeeperTable.setHorizontalHeaderLabels([
            "ID", "Name", "Brand", "Contact Info", "Total Due", "Paid Amount", "Remaining", "Last Submission", "Edit", "Delete", "View"
        ])
        
        self.ui.shopkeeperTable.setColumnHidden(0, True)  # Hide the ID column

        # Insert data into the table
        for rowIndex, rowData in enumerate(shopkeepers):
            self.ui.shopkeeperTable.insertRow(rowIndex)
            for colIndex, value in enumerate(rowData):  # Do not skip ID column now
                item = QTableWidgetItem(str(value) if value is not None else "N/A")
                self.ui.shopkeeperTable.setItem(rowIndex, colIndex, item)

            # Add buttons for Edit, Delete, and View
            shopkeeperID = rowData[0]  # Ensure correct ID is fetched
            self.addShopkeeperTableButtons(rowIndex, shopkeeperID)



    def onEditShopkeeper(self, rowIndex):
        """Handles the edit shopkeeper button click by filling form fields with selected shopkeeper data."""
        try:
            shopkeeperID = self.ui.shopkeeperTable.item(rowIndex, 0).text()  # Get ID from hidden column
            name = self.ui.shopkeeperTable.item(rowIndex, 1).text()
            contact = self.ui.shopkeeperTable.item(rowIndex, 3).text()

            if not shopkeeperID:
                QMessageBox.warning(None, "Error", "Could not retrieve shopkeeper ID.")
                return

            self.editingShopkeeperID = shopkeeperID
            self.ui.txtShopkeeperName.setText(name)
            self.ui.txtShopkeeperContact.setText(contact)

            # Change button text and store ID for tracking updates
            self.ui.btnAddShopkeeper.setText("Edit Shopkeeper")

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Could not load shopkeeper details: {str(e)}")


    def onDeleteShopkeeper(self, shopkeeperID):
        """Handles the delete shopkeeper button click."""
        confirm = QMessageBox.question(None, "Delete Shopkeeper", 
                                    f"Are you sure you want to delete Shopkeeper ID: {shopkeeperID}?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            success, error = shopkeeperManager.deleteShopkeeper(shopkeeperID)
            if success:
                QMessageBox.information(None, "Success", "Shopkeeper deleted successfully!")
                self.fillShopkeeperTable()  # Refresh table after deletion
            else:
                QMessageBox.critical(None, "Error", error)


    def onViewShopkeeper(self, shopkeeperID=None):
        """Handles the view shopkeeper button click and displays shopkeeper details from the selected row."""
        try:
            table = self.ui.shopkeeperTable
            rowIndex = table.currentRow()  # Get the selected row index

            if rowIndex < 0:
                QMessageBox.warning(None, "Warning", "Please select a shopkeeper row to view details.")
                return

            # Extract data from the selected row
            shopkeeperID = table.item(rowIndex, 0).text()  # Get hidden ID column
            name = table.item(rowIndex, 1).text()
            contact = table.item(rowIndex, 3).text()

            # Format the details with spacing and font size
            details = f"""
            <html>
            <body style="font-size:12pt;">
                <table border="0" cellspacing="0" cellpadding="8" style="border-collapse: collapse; width: 200%;">
                    <tr>
                        <th align="left">Field</th>
                        <th align="left">Value</th>
                    </tr>
                    <tr>
                        <td><b>ID</b></td>
                        <td>{shopkeeperID}</td>
                    </tr>
                    <tr>
                        <td><b>Name</b></td>
                        <td>{name}</td>
                    </tr>
                    <tr>
                        <td><b>Contact</b></td>
                        <td>{contact}</td>
                    </tr>
                </table>
            </body>
            </html>
            """

            # Show details in a message box
            QMessageBox.information(None, "Shopkeeper Details", details)

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Unexpected error while viewing shopkeeper: {e}")
    def addShopkeeperTableButtons(self, rowIndex, shopkeeperID):
        """Adds Edit, Delete, and View buttons to the shopkeeperTable row."""
        editButton = QPushButton("Edit")
        deleteButton = QPushButton("Delete")
        viewButton = QPushButton("View")

        editButton.clicked.connect(lambda: self.onEditShopkeeper(rowIndex))
        deleteButton.clicked.connect(lambda: self.onDeleteShopkeeper(shopkeeperID))
        viewButton.clicked.connect(lambda: self.onViewShopkeeper())

        self.ui.shopkeeperTable.setCellWidget(rowIndex, 8, editButton)  # Edit column
        self.ui.shopkeeperTable.setCellWidget(rowIndex, 9, deleteButton)  # Delete column
        self.ui.shopkeeperTable.setCellWidget(rowIndex, 10, viewButton)  # View column

    def resetShopkeeperForm(self):
        """Resets the shopkeeper input fields to default values."""
        self.ui.txtShopkeeperName.clear()
        self.ui.txtShopkeeperContact.clear()

        self.ui.btnAddShopkeeper.setText("Add Shopkeeper")
        self.editingShopkeeperID = None
# ------------------------------------------------------ PRODUCT FUNCTIONS -------------------------------------------------------
    def onAddProductClick(self):
        """Handles the add/edit product button click event."""
        try:
            sku = self.ui.txtProductSKU.text().strip()
            name = self.ui.txtProductName.text().strip()
            brand = self.ui.cmbxPBrand.currentText().strip()
            size = self.ui.cmbxPSize.currentText().strip()
            quantity = self.ui.numPQuantity.value()
            price = self.ui.numPrice.value()

            if not sku or not name or not brand or quantity <= 0 or price <= 0:
                QMessageBox.warning(None, "Input Error", "Please fill all fields correctly before proceeding.")
                return

            if self.ui.btnAddProduct.text() == "Edit Product":
                success, message = productManager.updateProduct(self.editingSKU, sku, name, brand, size, quantity, price)
            else:
                success, message = productManager.addProduct(sku, name, brand, size, quantity, price)

            if success:
                QMessageBox.information(None, "Success", message)
                self.resetProductForm()
                self.fillProductsTable()  # Refresh table after update
            else:
                QMessageBox.warning(None, "Error", message)

            # Reset button text
            self.ui.btnAddProduct.setText("Add Product")
            self.editingSKU = None  # Clear tracking variable

        except Exception as e:
            QMessageBox.critical(None, "Critical Error", f"An unexpected error occurred: {str(e)}")
    
    def fillProductsTable(self):
        """Fetches product data and fills the productsTable widget with Edit, Delete, and View buttons."""
        products, error = productManager.getProducts()

        if error:
            QMessageBox.critical(None, "Error", error)
            return

        # Clear existing data
        self.ui.productsTable.setRowCount(0)

        # Set column headers
        self.ui.productsTable.setColumnCount(10)  # Added 3 columns for buttons
        self.ui.productsTable.setHorizontalHeaderLabels([
            "SKU", "Name", "Brand", "Size", "Quantity", "Total Price", "Price/Item", "Edit", "Delete", "View"
        ])
         # Set text color (black) for better visibility
        textColor = QColor(0, 0, 0)  # Black color
        # Insert data into the table
        for rowIndex, rowData in enumerate(products):
            self.ui.productsTable.insertRow(rowIndex)
            for colIndex, value in enumerate(rowData):
                item = QTableWidgetItem(str(value) if value is not None else "N/A")
                self.ui.productsTable.setItem(rowIndex, colIndex, item)

            # Add buttons for Edit, Delete, and View
            self.addTableButtons(rowIndex, products[rowIndex][0])  # Pass SKU as the unique identifier
    
    def onEditProduct(self, rowIndex):
        """Handles the edit product button click by filling form fields with selected product data."""
        try:
            rowIndex = int(rowIndex)  # Ensure rowIndex is an integer

            # Set values in input fields directly
            self.ui.txtProductSKU.setText(self.ui.productsTable.item(rowIndex, 0).text())
            self.ui.txtProductName.setText(self.ui.productsTable.item(rowIndex, 1).text())
            self.ui.cmbxPBrand.setCurrentText(self.ui.productsTable.item(rowIndex, 2).text())
            self.ui.cmbxPSize.setCurrentText(self.ui.productsTable.item(rowIndex, 3).text())
            self.ui.numPQuantity.setValue(int(float(self.ui.productsTable.item(rowIndex, 4).text())))
            self.ui.numPrice.setValue(int(float(self.ui.productsTable.item(rowIndex, 5).text())))# Convert to float

            # Change button text and store SKU for tracking updates
            self.ui.btnAddProduct.setText("Edit Product")
            self.editingSKU = self.ui.productsTable.item(rowIndex, 0).text()

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Could not load product details: {str(e)}")



    def onDeleteProduct(self, sku):
        """Handles the delete product button click."""
        confirm = QMessageBox.question(None, "Delete Product", f"Are you sure you want to delete SKU: {sku}?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            from BL import productManager
            success, error = productManager.deleteProduct(sku)
            if success:
                QMessageBox.information(None, "Success", "Product deleted successfully!")
                self.fillProductsTable()  # Refresh table after deletion
            else:
                QMessageBox.critical(None, "Error", error)

    def onViewProduct(self, sku=None):
        """Handles the view product button click and displays product details from the selected row."""
        try:
            table = self.ui.productsTable
            rowIndex = table.currentRow()  # Get the selected row index

            if rowIndex < 0:
                QMessageBox.warning(None, "Warning", "Please select a product row to view details.")
                return

            # Extract data from the selected row
            sku = table.item(rowIndex, 0).text() if table.item(rowIndex, 0) else "N/A"
            name = table.item(rowIndex, 1).text() if table.item(rowIndex, 1) else "N/A"
            brand = table.item(rowIndex, 2).text() if table.item(rowIndex, 2) else "N/A"
            size = table.item(rowIndex, 3).text() if table.item(rowIndex, 3) else "N/A"
            quantity = table.item(rowIndex, 4).text() if table.item(rowIndex, 4) else "N/A"
            totalPrice = table.item(rowIndex, 5).text() if table.item(rowIndex, 5) else "N/A"
            price = table.item(rowIndex, 6).text() if table.item(rowIndex, 6) else "N/A"

            # Format the details with spacing and font size
            details = f"""
            <html>
            <body style="font-size:12pt;">
                <table border="0" cellspacing="0" cellpadding="8" style="border-collapse: collapse; width: 200%;">
                    <tr>
                        <th align="left">Field</th>
                        <th align="left">Value</th>
                    </tr>
                    <tr>
                        <td><b>SKU</b></td>
                        <td>{sku}</td>
                    </tr>
                    <tr>
                        <td><b>Name</b></td>
                        <td>{name}</td>
                    </tr>
                    <tr>
                        <td><b>Brand</b></td>
                        <td>{brand}</td>
                    </tr>
                    <tr>
                        <td><b>Size</b></td>
                        <td>{size}</td>
                    </tr>
                    <tr>
                        <td><b>Quantity</b></td>
                        <td>{quantity}</td>
                    </tr>
                    <tr>
                        <td><b>Per Item Price</b></td>
                        <td>{price}</td>
                    </tr>
                    <tr>
                        <td><b>Total Price</b></td>
                        <td>{totalPrice}</td>
                    </tr>
                </table>
            </body>
            </html>
            """


            # Show details in a message box
            QMessageBox.information(None, "Product Details", details)

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Unexpected error while viewing product: {e}")

    def addTableButtons(self, rowIndex, sku):
        """Adds Edit, Delete, and View buttons to the productsTable row."""
        # Create buttons
        editButton = QPushButton("Edit")
        deleteButton = QPushButton("Delete")
        viewButton = QPushButton("View")

        # Connect buttons to their respective methods
        editButton.clicked.connect(lambda: self.onEditProduct(rowIndex))  # Pass rowIndex instead of SKU
        deleteButton.clicked.connect(lambda: self.onDeleteProduct(sku))
        viewButton.clicked.connect(lambda: self.onViewProduct(rowIndex))  # Pass rowIndex to fetch data from table

        # Set buttons inside respective cells
        self.ui.productsTable.setCellWidget(rowIndex, 7, editButton)  # Edit column
        self.ui.productsTable.setCellWidget(rowIndex, 8, deleteButton)  # Delete column
        self.ui.productsTable.setCellWidget(rowIndex, 9, viewButton)  # View column


    def resetProductForm(self):
        """Resets the product input fields to default values."""
        self.ui.txtProductSKU.clear()
        self.ui.txtProductName.clear()
        self.ui.cmbxPBrand.setCurrentIndex(0)  
        self.ui.cmbxPSize.setCurrentIndex(0)  

        self.ui.numPQuantity.setValue(0)  # Ensure integer values
        self.ui.numPrice.setValue(0)  # Ensure integer values

        self.ui.btnAddProduct.setText("Add Product")  # Reset button text
        self.currentEditingSKU = None  # Reset editing state



# --------------------- UI FUNCTIONS ---------------------
    
    def show_message_box(self, title, message):
        """Displays a QMessageBox for general errors."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()
    def init_pages(self):
        """Initialize backend logic for each page."""
        # Initialize ConfigSystem logic
        self.stackedWidget.setCurrentIndex(0)
    
    def show_report_campaign_menu(self):
        self.handleMenuClick(self.btnReportCampaign, 8)
    
    def show_dashboard_menu(self):
        self.handleMenuClick(self.btnDashboard, 7)

    def show_config_system(self):
        self.handleMenuClick(self.btnProjects, 0)

    def show_menu_compiler(self):
        self.handleMenuClick(self.btnCriteria,2)
    def show_game_update_menu(self):
        self.handleMenuClick(self.btnTestList,3)
    def show_pairip_pass_menu(self):
        """Show the Pair IP Pass page."""
        self.handleMenuClick(self.btnSensorList, 4)

    def show_offset_leech_menu(self):
        """Show the Offset Leech page."""
        # self.current_page = self.offset_leech
        self.handleMenuClick(self.btnPlanning, 5)
    def show_multi_tool_menu(self):
        """Show the Multi-Tool page."""
        self.handleMenuClick(self.btnReport, 6)    
    def handleMenuClick(self, button, page_index):
        """
        Handles menu button clicks to update styles and switch pages.
        """
        from modules.ui_functions import UIFunctions

        # Deselect all buttons
        for btn in self.menu_buttons:
            btn.setStyleSheet(UIFunctions.deselectMenu(btn.styleSheet()))

        # Select the clicked button
        button.setStyleSheet(UIFunctions.selectMenu(button.styleSheet()))

        # Switch to the selected page
        self.stackedWidget.setCurrentIndex(page_index)


    def set_buttons_cursor(self):
        """Set the pointer cursor for all buttons in the UI."""
        buttons = self.findChildren(QPushButton)  # Find all QPushButton objects
        for button in buttons:
            button.setCursor(Qt.PointingHandCursor)

    def resizeEvent(self, event):
        # Update Size Grips
        from modules.ui_functions import UIFunctions
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')
    



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main_window = MasterScreen()
    main_window.show()
    sys.exit(app.exec_())
