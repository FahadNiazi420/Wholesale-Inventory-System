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
    QTextEdit,
    QDialog,
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtWidgets import QApplication, QPushButton, QMessageBox, QMainWindow,QTableWidgetItem
import os
import sys
import os
from datetime import datetime
import textwrap

from BL import productManager, shopkeeperManager, orderManager 
from DL import orderDL, paymentDL




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

            # --------------------- PAYMENT / KHATA PAGE BUTTON ---------------------
            
            # Connect Payment Spinner Change Event for Dynamic Update
            self.ui.numPaymentPaid.valueChanged.connect(self.updateRemainingAmount)
            self.ui.btnAddPayment.clicked.connect(self.addPayment)

            # --------------------- ORDER PAGE BUTTONS ---------------------
            self.ui.btnCreateOrder.clicked.connect(self.createOrder)
            self.ui.btnAddItem.clicked.connect(self.addItemToOrder)
            self.ui.btnFinishOrder.clicked.connect(self.finishOrder)
            self.fillOrderTable()
            self.fillOrderComboboxes()
            self.current_order_id=0
            self.ui.cmbxOProduct.currentIndexChanged.connect(self.updateBill)
            self.ui.cmbxOProduct.currentIndexChanged.connect(self.setMaxQuantity)
            self.ui.numOQuantity.valueChanged.connect(self.updateBill)
            self.ui.numDiscount.valueChanged.connect(self.updateOrderSummaryonDiscount)

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

