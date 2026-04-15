# Shopify Amazon Shipping Guide

**Source:** https://www.pluginhive.com/knowledge-base/amazon-shipping-guide-for-shopify/
**App:** Shopify Multi Carrier Shipping Label App (MCSL)
**Note:** Some screenshots may show older app UI — all text content is current.

---

# Shopify Amazon Shipping Guide

> This guide will help you integrate **your** Amazon Shipping account with your Shopify store using the **[**PH MultiCarrier Shipping Label app**](https://www.pluginhive.com/shopify-multi-carrier-shipping-label-app/) **by PluginHive. Once you have successfully integrated **Amazon Shipping** with Shopify, you will be able to automatically display Amazon Shipping rates at checkout, print shipping labels, and easily track your shipments

  1. **Add, Install, and Activate PH MultiCarrier Shipping Label App**
  2. **Add your Amazon Shipping Account**
  3. **Verify the Shipper or Warehouse Address**
  4. **Configure Weight& Dimensions for Your Products and Choose the Right Packaging Method**
  5. **Opt for the Preferred Amazon Shipping Services to be displayed at the Shopify Checkout**
  6. **Display Amazon Shipping rates on the Shopify checkout**
  7. **Verify the Shipping Cost Displayed on the Shopify Checkout Page**
  8. **Print the Amazon Shipping Labels for your Shopify Orders**
  9. **Mark Orders as Fulfilled and Automatically Send Amazon Shipping Tracking Details**
  10. **Track your Amazon Shipping Orders**

* * *

## **Add, Install, and Activate PH MultiCarrier Shipping Label App**

Install the [**PH MultiCarrier Shipping Label**](https://apps.shopify.com/multi-carrier-shipping-label) app. Go to your **Shopify Store → Apps → PH Multi Carrier Shipping Label** app as shown below: 

**Reference** : [How to install and activate the PH Multi Carrier Shipping Label app](https://www.pluginhive.com/knowledge-base/setting-up-shopify-multi-carrier-shipping-label-app/#install-and-activate)

* * *

## Add your Amazon Shipping Account 

Go to the **App** **Settings** → **Carrier (+) icon** as shown below:

* * *

Select the carrier **“Amazon Shipping”** & Click on **“Add Account”** as shown below.

* * *

In the Account Details, select the **“Country of Origin”** from the drop-down menu and click on the **Connect** button to connect your Amazon Shipping account with the PH MultiCarrier Shipping Label app.

* * *

You will be redirected to the Amazon Shipping Sign-in page. Enter your Amazon Shipping registered email ID or phone number below and click on **‘Continue’.**

* * *

Enter the password and click on **‘Sign in’.**

* * *

**_Note_**  
  

If you don’t have Amazon Seller Central login credentials, then you need to register for Shipper Central:

  * For India: [**Register here**](https://shipping.amazon.in/?ref_tag=SWA_IN_Referral_plugnhive_24)
  * For the US: [**Register here**](https://shipping.amazon.com/)
  * For the UK: [**Register here**](https://shipping.amazon.co.uk/)
  * For France: [**Register here**](https://shipping.amazon.fr/)
  * For Italy: [**Register here**](https://shipping.amazon.it/)
  * For Spain: [**Register here**](https://shipping.amazon.es/)

* * *

Click the checkbox to allow PluginHive Multi Carrier Shipping Label to access your Amazon Shipping account, then click ‘**Authorize** ‘

* * *

Upon successful registration, you will see the **Registration successful** message displayed below.

* * *

Once the registration is successful, the carrier account number automatically gets added to the carrier account details.

* * *

**Now you can access Amazon Shipping services using the app.** The app allows you to display Amazon Shipping rates, generate and print shipping labels in bulk, and track Amazon Shipping in real time.

* * *

## Verify the Shipper or Warehouse Address

Once you add the Amazon Shipping account, verify the shipper address details. The app will automatically configure your store location, which was added to Shopify as the shipping origin. Ensure your warehouse address matches the one you set up in your Amazon Shipping Shipper Central account.

* * *

**_Note_**  
  

The address must be within the respective country to where you’re shipping. Amazon Shipping currently doesn’t support cross-border shipments

* * *

Click on the **(≡)** icon and visit **Settings > Address** and your store name will be listed there.

* * *

Click on the store name and you can see the shipper address and other details as shown below.

* * *

Review the shipper details. If changes are needed, make them and click “**Save.** “

* * *

**_Note_**  
  

Please ensure the address entered is accurate, as it will be used to calculate shipping rates at the checkout page. Additionally, make sure to include the “Company Name” field, as Amazon Shipping uses this information to display your company name on the tracking portal and in any email communication related to your shipments.

* * *

## Configure Weight & Dimensions for Your Products and Choose the Right Packaging Method

To calculate the accurate shipping rate for an order, you must configure the weight of the product correctly.

**Reference** : [How to Configure the weight & dimensions for products and choose the right packaging method](https://www.pluginhive.com/knowledge-base/setting-up-shopify-multi-carrier-shipping-label-app/#configure-weight-dimension)

* * *

## Opt for the Preferred Amazon Shipping Services to be Displayed at the Shopify Checkout

The app automatically displays all the available Amazon Shipping rates on the Shopify checkout page. However, if you want to display shipping rates for a particular Amazon Shipping service on your Shopify checkout, you can do so without any hassle.

Click on the **(≡)** icon and visit **Settings > Shipping Rates > Rate Automation**, as shown below.

* * *

The app automatically creates rules for the shipping carriers that you add to help you choose the services that will be displayed on the Shopify store. Click on **Edit** to customize the shipping automation rules based on your preferences.

* * *

By default, the **“Any”** condition is selected in the automation criteria, which applies to all cases. Under the Action Details tab, the respective carrier, along with **“All”** services, will be selected by default.

* * *

However, if you want to select your preferred Amazon Shipping service(s) that you want to display to your customers, then you may do as shown below:

* * *

However, you can always choose to calculate and display shipping rates for the above-selected shipping service(s) based on various conditions, such as,

  * Shopify Shipping Zones
  * The product quantity that the customer chooses
  * Total weight of all the products
  * Cart sub-total amount
  * Shipping Classes
  * Time of order placement
  * Total weight range
  * Total price range

Based on your preference, you can select any conditions and the app will calculate the shipping rates only if the conditions are matched.

* * *

Click on the “**Update Rule** ” once the required changes are made, as shown below.

* * *

## Display Amazon Shipping rates on the Shopify checkout

Visit the store and add a product to the cart. Enter a shipping address and calculate the shipping cost. The app will display the shipping cost for all the available Amazon Shipping services or the shipping services that you have selected based on your preference at Shopify checkout.

* * *

**_Note_**  
  

  * Shipping rates are calculated based on product weight, dimensions, shipping origin and destination, packaging type, and selected special services (if any).
  * Here’s a summary of the Amazon Shipping services available in different countries:

Country | Service ID | Service Name | Carrier ID | Carrier Name  
---|---|---|---|---  
United States | std-us-swa-mfn | Amazon Shipping Ground | AMZN_US | Amazon Shipping  
United Kingdom | SWA-UK-PREM | Amazon Shipping One Day | AMZN_UK | Amazon Shipping  
United Kingdom | SWA-UK-2D | Amazon Shipping Two Day | AMZN_UK | Amazon Shipping  
Spain | SWA-ES-PRIME-PREM | Amazon Shipping Express | AMZN_ES | Amazon Shipping  
Italy | SWA-IT-PRIME-PREM | Spedizione nazionale express | AMZN_IT | Amazon Shipping  
France | SWA-FR-PRIME-PREM | Amazon Shipping One Day | AMZN_FR | Amazon Shipping  
India | SWA-IN-OA | Amazon Shipping Standard | ATS | Amazon Shipping  
  
* * *

## Verify the Shipping Cost Displayed on the Shopify Checkout Page

If you encounter any issues, review the logs for more information. If a deeper investigation is needed, you can share the logs with Amazon Shipping support. You can check the logs by going to**Settings > Shipping Rates > Request Log.**

* * *

Click on the **(i) icon** in front of the most recent Shipping Rate Request, as shown below.

* * *

After viewing the request log, you can verify the**Items,** **Package Details** & **Shipping Methods** under this section:

* * *

## Print the Amazon Shipping Labels for your Shopify Orders

Visit the **Orders** tab and select the order(s) for which you want to generate and print a shipping label, and click on **Generate Labels** , as shown below.

* * *

Select the order(s) again and click on **Print Labels to** get the shipping labels for your orders, as shown below.

* * *

The app will automatically redirect you to another page to print the shipping labels along with other documents like the tax invoice as shown below.

* * *

**_Note_**  
  

Pickup window should be pre-scheduled before attempting to generating a shipping label. In case of any issues in setting up the pickup window in Amazon Shipping Shipper Central, please contact Amazon Shipping support using your Shipper Central help pages.

* * *

## Mark Orders as Fulfilled and Automatically Send Amazon Shipping Tracking Details to your Customers via Email

After generating and printing the label(s), you can visit the **Orders** tab & select all the orders that are ready to be shipped, and click on **Mark As Fulfilled** to fulfill these orders.

* * *

Once you mark the orders as fulfilled in the App, your Shopify orders will be automatically marked as fulfilled. You can visit the Shopify > Orders page to check the order status and click on the order. In the image below, you can see that the order is automatically marked as fulfilled. Also, the shipment tracking details are automatically updated to the Shopify orders.

* * *

For the customers: The PH MultiCarrier Shipping Label app automatically sends the tracking details to the customer via the Shopify Order Shipped Email, as shown in the image below.

* * *

## Track your Amazon Shipping Orders 

To track your orders, select the orders that are shipped and click on **Track Your Orders**. Or, you can track all the orders by visiting the **Tracking** tab, where the app will display the live tracking status of all the shipments, as shown below.

* * *

If you face any issues or have any queries on setting up the app, feel free to [**contact our support**](https://www.pluginhive.com/support/).

[ Previous  How to Create a USPS Account and Integrate With Shopify  ](https://www.pluginhive.com/knowledge-base/create-usps-account-for-shopify/)

[ Next  Shopify Order Fulfilment Made Easy with Touchless Label Printing  ](https://www.pluginhive.com/knowledge-base/shopify-order-fulfilment-with-touchless-label-printing/?seq_no=2)
