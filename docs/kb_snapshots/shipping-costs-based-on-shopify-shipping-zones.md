# Calculate shipping costs based on Shopify shipping zones

**Source:** https://www.pluginhive.com/knowledge-base/shipping-costs-based-on-shopify-shipping-zones/
**App:** Shopify Multi Carrier Shipping Label App (MCSL)
**Note:** Some screenshots may show older app UI — all text content is current.

---

# Calculate shipping costs based on Shopify shipping zones

This guide explains how to use the [**Shopify Multi Carrier Shipping Label app**](https://apps.shopify.com/multi-carrier-shipping-label) to calculate shipping costs based on the shipping zones.

* * *

## On this page

  * **Setting up shipping zones in the Shopify Multi Carrier Shipping Label app**
  * **Setting up shipping zones based on Country**
  * **Setting up shipping zones based on State**
  * **Setting up shipping zones based on Postal Codes**
  * **Configure different carriers based on shipping zones**
  * **Configure Flat rate/Free shipping based on shipping zones**
  * **Adjust Shipment price based on shipping zones**
  * **Choose different warehouse locations based on shipping zones**

* * *

## Setting up Shipping Zones in Shopify Multi Carrier Shipping Label app

The Shopify Multi Carrier Shipping Label app helps you calculate and display rates based on shipping zones. You can create **[Shopify shipping](https://www.pluginhive.com/how-does-shopify-shipping-work/) **zones and calculate rates based on the criteria that include **Country** , **State** , and **Postal codes**. See the example below. You can create a zone for Country-state, United states-California, and add the rates for this zone.

To add shipping zones, head to **App settings – > Shipping –> Shipping zones**.

### Setting up shipping zones based on Country

The app allows you to add shipping zones based on a country and calculate shipping rates. Under the shipping zones section, add a zone by selecting the country as shown below.

Now, head to **App settings – > Shipping rates –> Rate automation**, where you can select the automation criteria as **“Zones”** and select the zone that you have added. 

* * *

### Setting up shipping zones based on State

You can set up shipping zones based on the Country-State if you would like to set it up for different states instead of the whole country. Under the shipping zones section, add a zone by choosing the required state as shown below.

Now, head to the Rates automation settings, where you can choose the automation criteria as **“Zones”**. Add the “State” zone that you have added, and the app calculates the shipping rates accordingly. 

* * *

### Setting up shipping zones based on Postal Codes

Similar to country and states, you can also set up shipping zones based on the postal codes. Under the shipping zones section, add a zone by providing the required postal codes as shown below.

> **Note** : You can add the zones based on the postal codes where each postal should be comma-separated.

Now, head to the Rates automation section from where you can choose the automation criteria as **“Zones”**. Add the zone that you have created, and the app calculates the shipping rates accordingly.

Adding the shipping zones based on postal code can be useful in situations where the carrier does not ship to a particular postcode (as in the case of the COVID pandemic when shipping was limited to very few areas).

* * *

## Configure different carriers based on shipping zones

After you set up the shipping zones, the app allows you to configure different carriers or carrier services based on zones. To do that, head to **App settings – > Shipping rates –> Rate automation** \--> **Action Details** , and choose US zone for example. 

Now, select “**Add Carrier Service** ” from the dropdown list. You can then select the carrier and the services based on your requirement.

* * *

## Configure Flat rate/Free shipping based on shipping zones

Adding a flat rate for one of the zones or providing free shipping for another zone is a common requirement for the merchants. This is easily possible with the app. For example, consider a situation where you would like to provide a flat rate for the California state and would like to provide free shipping for some of the areas in Miami. 

To do this, head to **App settings – > Shipping rates –> Rate automation** \--> **Action Details**. Choose California Zone and under action details, select “Add Flat Rate”. Now, add the required amount as the flat rate as shown below.

Now, to add free shipping to the Miami zone, choose Miami Zone and under action details, select “Add Flat Rate”. Now, add “0” as the flat rate amount as shown below. This will enable free shipping to the Miami zone.

> **Note** :   
> You can either add a flat rate or free shipping or both. If required, you can add flat rate to one zone and free shipping to another. You can add flat rate to one of the zones as shown above. 
> 
> Now, you have to add another automation rule, configure the other zone, and configure flat rate as “0” inorder to provide free shipping to the next zone. To add a rule, head to **App settings** \--> **Shipping rates – > Rate automation** \--> **Add Rule**. 

* * *

## Adjust Shipment price based on shipping zones

There are cases when you would have to add a handling charge over the shipping cost based on the zone. This might be due to the additional packaging requirement or the shipping location that is difficult to deliver. To add this, choose “Adjust shipment price” from the dropdown list and add the required percentage value as shown below.

> **Note** : You can also “Subtract” the shipment price if you would like to provide discounts to a specific zone.

* * *

## Choose different warehouse locations based on shipping zones

Consider an example where a merchant has a warehouse location in Los Angeles and Miami. When a customer orders from the Los Angeles area, the app helps the merchant to set the shipper location to the Los Angeles warehouse so that, the delivery becomes seamless. Let’s see how this is done with the app.

As explained in the previous section, head to **App settings – > Shipping –> Shipping zones**. Add a shipping zone for the Los Angeles area with the required zip codes as shown below.

Now, head to **App settings – > Shipping rates –> Rate automation**, from where you can choose the automation criteria as **“Zones”**. Select Los Angeles Zone from the list. Now, under “Action details”, select “**Shipper from address** ” and choose Los Angeles from the list. 

Once this is saved, whenever a customer orders from the zip codes mentioned under the Los Angeles zone, the product will be shipped from the Los Angeles warehouse.

Similarly, add a shipping zone for the Miami area with the required zip codes as shown below.

Head to **App settings – > Shipping rates –> Rate automation**, from where you can choose the automation criteria as **“Zones”**. Select Miami Zone from the list. Now, under “Action details”, select “**Shipper from address** ” and choose Miami from the list. 

Once this is done, whenever a customer orders from the zip codes mentioned under the Miami zone, the product will be shipped from the Miami warehouse.

> **Note:**   
> – If different products are shipped from different warehouse locations, the app doesn’t support the zones based rates calculation  
> – If the product variants are shipped from different warehouse locations, the app doesn’t support the zones based rates calculation

* * *

## Conclusion

In this guide, we discussed how to calculate shipping costs based on Shopify shipping zones using the [**Multi Carrier Shipping Label app**](https://apps.shopify.com/multi-carrier-shipping-label). We also discussed the various parameters that can be configured based on the shipping zones. 

Apart from those parameters, you can also configure different criterias based on shipping zones that include adjusting shipping price based on order cost, adding Insurance, add delivery confirmation, enable Saturday delivery, add DHL special services, and add Canada Post special services.

If you face any issues or have any queries on setting up the app to calculate the rates based on shipping zones, do [**contact PluginHive support**](https://www.pluginhive.com/support/).

[ Previous  Packing Methods in the Shopify Multi-Carrier Shipping Label App  ](https://www.pluginhive.com/knowledge-base/packing-methods-shopify-multi-carrier-shipping-label-app/)

[ Next  Accurate Customs Amount on Commercial Invoice for Easy Customs Clearance  ](https://www.pluginhive.com/knowledge-base/customs-amount-on-commercial-invoice/)