# ------------------------------------------------------ PAYMENT / KHATA ------------------------------------------------------
    def addPayment(self):
        """Handles the add or edit payment button click event."""
        try:
            shopkeeper_id = self.ui.cmbxPaySpk.currentData()
            order_id = self.ui.cmbxPayOrder.currentData()
            salesman_id = self.ui.cmbxPaySaleman.currentData()
            amount_paid = self.ui.numPaymentPaid.value()

            if not shopkeeper_id or not order_id or not salesman_id or amount_paid <= 0:
                QMessageBox.warning(None, "Input Error", "Please fill all fields correctly before proceeding.")
                return

            if self.ui.btnAddPayment.text() == "Update Payment":
                # Handle edit logic
                success, message = paymentDL.updatePayment(self.current_payment_id, shopkeeper_id, order_id, salesman_id, amount_paid)
                if success:
                    QMessageBox.information(None, "Success", "Payment updated successfully!")
                    self.ui.btnAddPayment.setText("Add Payment")  # Reset button text
                    self.current_payment_id = None  # Clear current payment ID
                else:
                    QMessageBox.warning(None, "Error", message)
            else:
                # Handle add logic
                success, message = paymentDL.addPayment(shopkeeper_id, order_id, salesman_id, amount_paid)
                if success:
                    QMessageBox.information(None, "Success", message)
                else:
                    QMessageBox.warning(None, "Error", message)
            self.loadOrdersForSelectedShopkeeper()
            self.fillPaymentsTable()  # Refresh payments table

        except Exception as e:
            QMessageBox.critical(None, "Critical Error", f"An unexpected error occurred: {str(e)}")

 
    def fillPaymentsTable(self):
        """Fetches payment data and fills the paymentsTable widget with Edit, Delete, and View buttons."""
        payments, error = paymentDL.getPayments()
        if error:
            QMessageBox.critical(self, "Error", error)
            return

        # Clear existing data
        self.ui.paymentsTable.setRowCount(0)

        # Define column headers (excluding hidden IDs)
        self.ui.paymentsTable.setColumnCount(17)  # Adjusted for buttons
        self.ui.paymentsTable.setHorizontalHeaderLabels([
            "Payment ID", "Shopkeeper ID", "Order ID",  # Hidden columns
            "Order Info", "Shopkeeper", "Brand", "Khata", "Order Total", "Discount", 
            "Discounted Total", "Amount Paid", "Cumulative Paid", "Remaining Due", "Payment Date",
            "Edit", "Delete", "View"
        ])

        # Populate table with fetched data
        for rowIndex, rowData in enumerate(payments):
            payment_id, shopkeeper_id, shopkeeper_name, brand, khata_value, order_id, order_info, total_amount, discount_percentage, discounted_total, amount_paid, cumulative_paid, remaining_due, payment_date = rowData

            self.ui.paymentsTable.insertRow(rowIndex)

            # Fill data columns (including hidden IDs)
            column_values = [
                str(payment_id), str(shopkeeper_id), str(order_id),  # Hidden columns
                order_info, shopkeeper_name, brand,f"{khata_value:.2f}", f"{total_amount:.2f}", f"{discount_percentage:.2f}%", 
                f"{discounted_total:.2f}", f"{amount_paid:.2f}", f"{cumulative_paid:.2f}", f"{remaining_due:.2f}", 
                str(payment_date)
            ]

            for colIndex, value in enumerate(column_values):
                item = QTableWidgetItem(value)
                self.ui.paymentsTable.setItem(rowIndex, colIndex, item)

            # Add action buttons
            self.addPaymentTableButtons(rowIndex, payment_id, order_id)

        # Hide backend-use columns (Payment_ID, Shopkeeper_ID, Order_ID)
        self.ui.paymentsTable.setColumnHidden(0, True)  # Hide Payment_ID
        self.ui.paymentsTable.setColumnHidden(1, True)  # Hide Shopkeeper_ID
        self.ui.paymentsTable.setColumnHidden(2, True)  # Hide Order_ID

        # Adjust column resizing
        self.ui.paymentsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.paymentsTable.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.ui.paymentsTable.horizontalHeader().setSectionResizeMode(13, QHeaderView.ResizeToContents)
        self.ui.paymentsTable.horizontalHeader().setSectionResizeMode(14, QHeaderView.ResizeToContents)
        self.ui.paymentsTable.horizontalHeader().setSectionResizeMode(15, QHeaderView.ResizeToContents)
        self.ui.paymentsTable.horizontalHeader().setSectionResizeMode(16, QHeaderView.ResizeToContents)
        self.ui.paymentsTable.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)
        self.ui.paymentsTable.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        # self.ui.paymentsTable.horizontalHeader().setSectionResizeMode(13, QHeaderView.ResizeToContents)

    def addPaymentTableButtons(self, rowIndex, paymentID, orderID):
        """Adds Edit, Delete, and View buttons to the paymentsTable for a specific payment."""
        editButton = QPushButton("Edit")
        deleteButton = QPushButton("Delete")
        viewButton = QPushButton("View")

        editButton.clicked.connect(lambda: self.editPayment(paymentID))
        deleteButton.clicked.connect(lambda: self.deletePayment(paymentID))
        viewButton.clicked.connect(lambda: self.viewPayment(paymentID))

        # **Ensure buttons appear by placing them in the correct columns**
        self.ui.paymentsTable.setCellWidget(rowIndex, 14, editButton)  
        self.ui.paymentsTable.setCellWidget(rowIndex, 15, deleteButton)
        self.ui.paymentsTable.setCellWidget(rowIndex, 16, viewButton)
    
    def deletePayment(self, payment_id):
        """Handles the delete payment button click event."""
        confirm = QMessageBox.question(self, "Delete Payment", 
                                    f"Are you sure you want to delete Payment ID: {payment_id}?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            success, error = paymentDL.deletePayment(payment_id)
            if success:
                QMessageBox.information(self, "Success", "Payment deleted successfully!")
                self.fillPaymentsTable()
            else:
                QMessageBox.critical(self, "Error", error)

    def editPayment(self, payment_id):
        """Fills the payment form with existing data for editing."""
        try:
            payment, error = paymentDL.getPaymentById(payment_id)
            self.current_payment_id = payment_id
            if error:
                QMessageBox.critical(self, "Error", error)
                return
            if not payment:
                QMessageBox.critical(self, "Error", "Payment not found!")
                return

            shopkeeper_name, order_info, amount_paid, payment_date = payment

            # Set values in the UI fields
            self.ui.cmbxPaySpk.setCurrentText(shopkeeper_name)
            # Find the matching order in the combo box based on OrderInfo
            for i in range(self.ui.cmbxPayOrder.count()):
                item_text = self.ui.cmbxPayOrder.itemText(i)
                if item_text.split(" (")[0] == order_info:  # Extract OrderInfo part
                    self.ui.cmbxPayOrder.setCurrentIndex(i)
                    break
            self.ui.numPaymentPaid.setValue(int(amount_paid))
            self.ui.txtPayLastPayment.setText(payment_date)
            

            # Update remaining amount
            self.updateRemainingAmount()

            # Update button text to indicate editing
            self.ui.btnAddPayment.setText("Update Payment")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load payment details: {str(e)}")

    def viewPayment(self, payment_id):
        """Displays detailed payment information from the table instead of querying the database."""
        try:
            # Find the row that corresponds to the given payment_id
            row = -1
            for i in range(self.ui.paymentsTable.rowCount()):
                if self.ui.paymentsTable.item(i, 0) and self.ui.paymentsTable.item(i, 0).text() == str(payment_id):
                    row = i
                    break
            
            if row == -1:
                QMessageBox.warning(self, "Error", "Payment ID not found in the table.")
                return

            # Fetch values from the table
            payment_id = self.ui.paymentsTable.item(row, 0).text()  # Payment ID
            shopkeeper_name = self.ui.paymentsTable.item(row, 4).text()
            brand = self.ui.paymentsTable.item(row, 5).text()
            order_info = self.ui.paymentsTable.item(row, 3).text()
            khata = float(self.ui.paymentsTable.item(row, 6).text())
            total_amount = float(self.ui.paymentsTable.item(row, 7).text())
            discount_percentage = float(self.ui.paymentsTable.item(row, 8).text().replace("%", ""))  # Remove % if present
            discounted_total = float(self.ui.paymentsTable.item(row, 9).text())
            amount_paid = float(self.ui.paymentsTable.item(row, 10).text())
            cumulative_paid = float(self.ui.paymentsTable.item(row, 11).text())
            remaining_due = float(self.ui.paymentsTable.item(row, 12).text())
            payment_date = self.ui.paymentsTable.item(row, 13).text()

            # Format data into an HTML table
            details = textwrap.dedent(f"""
            <html>
            <body style="font-size:12pt; margin: auto; align-item:center;">
                <h2 style="text-align:center;">Payment Details</h2>
                <table border="0" cellspacing="0" cellpadding="8" style="border-collapse: collapse; width: 100%;">
                    <tr><th align="left">Field</th><th align="left">Value</th></tr>
                    <tr><td><b>Payment ID</b></td><td>{payment_id}</td></tr>
                    <tr><td><b>Shopkeeper</b></td><td>{shopkeeper_name}</td></tr>
                    <tr><td><b>Brand</b></td><td>{brand}</td></tr>
                    <tr><td><b>Order Info</b></td><td>{order_info}</td></tr>
                    <tr><td><b>Khata</b></td><td>{khata:.2f}</td></tr>
                    <tr><td><b>Order Total</b></td><td>{total_amount:.2f}</td></tr>
                    <tr><td><b>Discount</b></td><td>{discount_percentage:.2f}%</td></tr>
                    <tr><td><b>Discounted Total</b></td><td>{discounted_total:.2f}</td></tr>
                    <tr><td><b>Amount Paid</b></td><td>{amount_paid:.2f}</td></tr>
                    <tr><td><b>Cumulative Paid</b></td><td>{cumulative_paid:.2f}</td></tr>
                    <tr><td><b>Remaining Due</b></td><td>{remaining_due:.2f}</td></tr>
                    <tr><td><b>Payment Date</b></td><td>{payment_date}</td></tr>
                </table>
            </body>
            </html>
            """)

            # Use a dialog instead of QMessageBox to display HTML properly
            dialog = QDialog(self)
            dialog.setWindowTitle("Payment Details")
            layout = QVBoxLayout()
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setHtml(details)  # Correctly render HTML
            layout.addWidget(text_edit)
            dialog.setLayout(layout)
            dialog.resize(600, 500)
            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Critical Error", f"An unexpected error occurred: {str(e)}")

    def fillPaymentComboboxes(self):
        """Fills shopkeeper combobox and sets up dynamic updates for order and salesman."""
        self.ui.cmbxPaySpk.clear()
        self.ui.cmbxPayOrder.clear()
        self.ui.cmbxPaySaleman.clear()

        # Load Shopkeepers
        shopkeepers, _ = paymentDL.getDistinctShopkeepersFromOrders()
        if shopkeepers:
            for sk in shopkeepers:
                self.ui.cmbxPaySpk.addItem(sk[1], sk[0])  # Display Name, store ID

        # Connect signal to load orders dynamically
        self.ui.cmbxPaySpk.currentIndexChanged.connect(self.loadOrdersForSelectedShopkeeper)

        # Auto-select first shopkeeper if available
        if self.ui.cmbxPaySpk.count() > 0:
            self.ui.cmbxPaySpk.setCurrentIndex(0)
            self.loadOrdersForSelectedShopkeeper()

    def loadOrdersForSelectedShopkeeper(self):
        """Loads orders for the selected shopkeeper and updates related fields."""
        self.ui.cmbxPayOrder.clear()
        self.ui.cmbxPayBrand.clear()

        shopkeeper_id = self.ui.cmbxPaySpk.currentData()
        if not shopkeeper_id:
            return

        # Load Orders for the Selected Shopkeeper
        orders, _ = paymentDL.getOrdersByShopkeeper(shopkeeper_id)
        if orders:
            for order in orders:
                display_text = f"{order[1]} (ID: {order[0]})"  # Order_Info (ID: Order_ID)
                self.ui.cmbxPayOrder.addItem(display_text, order[0])  # Display Order_Info, store Order_ID

            # Auto-select the first order
            self.ui.cmbxPayOrder.setCurrentIndex(0)

        # Load Shopkeeper Brand
        brand, _ = paymentDL.getShopkeeperBrand(shopkeeper_id)
        if brand:
            self.ui.cmbxPayBrand.addItem(brand)

        # Load Last Payment Submission Date
        last_submission, _ = paymentDL.getLastSubmissionDate(shopkeeper_id)
        self.ui.txtPayLastPayment.setText(last_submission)

        # Load Total Paid and Total Due for Shopkeeper
        total_paid, total_due, _ = paymentDL.getShopkeeperTotalPaidAndDue(shopkeeper_id)
        # print(shopkeeper_id,total_paid, total_due)
        self.ui.lblSpkPaid.setText(str(int(total_paid)))
        self.ui.lblTotalDue.setText(str(int(total_due)))

        # Ensure order updates are handled dynamically
        try:
            self.ui.cmbxPayOrder.currentIndexChanged.disconnect(self.loadSalesmanForSelectedOrder)
        except TypeError:
            pass  # Ignore if already disconnected

        self.ui.cmbxPayOrder.currentIndexChanged.connect(self.loadSalesmanForSelectedOrder)

        # Call function to fill salesman based on first selected order
        self.loadSalesmanForSelectedOrder()

    def loadSalesmanForSelectedOrder(self):
        """Loads salesman details for the selected order and updates order total."""
        self.ui.cmbxPaySaleman.clear()

        order_id = self.ui.cmbxPayOrder.currentData()
        if not order_id:
            return

        # Load Salesman
        salesman, _ = paymentDL.getSalesmanByOrder(order_id)
        if salesman:
            self.ui.cmbxPaySaleman.addItem(salesman[1], salesman[0])  # Display Name, store ID
            self.ui.cmbxPaySaleman.setCurrentIndex(0)  # Auto-select salesman

        # Load Order Total
        total_amount, _ = paymentDL.getOrderTotalAmount(order_id)
        self.ui.lblOrderPaidbyDue.setText(str(int(total_amount)))
        self.ui.numPaymentPaid.setMaximum(int(total_amount))  # Set max limit on spin box

        # Call update function to handle remaining amount
        self.updateRemainingAmount()

    def updateRemainingAmount(self):
        """Dynamically update remaining amount with accurate calculations."""
        try:
            total_due = int(self.ui.lblTotalDue.text())  # Total amount due
            total_paid = int(self.ui.lblSpkPaid.text())  # Already paid amount
            amount_paying = int(self.ui.numPaymentPaid.value())  # New payment
            self.ui.lblAmountPaid.setText(str(amount_paying))

            orderTotal = int(self.ui.lblOrderPaidbyDue.text())
            self.ui.lblOrderRemain.setText(str(orderTotal-amount_paying))
            # Remaining should be due - (already paid + new payment)
            remaining_amount = total_due - amount_paying

            
            self.ui.lblRemaining.setText(str(remaining_amount))
        except ValueError:
            self.ui.lblRemaining.setText("0")  # Handle errors


# ------------------------------------------------------ ORDER FUNCTIONS ------------------------------------------------------
    def createOrder(self):
        """Handles order creation when the button is clicked."""
        shopkeeper_id = self.ui.cmbxOShopkeeper.currentData()
        salesman_id = self.ui.cmbxOSaleman.currentData()
        order_info = self.ui.txtOrderInfo.text()  # Ensure this field is optional if not needed
        discount = self.ui.numDiscount.value()

        if self.ui.btnCreateOrder.text() == "Edit Order":
            success, message = orderDL.updateOrder(self.current_order_id, shopkeeper_id, salesman_id, order_info, discount)
        else:
            success, message, order_id = orderManager.addOrder(shopkeeper_id, salesman_id, order_info, discount)
            self.current_order_id = order_id  # Store order ID for adding items

        if success:
            # Disable order-related fields
            self.ui.cmbxOShopkeeper.setDisabled(True)
            self.ui.cmbxOSaleman.setDisabled(True)
            self.ui.numDiscount.setDisabled(True)
            self.ui.txtOrderInfo.setDisabled(True)
            self.ui.btnCreateOrder.setDisabled(True)

            # Enable order item addition
            self.ui.cmbxOProduct.setEnabled(True)
            self.ui.numOQuantity.setEnabled(True)
            self.ui.btnAddItem.setEnabled(True)
            self.ui.btnFinishOrder.setEnabled(True)

            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)

    def addItemToOrder(self):
        """Adds an item to the current order and updates discount & total."""
        if not hasattr(self, 'current_order_id'):
            QMessageBox.warning(self, "Warning", "Please create an order first.")
            return
        
        product_sku = self.ui.cmbxOProduct.currentData()
        quantity = self.ui.numOQuantity.value()
        calculated_price = self.ui.txtOBill.text()  # Retrieve correct value

        # Add order item
        success, message = orderManager.addOrderItem(self.current_order_id, product_sku, quantity, calculated_price)
        if success:
            self.updateOrderSummary()
            self.fillOrderDetailTable()
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)
    
    def fillOrderDetailTable(self):
        """Fetches order items and fills the order details table."""
        if not hasattr(self, 'current_order_id'):
            return  # No order created yet

        self.ui.orderDetailTable.setRowCount(0)  # Clear table
        order_id = self.current_order_id
        items = orderDL.getOrderItems(order_id)  # Fetch order items
        if not items:
            return  # No items to display

        for row_index, (order_item_id, product_name, quantity, bill) in enumerate(items):
            self.ui.orderDetailTable.insertRow(row_index)

            # Product Name
            self.ui.orderDetailTable.setItem(row_index, 0, QTableWidgetItem(str(product_name)))

            # Quantity
            self.ui.orderDetailTable.setItem(row_index, 1, QTableWidgetItem(str(quantity)))

            # Bill (Formatted)
            self.ui.orderDetailTable.setItem(row_index, 2, QTableWidgetItem(f"{bill:.2f}"))

            # Edit Button
            btn_edit = QPushButton("Edit")
            btn_edit.clicked.connect(lambda _, item_id=order_item_id: self.editOrderItem(item_id))
            self.ui.orderDetailTable.setCellWidget(row_index, 3, btn_edit)

            # Delete Button
            btn_delete = QPushButton("Delete")
            btn_delete.clicked.connect(lambda _, item_id=order_item_id: self.deleteOrderItem(item_id))
            self.ui.orderDetailTable.setCellWidget(row_index, 4, btn_delete)
        
    def deleteOrderItem(self, order_item_id):
        """Deletes an item from the order and updates the table."""
        confirm = QMessageBox.question(self, "Delete Item", "Are you sure you want to delete this item?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.No:
            return

        success, message = orderDL.removeOrderItem(order_item_id)
        if success:
            QMessageBox.information(self, "Success", "Item deleted successfully!")
            self.fillOrderDetailTable()  # Refresh the table
            self.updateOrderSummary()
        else:
            QMessageBox.critical(self, "Error", message)

    def editOrderItem(self, order_item_id):
        """Fills the input fields with order item details for editing."""
        item = orderDL.getOrderItemById(order_item_id)
        if not item:
            QMessageBox.critical(self, "Error", "Item not found!")
            return

        product_sku, quantity, bill = item

        # Set values in the UI fields
        self.ui.cmbxOProduct.setCurrentIndex(self.ui.cmbxOProduct.findData(product_sku))
        self.ui.numOQuantity.setValue(int(quantity))
        # dividing bill by quantity because getOrderById is sending quan*price calcualted as bill
        self.ui.txtOBill.setText(f"{bill/quantity:.2f}")
        # print("editorder:",product_sku,quantity,bill)

        # Store current order_item_id for update action
        self.current_order_item_id = order_item_id

    def setMaxQuantity(self):
        """Sets the maximum quantity for a product based on stock."""
        sku = self.ui.cmbxOProduct.currentData()
        _, upperQuantity = orderDL.getProductPrice(sku)
        # print("upperQuantity:",upperQuantity)
        # Check if upperQuantity is a valid number
        try:
            upperQuantity = int(upperQuantity)
        except (ValueError, TypeError):
            upperQuantity = 0  # Default to 0 if invalid
        
        # Set maximum quantity based on stock
        self.ui.numOQuantity.setMaximum(upperQuantity)
    
    def updateBill(self):
        """Calculates bill amount when quantity changes."""
        sku = self.ui.cmbxOProduct.currentData()
        quantity = self.ui.numOQuantity.value()

        price, upperQuantity = orderDL.getProductPrice(sku)

        # Handle cases where price or quantity is None
        if price is None or upperQuantity is None:
            self.ui.txtOBill.setText("0")
            return

        total_price = price * quantity
        self.ui.txtOBill.setText(str(total_price))

    def updateOrderSummaryonDiscount(self):
        """Updates the discount and grand total labels based on the discount percentage."""
        total_amount, _, grand_total = orderDL.calculateOrderTotals(self.current_order_id)
        discount_percentage = self.ui.numDiscount.value()
        discount_amount = (discount_percentage / 100) * total_amount
        grand_total = total_amount - discount_amount

        self.ui.lblTotal.setText(f"{total_amount:.2f}")
        self.ui.lblDiscount.setText(f"{discount_amount:.2f}")
        self.ui.lblGrandTotal.setText(f"{grand_total:.2f}")

    def updateOrderSummary(self):
        """Updates the discount and grand total labels based on added items."""
        total_amount, discount, grand_total = orderDL.calculateOrderTotals(self.current_order_id)
        self.ui.lblTotal.setText(f"{total_amount:.2f}")
        self.ui.lblDiscount.setText(f"{discount:.2f}")
        self.ui.lblGrandTotal.setText(f"{grand_total:.2f}")

    def finishOrder(self):
        """Finalizes the order, saves changes, and refreshes the order table."""
        success, message = orderManager.finalizeOrder(self.current_order_id)
        if success:
            self.fillOrderTable()
            self.fillOrderDetailTable()
            self.resetOrderForm()
            QMessageBox.information(self, "Success", message)

            # Enable order item addition
            self.ui.cmbxOProduct.setEnabled(False)
            self.ui.numOQuantity.setEnabled(False)
            self.ui.btnAddItem.setEnabled(False)
            self.ui.btnFinishOrder.setEnabled(False)
        else:
            QMessageBox.critical(self, "Error", message)

    def fillOrderTable(self):
        """Fetches and displays all orders in the order table."""
        orders, error = orderManager.getOrders()
        if error:
            QMessageBox.critical(self, "Error", error)
            return
        
        self.ui.orderTable.setRowCount(0)
        self.ui.orderTable.setColumnCount(10)  # Adjusted column count to include all columns
        self.ui.orderTable.setHorizontalHeaderLabels([
            "Order Info", "Shopkeeper", "Salesman", "Date", "Total Amount", "Discount", "Grand Total", "Edit", "Delete", "View"
        ])
        
        for rowIndex, rowData in enumerate(orders):
            self.ui.orderTable.insertRow(rowIndex)
            for colIndex, value in enumerate(rowData[1:]):  # Skip the first column (Order ID)
                item = QTableWidgetItem(str(value) if value is not None else "N/A")
                self.ui.orderTable.setItem(rowIndex, colIndex, item)
            
            self.addOrderTableButtons(rowIndex, rowData[0])  # Pass Order ID to button handlers

        self.ui.orderTable.setColumnHidden(0, False)  # Ensure the Order Info column is visible
        self.ui.orderTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Ensure columns are visible

    def addOrderTableButtons(self, rowIndex, orderID):
        """Adds Edit, Delete, and View buttons to the orderTable for a specific order."""
        editButton = QPushButton("Edit")
        deleteButton = QPushButton("Delete")
        viewButton = QPushButton("View")

        editButton.clicked.connect(lambda: self.editOrder(orderID))
        deleteButton.clicked.connect(lambda: self.deleteOrder(orderID))
        viewButton.clicked.connect(lambda: self.viewOrder(orderID))

        self.ui.orderTable.setCellWidget(rowIndex, 7, editButton)  # Adjust column index based on your table
        self.ui.orderTable.setCellWidget(rowIndex, 8, deleteButton)
        self.ui.orderTable.setCellWidget(rowIndex, 9, viewButton)
 
    def viewOrder(self, orderID):
        """Handles the view order button click and displays order details."""
        try:
            order, error = orderDL.getOrderById(orderID)
            if error:
                QMessageBox.critical(self, "Error", error)
                return
            if not order:
                QMessageBox.critical(self, "Error", "Order not found!")
                return

            order_id, order_info, shopkeeper_name, salesman_name, order_date, total_amount, discount_amount, grand_total = order

            order_date = order_date if order_date is not None else "N/A"
            total_amount = total_amount if total_amount is not None else 0.0
            discount_amount = discount_amount if discount_amount is not None else 0.0
            grand_total = grand_total if grand_total is not None else 0.0

            details = f"""
            <html>
            <body style="font-size:12pt;">
                <table border="0" cellspacing="0" cellpadding="8" style="border-collapse: collapse; width: 200%;">
                    <tr>
                        <th align="left">Field</th>
                        <th align="left">Value</th>
                    </tr>
                    <tr>
                        <td><b>Order ID</b></td>
                        <td>{order_id}</td>
                    </tr>
                    <tr>
                        <td><b>Order Info</b></td>
                        <td>{order_info}</td>
                    </tr>
                    <tr>
                        <td><b>Shopkeeper</b></td>
                        <td>{shopkeeper_name}</td>
                    </tr>
                    <tr>
                        <td><b>Salesman</b></td>
                        <td>{salesman_name}</td>
                    </tr>
                    <tr>
                        <td><b>Order Date</b></td>
                        <td>{order_date}</td>
                    </tr>
                    <tr>
                        <td><b>Total Amount</b></td>
                        <td>{total_amount:.2f}</td>
                    </tr>
                    <tr>
                        <td><b>Discount Amount</b></td>
                        <td>{discount_amount:.2f}</td>
                    </tr>
                    <tr>
                        <td><b>Grand Total</b></td>
                        <td>{grand_total:.2f}</td>
                    </tr>
                </table>
            </body>
            </html>
            """

            QMessageBox.information(self, "Order Details", details)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error while viewing order: {e}")

    def editOrder(self, orderID):
        """Handles the edit order button click by filling order details for the selected order."""
        try:
            self.current_order_id = orderID
            order, error = orderDL.getOrderById(orderID)
            if error:
                QMessageBox.critical(self, "Error", error)
                return
            if not order:
                QMessageBox.critical(self, "Error", "Order not found!")
                return

            order_id, order_info, shopkeeper_name, salesman_name, order_date, total_amount, discount_amount, grand_total = order

            # Calculate discount percentage
            discount_percentage = (discount_amount / total_amount) * 100 if total_amount > 0 else 0

            # Set values in the UI fields
            self.ui.cmbxOShopkeeper.setCurrentIndex(
            next((i for i in range(self.ui.cmbxOShopkeeper.count()) if self.ui.cmbxOShopkeeper.itemText(i).startswith(shopkeeper_name)), -1))
            self.ui.cmbxOSaleman.setCurrentIndex(self.ui.cmbxOSaleman.findText(salesman_name))
            self.ui.txtOrderInfo.setText(order_info)
            self.ui.numDiscount.setValue(int(discount_percentage))  # Set discount as percentage

            # Enable order item addition
            self.ui.cmbxOProduct.setEnabled(True)
            self.ui.numOQuantity.setEnabled(True)
            self.ui.btnAddItem.setEnabled(True)
            self.ui.btnFinishOrder.setEnabled(True)

            # Change button text to "Edit Order"
            self.ui.btnCreateOrder.setText("Edit Order")
            self.ui.btnCreateOrder.setEnabled(True)

            self.fillOrderDetailTable()
            self.updateOrderSummary()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load order details: {str(e)}")

    def deleteOrder(self, orderID):
        """Handles the delete order button click."""
        confirm = QMessageBox.question(self, "Delete Order", 
                                    f"Are you sure you want to delete Order ID: {orderID}?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            success, error = orderManager.deleteOrder(orderID)
            if success:
                self.fillOrderTable()  # Refresh table after deletion
                QMessageBox.information(self, "Success", "Order deleted successfully!")
            else:
                QMessageBox.critical(self, "Error", error)

    def fillOrderComboboxes(self):
        """Fills shopkeeper, salesman, and product combo boxes with IDs and names."""
        self.ui.cmbxOShopkeeper.clear()
        self.ui.cmbxOSaleman.clear()
        self.ui.cmbxOProduct.clear()

        # Fetch shopkeepers
        shopkeepers, _ = orderDL.getShopkeepers()
        if shopkeepers:
            for sk in shopkeepers:
                display_text = f"{sk[1]} ({sk[2]})"  # Name (Brand)
                self.ui.cmbxOShopkeeper.addItem(display_text, sk[0])  # Store ID as data

        # Fetch salesmen
        salesmen, _ = orderDL.getSalesmen()
        if salesmen:
            for sm in salesmen:
                self.ui.cmbxOSaleman.addItem(sm[1], sm[0])  # Store ID as data

        # Load products based on the first shopkeeper's brand (if exists)
        if shopkeepers:
            self.updateProductsByShopkeeper(shopkeepers[0][0])  # Pass first shopkeeper ID

        # Connect shopkeeper selection change to reload products
        self.ui.cmbxOShopkeeper.currentIndexChanged.connect(self.onShopkeeperChanged)

    def onShopkeeperChanged(self):
        """Updates product list when shopkeeper selection changes."""
        index = self.ui.cmbxOShopkeeper.currentIndex()
        if index != -1:
            shopkeeper_id = self.ui.cmbxOShopkeeper.itemData(index)
            self.updateProductsByShopkeeper(shopkeeper_id)

    def updateProductsByShopkeeper(self, shopkeeper_id):
        """Fetches and updates product combo box based on the selected shopkeeper's brand."""
        shopkeepers, _ = orderDL.getShopkeepers()
        selected_brand = None
        for sk in shopkeepers:
            if sk[0] == shopkeeper_id:
                selected_brand = sk[2]  # Get brand
                break

        if selected_brand:
            self.ui.cmbxOProduct.clear()
            products, _ = orderDL.getProductsByBrand(selected_brand)
            if products:
                for p in products:
                    display_text = f"{p[0]} - {p[1]} - {p[2]}"  # SKU - Name - Size
                    self.ui.cmbxOProduct.addItem(display_text, p[0])  # Store SKU as data

    def resetOrderForm(self):
        """Resets order fields for new entry and clears the order detail table."""
        self.ui.cmbxOShopkeeper.setEnabled(True)
        self.ui.cmbxOSaleman.setEnabled(True)
        self.ui.numDiscount.setEnabled(True)
        self.ui.txtOrderInfo.setEnabled(True)

        # Reset input fields
        self.ui.txtOrderInfo.clear()
        self.ui.numDiscount.setValue(0)
        self.ui.lblDiscount.setText("0.00")
        self.ui.lblGrandTotal.setText("0.00")
        self.ui.lblTotal.setText("0.00")

        # Clear the order details table
        self.ui.orderDetailTable.setRowCount(0)  

        # Reset order state
        self.current_order_id = None
        self.ui.btnCreateOrder.setText("Create Order")


# ------------------------------------------------------ SHOPKEEPER FUNCTION ------------------------------------------------------
    def onAddShopkeeperClick(self):
        """Handles the add/edit shopkeeper button click event."""
        try:
            name = self.ui.txtShopkeeperName.text().strip()
            contact = self.ui.txtShopkeeperContact.text().strip()
            brand = self.ui.cmbxSpkBrand.currentText().strip()  # Get selected brand

            if not name or not contact or not brand:
                QMessageBox.warning(None, "Input Error", "Please fill all fields correctly before proceeding.")
                return

            if self.ui.btnAddShopkeeper.text() == "Edit Shopkeeper":
                success, message = shopkeeperManager.updateShopkeeper(self.editingShopkeeperID, name, contact, brand)
            else:
                success, message = shopkeeperManager.addShopkeeper(name, contact, brand)

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
        self.ui.shopkeeperTable.setColumnCount(11)  # Ensure correct number of columns
        self.ui.shopkeeperTable.setHorizontalHeaderLabels([
            "ID", "Name", "Brand", "Contact Info", "Total Due", "Paid Amount", "Remaining", "Last Submission", "Edit", "Delete", "View"
        ])
        
        self.ui.shopkeeperTable.setColumnHidden(0, True)  # Hide the ID column

        # Insert data into the table
        for rowData in shopkeepers:
            isDeleted = rowData[-1]  # Assuming IsDeleted is the last column
            if isDeleted in (1, True):  # Skip if marked as deleted
                continue

            rowIndex = self.ui.shopkeeperTable.rowCount()
            self.ui.shopkeeperTable.insertRow(rowIndex)
            
            for colIndex, value in enumerate(rowData[:-1]):  # Exclude IsDeleted column
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
            brand = self.ui.shopkeeperTable.item(rowIndex, 2).text()
            contact = self.ui.shopkeeperTable.item(rowIndex, 3).text()

            if not shopkeeperID:
                QMessageBox.warning(None, "Error", "Could not retrieve shopkeeper ID.")
                return

            self.editingShopkeeperID = shopkeeperID
            self.ui.txtShopkeeperName.setText(name)
            self.ui.cmbxSpkBrand.setCurrentText(brand)
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
        self.fillPaymentComboboxes()
        self.fillPaymentsTable()
    def show_pairip_pass_menu(self):
        """Show the Pair IP Pass page."""
        self.handleMenuClick(self.btnSensorList, 4)
        self.fillOrderTable()
        self.fillOrderComboboxes()

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
