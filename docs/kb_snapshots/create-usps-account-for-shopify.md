# How to Create a USPS Account and Integrate With Shopify

**Source:** https://www.pluginhive.com/knowledge-base/create-usps-account-for-shopify/
**App:** Shopify Multi Carrier Shipping Label App (MCSL)
**Note:** Some screenshots may show older app UI — all text content is current.

---

# How to Create a USPS Account and Integrate With Shopify 

If you’re running a Shopify store and want to use USPS for shipping, you’ll need to create a USPS business account and gather key credentials like your CRID and MID. In this guide, we’ll walk you through the steps to create a USPS account and integrate it with your Shopify store using the correct credentials, ensuring smooth label generation and accurate rate calculation.

* * *

## Create a USPS Account 

Follow the steps below to create a USPS Account and obtain the required account details for integration with the [PH Multi-Carrier Shipping Label App](https://apps.shopify.com/multi-carrier-shipping-label).

1\. Go to the [USPS Developer Portal](https://developers.usps.com/) and click on the **Getting Started** tab.

* * *

* * *

2\. Go to the **USPS Customer Onboarding Portal (COP)** as shown in the image.

* * *

3\. Click **Create New Account** to start the registration process. (If you already have an account, simply sign in to retrieve your credentials.)

* * *

4\. Enter your email address and submit. USPS will send a verification link; click it to verify your email.

* * *

5\. In the registration steps:

**Step 1** : Enter your company information, including address/ ZIP code/ company identifier. In this example, we have entered the address. Then, click **Search Address**.

* * *

* * *

When your address appears, click **Confirm Address**.

* * *

**Step 2** : Add your contact details to verify your account.

* * *

**Step 3** : Set your username, password, and security questions answers, and create an account.

* * *

6\. Read through and accept to Terms and Conditions by checking the box, then click **Continue**.

* * *

Once your account is created, you’ll be redirected to a page displaying your, 

  * **Customer Registration ID (CRID):** A USPS-generated identifier for your business location. It connects your shipping activity to your USPS profile.
  * **Mailer Identifier (MID):** A numeric code (6 or 9 digits) assigned by USPS to identify your business for outbound mail tracking.
  * **Return MID:** A specific MID used to manage return shipments, ensuring returns are properly tracked in USPS systems.

(Existing account holders can visit[ this site](https://cop.usps.com/cop-navigator?wf=API&showCC=false) to access these credentials.)

* * *

* * *

## Add Payment Details for Your USPS Account

On the same page, you’ll see an option to add a payment method. Agree to the terms and conditions, select your payment account type, and click **Continue**.

* * *

* * *

Enter your **bank account details** and **submit**.

* * *

You will then see your **EPS Payment Account Number**.

* * *

## Create an App for API Access

  1. Log in to the [USPS Developer Portal](https://developers.usps.com/) again. Go to the **Apps** section from the top menu.

* * *

2\. Click on Add App to add a Shopify app, such as the [PH Multi-Carrier Shipping Label App](https://apps.shopify.com/multi-carrier-shipping-label). 

* * *

3\. Fill in the app details and click on **Add App**. 

(We recommend using **PH Multi-Carrier** **Shipping Label** as the app name for the [PH Multi-Carrier Shipping Label App](https://apps.shopify.com/multi-carrier-shipping-label))

* * *

4\. Once the app is created, click on the app to get the **Consumer Key** **_(client_id)_** and **Consumer Secret** **_(client_secret)_** under the **View** tab, as shown in the image.

* * *

* * *

* * *

These credentials will be required in the next step to generate an OAuth token and access protected USPS account information.

## Authorize App to Access Protected Information Resources

In the [USPS Customer Onboarding Portal](https://cop.usps.com/navigator?wf=apisonboarding&callback=https://developers.usps.com), enter your **Consumer Key** and submit to authorize your app.

* * *

* * *

This step enables access to your **payment accounts, permits, CRIDs,** and**MIDs** required for successful integration. 

Now, to get the Manifest MID, go to **My Account** and click on **Manage Locations**.

* * *

Here, you will be able to get your **Manifest/ Master MID** as shown in the image. 

* * *

**Important Note:**   
After completing all setup steps, you must contact USPS Web Tools support to request production access approval for your application. Without this final approval, label generation will not work — even if all credentials are correct. Once approved, you can connect your USPS account to the app without issues. 

* * *

## Integrate Your USPS Account in Shopify 

Now that you have all the required details – CRID, Consumer Key, Consumer Secret, Account Number, MID, Manifest MID, and Return MID- you can seamlessly integrate your USPS account in Shopify with the [PH Multi-Carrier Shipping Label App](https://apps.shopify.com/multi-carrier-shipping-label).

Make sure the [PH Multi-Carrier Shipping Label App](https://apps.shopify.com/multi-carrier-shipping-label) has been installed. 

Add the USPS carrier by selecting **USPS Ship.** Then, click the **Add Account** button. 

* * *

* * *

Now simply copy the credentials you obtained from the previous steps and paste them into their respective fields in the app, then click **Connect**. 

* * *

* * *

You’re now successfully connected! 

You can start accessing live rates, generating labels, tracking shipments, and fulfilling orders. Refer to this guide for step-by-step instructions:[ Setting Up Shopify Multi-Carrier Shipping Label App](https://www.pluginhive.com/knowledge-base/setting-up-shopify-multi-carrier-shipping-label-app/)

* * *

## Having Trouble?

If you face issues like authentication errors or connection failures, please double-check that all credentials are entered correctly and match the values shown in your USPS portals.

If the issue persists, contact [PluginHive support](https://www.pluginhive.com/support/). To expedite resolution or escalate the issue to USPS if required, be sure to include your USPS Account Number in your message.

[ Previous  Integrating USPS Via EasyPost on Shopify  ](https://www.pluginhive.com/knowledge-base/integrate-usps-easypost-on-shopify/)

[ Next  Shopify Amazon Shipping Guide  ](https://www.pluginhive.com/knowledge-base/amazon-shipping-guide-for-shopify/)
